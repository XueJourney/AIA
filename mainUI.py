import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from tkinter import font as tkFont
import threading
import queue
import json
import hashlib
import platform
import os
import subprocess
from pathlib import Path
from datetime import datetime
import logging
from openai import OpenAI
import requests
from pydub import AudioSegment
import simpleaudio as sa

# 创建一个 Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 设置Logger的最低等级为DEBUG，这样所有等级的日志都会被传递给Handler

# 创建文件Handler，保存为 UTF-8 编码，等级为 DEBUG
file_handler = logging.FileHandler("app_gui.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

# 创建控制台Handler，等级为 INFO
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 设置日志格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 给两个Handler都设置格式
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 添加Handler到Logger中
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class AIChat:
    def __init__(self, root):
        self.root = root
        self.root.title("AI 双模式对话系统")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 配置样式
        self.setup_styles()
        
        # 初始化变量
        self.client_sf = None
        self.client_ba = None
        self.system_prompt = ""
        self.history_sf = []
        self.history_ba = []
        self.voice_list = []
        self.selected_voice = None
        self.user_preferences = {}
        self.voice_enabled = tk.BooleanVar()
        self.message_queue = queue.Queue()
        
        # 缓存设置
        self.CACHE_DIR = Path(__file__).parent
        self.CACHE_FILE = self.CACHE_DIR / "user_cache.json"
        
        # 设置日志
        self.setup_logging()
        
        # 创建界面
        self.create_widgets()
        
        # 启动初始化
        self.initialize_app()
        
        # 处理消息队列
        self.process_queue()
    
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置颜色
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Status.TLabel', font=('Arial', 9))
        style.configure('Chat.TFrame', relief='solid', borderwidth=1)
    
    def setup_logging(self):
        """设置日志"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        if not self.logger.handlers:
            file_handler = logging.FileHandler("app_gui.log", encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置行列权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="AI 双模式对话系统", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # 左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="10")
        control_frame.grid(row=1, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # API设置按钮
        ttk.Button(control_frame, text="配置API密钥", command=self.setup_api_keys).pack(fill=tk.X, pady=2)
        
        # 用户偏好按钮
        ttk.Button(control_frame, text="设置用户偏好", command=self.setup_user_preferences).pack(fill=tk.X, pady=2)
        
        # 语音设置
        voice_frame = ttk.LabelFrame(control_frame, text="语音设置", padding="5")
        voice_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Checkbutton(voice_frame, text="启用语音回复", variable=self.voice_enabled).pack(anchor=tk.W)
        ttk.Button(voice_frame, text="选择音色", command=self.select_voice).pack(fill=tk.X, pady=2)
        
        self.voice_status_label = ttk.Label(voice_frame, text="未选择音色", style='Status.TLabel')
        self.voice_status_label.pack(anchor=tk.W)
        
        # 对话模式
        mode_frame = ttk.LabelFrame(control_frame, text="对话模式", padding="5")
        mode_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(mode_frame, text="特殊前缀:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        ttk.Label(mode_frame, text="！- 直接人性化回复", style='Status.TLabel').pack(anchor=tk.W)
        ttk.Label(mode_frame, text="#- 仅逻辑分析", style='Status.TLabel').pack(anchor=tk.W)
        
        # 清空对话按钮
        ttk.Button(control_frame, text="清空对话历史", command=self.clear_chat).pack(fill=tk.X, pady=(10, 0))
        
        # 状态标签
        self.status_label = ttk.Label(main_frame, text="正在初始化...", style='Status.TLabel')
        self.status_label.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 聊天区域
        chat_frame = ttk.Frame(main_frame, style='Chat.TFrame')
        chat_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # 聊天显示区
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, 
            wrap=tk.WORD, 
            state=tk.DISABLED,
            font=('Arial', 10),
            height=20
        )
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # 配置聊天显示区的标签
        self.chat_display.tag_configure("user", foreground="blue", font=('Arial', 10, 'bold'))
        self.chat_display.tag_configure("ai", foreground="green")
        self.chat_display.tag_configure("system", foreground="gray", font=('Arial', 9, 'italic'))
        self.chat_display.tag_configure("analysis", foreground="purple")
        
        # 输入区域
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        input_frame.columnconfigure(0, weight=1)
        
        self.input_text = tk.Text(input_frame, height=3, font=('Arial', 10))
        self.input_text.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.input_text.bind('<Return>', self.on_enter)
        self.input_text.bind('<Control-Return>', self.insert_newline)
        
        send_button = ttk.Button(input_frame, text="发送", command=self.send_message)
        send_button.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def insert_newline(self, event):
        """插入换行符"""
        self.input_text.insert(tk.INSERT, '\n')
        return "break"
    
    def on_enter(self, event):
        """回车键处理"""
        if event.state & 0x4:  # Ctrl+Enter
            return
        self.send_message()
        return "break"
    
    def get_cache_key(self):
        """生成缓存键"""
        machine_info = platform.uname()
        user_info = os.getlogin()
        key_str = f"{machine_info.system}_{machine_info.node}_{user_info}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def load_cached_data(self):
        """加载缓存数据"""
        try:
            if self.CACHE_FILE.exists():
                with open(self.CACHE_FILE, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    cache_key = self.get_cache_key()
                    if cache_key in cache:
                        return cache[cache_key]
            return None
        except Exception as e:
            self.logger.error(f"加载缓存失败: {e}")
            return None
    
    def save_to_cache(self, data):
        """保存数据到缓存"""
        try:
            cache = {}
            if self.CACHE_FILE.exists():
                with open(self.CACHE_FILE, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
            
            cache_key = self.get_cache_key()
            cache[cache_key] = data
            
            with open(self.CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            self.logger.error(f"保存到缓存失败: {e}")
    
    def initialize_app(self):
        """初始化应用"""
        def init_thread():
            # 加载缓存数据
            cached_data = self.load_cached_data()
            
            # 如果有缓存的API密钥，自动初始化客户端
            if cached_data and 'api_keys' in cached_data:
                try:
                    self.client_sf = OpenAI(
                        api_key=cached_data['api_keys']['sf'],
                        base_url="https://api.siliconflow.cn/v1"
                    )
                    self.client_ba = OpenAI(
                        api_key=cached_data['api_keys']['ba'],
                        base_url="https://api2.aigcbest.top/v1"
                    )
                    self.message_queue.put(("status", "API客户端已就绪"))
                except Exception as e:
                    self.message_queue.put(("status", f"API初始化失败: {str(e)}"))
            
            # 加载用户偏好
            if cached_data and 'preferences' in cached_data:
                self.user_preferences = cached_data['preferences']
                self.system_prompt = self.create_system_prompt(self.user_preferences)
                self.message_queue.put(("status", "用户偏好已加载"))
            
            # 加载语音设置
            if cached_data and 'selected_voice' in cached_data:
                self.selected_voice = cached_data['selected_voice']
                voice_name = self.selected_voice.get('customName', 'Unknown')
                self.message_queue.put(("voice_status", f"音色: {voice_name}"))
            
            if not cached_data or 'api_keys' not in cached_data:
                self.message_queue.put(("status", "请先配置API密钥"))
            elif not self.user_preferences:
                self.message_queue.put(("status", "请设置用户偏好"))
            else:
                self.message_queue.put(("status", "系统就绪，可以开始对话"))
        
        threading.Thread(target=init_thread, daemon=True).start()
    
    def process_queue(self):
        """处理消息队列"""
        try:
            while True:
                msg_type, content = self.message_queue.get_nowait()
                
                if msg_type == "status":
                    self.status_label.config(text=content)
                elif msg_type == "voice_status":
                    self.voice_status_label.config(text=content)
                elif msg_type == "chat":
                    self.append_to_chat(*content)
                elif msg_type == "error":
                    messagebox.showerror("错误", content)
        except queue.Empty:
            pass
        
        self.root.after(100, self.process_queue)
    
    def setup_api_keys(self):
        """设置API密钥"""
        dialog = APIKeyDialog(self.root)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            sf_key, ba_key = dialog.result
            try:
                self.client_sf = OpenAI(
                    api_key=sf_key,
                    base_url="https://api.siliconflow.cn/v1"
                )
                self.client_ba = OpenAI(
                    api_key=ba_key,
                    base_url="https://api2.aigcbest.top/v1"
                )
                
                # 保存到缓存
                cached_data = self.load_cached_data() or {}
                cached_data['api_keys'] = {'sf': sf_key, 'ba': ba_key}
                self.save_to_cache(cached_data)
                
                self.status_label.config(text="API密钥配置成功")
                messagebox.showinfo("成功", "API密钥配置成功！")
            except Exception as e:
                messagebox.showerror("错误", f"API客户端初始化失败: {str(e)}")
    
    def setup_user_preferences(self):
        """设置用户偏好"""
        dialog = UserPreferencesDialog(self.root, self.user_preferences)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.user_preferences = dialog.result
            self.system_prompt = self.create_system_prompt(self.user_preferences)
            
            # 保存到缓存
            cached_data = self.load_cached_data() or {}
            cached_data['preferences'] = self.user_preferences
            self.save_to_cache(cached_data)
            
            self.status_label.config(text="用户偏好设置成功")
            messagebox.showinfo("成功", "用户偏好设置成功！")
    
    def create_system_prompt(self, preferences):
        """创建系统提示词"""
        preferred_title = preferences.get('preferred_title', 'None')
        title_str = f'请称呼用户为"{preferred_title}"' if preferred_title != 'None' else 'None'

        return (
            f"# 用户信息\n"
            f"- 职业：{preferences.get('profession', 'None')}\n"
            f"- 称呼偏好：{title_str}\n"
            f"- 回复风格：{preferences.get('reply_style', 'None')}\n"
            f"- 补充信息：{preferences.get('additional_info', 'None')}\n\n"
            f"# 指令\n"
            f"请根据以上用户信息，以合适的语言风格和称呼方式与用户进行对话。"
            f"保持专业性的同时，确保回复符合用户的期望和偏好。如果某项信息为None，表示用户未提供该信息。"
        )
    
    def select_voice(self):
        """选择语音音色"""
        if not self.client_sf:
            messagebox.showwarning("警告", "请先配置SF API密钥")
            return
        
        def load_voices():
            try:
                self.message_queue.put(("status", "正在获取音色列表..."))
                self.voice_list = self.get_voice_list()
                if self.voice_list:
                    self.show_voice_selection()
                else:
                    self.message_queue.put(("error", "无法获取音色列表"))
            except Exception as e:
                self.message_queue.put(("error", f"获取音色列表失败: {str(e)}"))
        
        threading.Thread(target=load_voices, daemon=True).start()
    
    def get_voice_list(self):
        """获取音色列表"""
        try:
            url = "https://api.siliconflow.cn/v1/audio/voice/list"
            headers = {"Authorization": f"Bearer {self.client_sf.api_key}"}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                voice_data = response.json()
                return voice_data.get('result', [])
            return []
        except Exception as e:
            self.logger.error(f"获取音色列表失败: {e}")
            return []
    
    def show_voice_selection(self):
        """显示音色选择对话框"""
        dialog = VoiceSelectionDialog(self.root, self.voice_list, self.selected_voice)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.selected_voice = dialog.result
            voice_name = self.selected_voice.get('customName', 'Unknown')
            self.voice_status_label.config(text=f"音色: {voice_name}")
            
            # 保存到缓存
            cached_data = self.load_cached_data() or {}
            cached_data['selected_voice'] = self.selected_voice
            self.save_to_cache(cached_data)
            
            messagebox.showinfo("成功", f"音色设置成功: {voice_name}")
    
    def clear_chat(self):
        """清空对话历史"""
        self.history_sf.clear()
        self.history_ba.clear()
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.status_label.config(text="对话历史已清空")
    
    def append_to_chat(self, text, tag=None):
        """添加文本到聊天区域"""
        self.chat_display.config(state=tk.NORMAL)
        if tag:
            self.chat_display.insert(tk.END, text, tag)
        else:
            self.chat_display.insert(tk.END, text)
        self.chat_display.insert(tk.END, "\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def send_message(self):
        """发送消息"""
        if not self.client_sf or not self.client_ba:
            messagebox.showwarning("警告", "请先配置API密钥")
            return
        
        if not self.system_prompt:
            messagebox.showwarning("警告", "请先设置用户偏好")
            return
        
        message = self.input_text.get(1.0, tk.END).strip()
        if not message:
            return
        
        # 清空输入框
        self.input_text.delete(1.0, tk.END)
        
        # 显示用户消息
        self.append_to_chat(f"用户: {message}", "user")
        
        # 在后台处理对话
        def process_message():
            try:
                self.message_queue.put(("status", "AI正在思考..."))
                
                # 处理对话逻辑
                result = self.handle_conversation(message)
                
                self.message_queue.put(("status", "系统就绪"))
                
            except Exception as e:
                self.logger.error(f"处理消息失败: {e}")
                self.message_queue.put(("error", f"处理消息失败: {str(e)}"))
        
        threading.Thread(target=process_message, daemon=True).start()
    
    def handle_conversation(self, user_input):
        """处理对话逻辑"""
        # 检查特殊前缀
        skip_sf = False
        skip_ba = False
        display_text = user_input
        
        if user_input.startswith('！'):
            skip_sf = True
            display_text = user_input[1:].strip()
        elif user_input.startswith('#'):
            skip_ba = True
            display_text = user_input[1:].strip()
        
        if not display_text:
            self.message_queue.put(("chat", ("请输入有效内容", "system")))
            return
        
        sf_analysis = None
        ba_reply = None
        
        # SF逻辑分析
        if not skip_sf:
            sf_prompt = (
                "你是一个逻辑分析助手。请对用户的问题进行深入的逻辑分析，包括：\n"
                "1. 问题的核心要点\n"
                "2. 可能的解决思路\n"
                "3. 需要考虑的关键因素\n"
                "4. 逻辑推理过程\n"
                "请提供结构化的分析结果，不需要人性化的表达，专注于逻辑和事实。"
            )
            
            sf_messages = [{"role": "system", "content": sf_prompt}] + self.history_sf + [{"role": "user", "content": display_text}]
            
            sf_response = self.client_sf.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1",
                messages=sf_messages,
                temperature=0.3
            )
            
            sf_analysis = sf_response.choices[0].message.content
            
            # 更新SF历史
            self.history_sf.append({"role": "user", "content": display_text})
            self.history_sf.append({"role": "assistant", "content": sf_analysis})
        
        # BA人性化回复
        if not skip_ba:
            if skip_sf:
                ba_input = display_text
            else:
                ba_input = (
                    f"基于以下逻辑分析结果，请给用户一个人性化、温暖的回复：\n\n"
                    f"【逻辑分析(deepseek分析)】\n{sf_analysis}\n\n"
                    f"【用户原问题】\n{display_text}\n\n"
                    f"请结合分析结果，用符合用户偏好的方式进行回复。"
                )
            
            ba_messages = [{"role": "system", "content": self.system_prompt}] + self.history_ba + [{"role": "user", "content": ba_input}]
            
            ba_response = self.client_ba.chat.completions.create(
                model="gpt-4o",
                messages=ba_messages,
                temperature=0.7
            )
            
            ba_reply = ba_response.choices[0].message.content
            
            # 更新BA历史
            self.history_ba.append({"role": "user", "content": display_text})
            self.history_ba.append({"role": "assistant", "content": ba_reply})
        
        # 显示结果
        if skip_ba:
            self.message_queue.put(("chat", (f"📊 逻辑分析结果：\n{sf_analysis}", "analysis")))
        else:
            self.message_queue.put(("chat", (f"AI: {ba_reply}", "ai")))
            
            # 语音合成
            if self.voice_enabled.get() and self.selected_voice and ba_reply:
                self.generate_and_play_speech(ba_reply)
    
    def generate_and_play_speech(self, text):
        """生成并播放语音"""
        def generate_speech():
            try:
                speech_file_path = Path(__file__).parent / "ai_reply.mp3"
                
                with self.client_sf.audio.speech.with_streaming_response.create(
                    model="FunAudioLLM/CosyVoice2-0.5B",
                    voice=self.selected_voice['uri'],
                    input=text,
                    response_format="mp3"
                ) as response:
                    response.stream_to_file(speech_file_path)
                
                # 播放音频
                self.message_queue.put(("chat", ("🔊 语音播放中...", "system")))
                system = platform.system()
                if system == "Windows":
                    # 播放音频文件
                    sound = AudioSegment.from_mp3(str(speech_file_path))
                    play_obj = sa.play_buffer(
                        sound.raw_data,
                        num_channels=sound.channels,
                        bytes_per_sample=sound.sample_width,
                        sample_rate=sound.frame_rate
                    )
                    play_obj.wait_done()  # 等待播放结束
                elif system == "Darwin":
                    subprocess.run(["open", speech_file_path])
                else:
                    subprocess.run(["xdg-open", speech_file_path])
                
            except Exception as e:
                self.logger.error(f"语音生成失败: {e}")
                self.message_queue.put(("chat", ("⚠️ 语音生成失败", "system")))
        
        threading.Thread(target=generate_speech, daemon=True).start()


class APIKeyDialog:
    def __init__(self, parent):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("配置API密钥")
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="SF API密钥:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.sf_entry = ttk.Entry(frame, width=40, show="*")
        self.sf_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(frame, text="BA API密钥:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.ba_entry = ttk.Entry(frame, width=40, show="*")
        self.ba_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="确定", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        self.sf_entry.focus()
    
    def ok_clicked(self):
        sf_key = self.sf_entry.get().strip()
        ba_key = self.ba_entry.get().strip()
        
        if not sf_key or not ba_key:
            messagebox.showwarning("警告", "请输入完整的API密钥")
            return
        
        self.result = (sf_key, ba_key)
        self.dialog.destroy()
    
    def cancel_clicked(self):
        self.dialog.destroy()


class UserPreferencesDialog:
    def __init__(self, parent, current_prefs=None):
        self.result = None
        current_prefs = current_prefs or {}
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("用户偏好设置")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="职业:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.profession_entry = ttk.Entry(frame, width=40)
        self.profession_entry.grid(row=0, column=1, pady=5, padx=(10, 0), sticky=tk.W)
        self.profession_entry.insert(0, current_prefs.get('profession', ''))
        
        ttk.Label(frame, text="称呼偏好:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.title_entry = ttk.Entry(frame, width=40)
        self.title_entry.grid(row=1, column=1, pady=5, padx=(10, 0), sticky=tk.W)
        self.title_entry.insert(0, current_prefs.get('preferred_title', ''))
        
        ttk.Label(frame, text="回复风格:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.style_text = tk.Text(frame, width=40, height=3)
        self.style_text.grid(row=2, column=1, pady=5, padx=(10, 0), sticky=tk.W)
        self.style_text.insert(1.0, current_prefs.get('reply_style', ''))
        
        ttk.Label(frame, text="补充信息:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.info_text = tk.Text(frame, width=40, height=3)
        self.info_text.grid(row=3, column=1, pady=5, padx=(10, 0), sticky=tk.W)
        self.info_text.insert(1.0, current_prefs.get('additional_info', ''))
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="确定", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        self.profession_entry.focus()
    
    def ok_clicked(self):
        self.result = {
            'profession': self.profession_entry.get().strip() or "None",
            'preferred_title': self.title_entry.get().strip() or "None",
            'reply_style': self.style_text.get(1.0, tk.END).strip() or "None",
            'additional_info': self.info_text.get(1.0, tk.END).strip() or "None",
            'last_updated': datetime.now().isoformat()
        }
        self.dialog.destroy()
    
    def cancel_clicked(self):
        self.dialog.destroy()


class VoiceSelectionDialog:
    def __init__(self, parent, voice_list, current_voice=None):
        self.result = None
        self.voice_list = voice_list
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("选择语音音色")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        frame = ttk.Frame(self.dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="请选择语音音色:", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        # 创建列表框和滚动条
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.voice_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=('Arial', 10))
        self.voice_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.voice_listbox.yview)
        
        # 填充音色列表
        current_index = -1
        for i, voice in enumerate(voice_list):
            name = voice.get('customName', 'Unknown')
            desc = voice.get('text', 'No description')[:50]
            display_text = f"{name} - {desc}..."
            self.voice_listbox.insert(tk.END, display_text)
            
            if current_voice and voice.get('uri') == current_voice.get('uri'):
                current_index = i
        
        if current_index >= 0:
            self.voice_listbox.selection_set(current_index)
            self.voice_listbox.see(current_index)
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="确定", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="跳过", command=self.skip_clicked).pack(side=tk.LEFT, padx=5)
    
    def ok_clicked(self):
        selection = self.voice_listbox.curselection()
        if selection:
            index = selection[0]
            self.result = self.voice_list[index]
        self.dialog.destroy()
    
    def cancel_clicked(self):
        self.dialog.destroy()
    
    def skip_clicked(self):
        self.result = None
        self.dialog.destroy()


def main():
    root = tk.Tk()
    app = AIChat(root)
    
    # 设置程序图标（如果有的话）
    try:
        # root.iconbitmap('icon.ico')  # 如果有图标文件
        pass
    except:
        pass
    
    # 处理窗口关闭事件
    def on_closing():
        if messagebox.askokcancel("退出", "确定要退出程序吗？"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    main()