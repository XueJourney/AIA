from openai import OpenAI
import logging
import requests
from pathlib import Path
import os
import platform
import subprocess
import json
import hashlib
from datetime import datetime

# 创建一个 Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 设置Logger的最低等级为DEBUG，这样所有等级的日志都会被传递给Handler

# 创建文件Handler，保存为 UTF-8 编码，等级为 DEBUG
file_handler = logging.FileHandler("app.log", encoding="utf-8")
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

# 缓存文件路径
CACHE_FILE = Path(__file__).parent / "user_cache.json"

def get_cache_key():
    """生成缓存键，基于机器和用户信息"""
    machine_info = platform.uname()
    user_info = os.getlogin()
    key_str = f"{machine_info.system}_{machine_info.node}_{user_info}"
    return hashlib.md5(key_str.encode()).hexdigest()

def load_cached_data():
    """加载缓存数据"""
    try:
        if CACHE_FILE.exists():
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                cache_key = get_cache_key()
                if cache_key in cache:
                    logger.info("从缓存加载用户数据")
                    return cache[cache_key]
        return None
    except Exception as e:
        logger.error(f"加载缓存失败: {e}")
        return None

def save_to_cache(data):
    """保存数据到缓存"""
    try:
        cache = {}
        if CACHE_FILE.exists():
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
        
        cache_key = get_cache_key()
        cache[cache_key] = data
        
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2)
        
        logger.info("用户数据已保存到缓存")
    except Exception as e:
        logger.error(f"保存到缓存失败: {e}")

def get_api_clients():
    """获取API客户端配置"""
    logger.info("初始化API客户端")
    
    # 尝试从缓存加载
    cached_data = load_cached_data()
    if cached_data and 'api_keys' in cached_data:
        use_cache = input("检测到已保存的API密钥，是否使用？(y/n): ").strip().lower()
        if use_cache == 'y':
            logger.info("使用缓存的API密钥")
            apikey_sf = cached_data['api_keys']['sf']
            apikey_ba = cached_data['api_keys']['ba']
        else:
            apikey_sf = input("请输入您的SF_API密钥：")
            apikey_ba = input("请输入您的BA_API密钥：")
    else:
        apikey_sf = input("请输入您的SF_API密钥：")
        apikey_ba = input("请输入您的BA_API密钥：")
    
    # 保存到缓存
    if cached_data:
        cached_data['api_keys'] = {'sf': apikey_sf, 'ba': apikey_ba}
    else:
        cached_data = {'api_keys': {'sf': apikey_sf, 'ba': apikey_ba}}
    save_to_cache(cached_data)
    
    client_sf = OpenAI(
        api_key=apikey_sf,
        base_url="https://api.siliconflow.cn/v1"
    )
    
    client_ba = OpenAI(
        api_key=apikey_ba,
        base_url="https://api2.aigcbest.top/v1"
    )
    
    return client_sf, client_ba

def get_user_preferences():
    """获取用户偏好设置"""
    logger.info("获取用户偏好设置")
    
    # 尝试从缓存加载
    cached_data = load_cached_data()
    if cached_data and 'preferences' in cached_data:
        use_cache = input("检测到已保存的用户偏好，是否使用？(y/n): ").strip().lower()
        if use_cache == 'y':
            logger.info("使用缓存的用户偏好")
            return cached_data['preferences']
    
    preferences = {
        'profession': input("您的职业：").strip() or "None",
        'preferred_title': input("您喜欢的称呼：").strip() or "None",
        'reply_style': input("您希望AI如何回复：").strip() or "None",
        'additional_info': input("AI还需要知道的其他信息：").strip() or "None",
        'last_updated': datetime.now().isoformat()
    }
    
    # 保存到缓存
    if cached_data:
        cached_data['preferences'] = preferences
    else:
        cached_data = {'preferences': preferences}
    save_to_cache(cached_data)
    
    return preferences

def create_system_prompt(preferences):
    """创建系统提示词"""
    logger.info("创建系统提示词")
    
    preferred_title = preferences['preferred_title']
    if preferred_title != 'None':
        title_str = f'请称呼用户为"{preferred_title}"'
    else:
        title_str = 'None'

    system_prompt = (
        f"# 用户信息\n"
        f"- 职业：{preferences['profession']}\n"
        f"- 称呼偏好：{title_str}\n"
        f"- 回复风格：{preferences['reply_style']}\n"
        f"- 补充信息：{preferences['additional_info']}\n\n"
        f"# 指令\n"
        f"请根据以上用户信息，以合适的语言风格和称呼方式与用户进行对话。"
        f"保持专业性的同时，确保回复符合用户的期望和偏好。如果某项信息为None，表示用户未提供该信息。"
    )
    
    return system_prompt

def get_voice_list(api_key):
    """获取可用音色列表"""
    try:
        logger.info("请求音色列表API")
        url = "https://api.siliconflow.cn/v1/audio/voice/list"
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            voice_data = response.json()
            logger.info(f"获取到 {len(voice_data.get('result', []))} 个音色")
            return voice_data.get('result', [])
        else:
            logger.error(f"获取音色列表失败，状态码: {response.status_code}, 响应: {response.text}")
            return []
    except Exception as e:
        logger.error(f"获取音色列表出错: {str(e)}", exc_info=True)
        return []

def select_voice(voice_list):
    """让用户选择音色"""
    if not voice_list:
        logger.warning("音色列表为空")
        print("未找到可用音色")
        return None
    
    print("\n=== 可用音色列表 ===")
    for i, voice in enumerate(voice_list, 1):
        print(f"{i}. {voice.get('customName', 'Unknown')} - {voice.get('text', 'No description')[:50]}...")
    
    while True:
        try:
            choice = input(f"\n请选择音色 (1-{len(voice_list)})，或输入0跳过: ").strip()
            if choice == '0':
                logger.info("用户跳过音色选择")
                return None
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(voice_list):
                selected_voice = voice_list[choice_idx]
                logger.info(f"用户选择音色: {selected_voice.get('customName', 'Unknown')}")
                
                # 保存到缓存
                cached_data = load_cached_data() or {}
                cached_data['selected_voice'] = selected_voice
                save_to_cache(cached_data)
                
                print(f"已选择音色: {selected_voice.get('customName', 'Unknown')}")
                return selected_voice
            else:
                print("选择无效，请重新输入")
        except ValueError:
            print("请输入有效数字")

def generate_speech(client_sf, text, voice_uri, output_path):
    """生成语音文件"""
    try:
        logger.info(f"开始生成语音，文本长度: {len(text)} 字符")
        
        start_time = datetime.now()
        with client_sf.audio.speech.with_streaming_response.create(
            model="FunAudioLLM/CosyVoice2-0.5B",
            voice=voice_uri,
            input=text,
            response_format="mp3"
        ) as response:
            response.stream_to_file(output_path)
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"语音生成成功，耗时: {duration:.2f}秒，保存到: {output_path}")
        return True
    except Exception as e:
        logger.error(f"语音生成失败: {str(e)}", exc_info=True)
        return False

def play_audio(file_path):
    """播放音频文件"""
    try:
        logger.info(f"尝试播放音频: {file_path}")
        system = platform.system()
        if system == "Windows":
            os.startfile(file_path)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", file_path])
        else:  # Linux
            subprocess.run(["xdg-open", file_path])
        logger.info("音频播放成功")
        return True
    except Exception as e:
        logger.error(f"播放音频失败: {str(e)}", exc_info=True)
        return False

def show_menu():
    """显示主菜单"""
    print("\n" + "="*50)
    print("           AI 双模式对话系统")
    print("="*50)
    print("1. 开始对话 (仅文字)")
    print("2. 开始对话 (文字 + 语音)")
    print("3. 选择语音音色")
    print("4. 更新用户偏好")
    print("5. 退出程序")
    print("="*50)
    print("💡 对话技巧:")
    print("   ！开头 - 跳过逻辑分析，直接人性化回复")
    print("   #开头 - 仅逻辑分析，不进行人性化回复")
    print("="*50)

def get_menu_choice():
    """获取用户菜单选择"""
    while True:
        try:
            choice = input("请选择功能 (1-5): ").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return int(choice)
            else:
                print("请输入1-5之间的数字")
        except ValueError:
            print("请输入有效数字")

def handle_conversation(user_input, client_sf, client_ba, system_prompt, history_sf, history_ba, voice_enabled=False, selected_voice=None):
    """
    处理对话逻辑：
    - 普通输入：SF进行逻辑性分析 + BA进行人性化回复
    - ！开头：跳过SF，直接BA人性化回复
    - #开头：仅SF逻辑分析，不进行BA回复
    """
    
    # 检查特殊前缀
    skip_sf = False
    skip_ba = False
    display_text = user_input
    
    if user_input.startswith('！'):
        skip_sf = True
        display_text = user_input[1:].strip()
        logger.info("用户选择跳过SF逻辑分析")
        
    elif user_input.startswith('#'):
        skip_ba = True
        display_text = user_input[1:].strip()
        logger.info("用户选择跳过BA人性化回复")
    
    if not display_text:
        return "请输入有效内容（特殊前缀后需要有实际内容）", None
    
    try:
        sf_analysis = None
        ba_reply = None
        
        # Step 1: SF逻辑分析（除非被跳过）
        if not skip_sf:
            # SF固定提示词 - 专注于逻辑分析
            sf_prompt = (
                "你是一个逻辑分析助手。请对用户的问题进行深入的逻辑分析，包括：\n"
                "1. 问题的核心要点\n"
                "2. 可能的解决思路\n"
                "3. 需要考虑的关键因素\n"
                "4. 逻辑推理过程\n"
                "请提供结构化的分析结果，不需要人性化的表达，专注于逻辑和事实。"
            )
            
            logger.info("SF正在进行逻辑分析...")
            
            # 构建SF的对话历史
            sf_messages = [{"role": "system", "content": sf_prompt}] + history_sf + [{"role": "user", "content": display_text}]
            
            logger.debug(f"SF请求消息: {sf_messages}")
            start_time = datetime.now()
            
            sf_response = client_sf.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1",
                messages=sf_messages,
                temperature=0.3
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"SF分析完成，耗时: {duration:.2f}秒")
            
            sf_analysis = sf_response.choices[0].message.content
            logger.debug(f"SF分析结果: {sf_analysis[:200]}...")
            
            # 更新SF历史记录
            history_sf.append({"role": "user", "content": display_text})
            history_sf.append({"role": "assistant", "content": sf_analysis})
        
        # Step 2: BA人性化回复（除非被跳过）
        if not skip_ba:
            logger.info("BA正在生成人性化回复...")
            
            if skip_sf:
                # 直接回复用户问题
                ba_input = display_text
            else:
                # 基于SF分析进行回复
                ba_input = (
                    f"基于以下逻辑分析结果，请给用户一个人性化、温暖的回复：\n\n"
                    f"【逻辑分析(deepseek分析)】\n{sf_analysis}\n\n"
                    f"【用户原问题】\n{display_text}\n\n"
                    f"请结合分析结果，用符合用户偏好的方式进行回复。"
                )
            
            # 构建BA的对话历史
            ba_messages = [{"role": "system", "content": system_prompt}] + history_ba + [{"role": "user", "content": ba_input}]
            logger.debug(f"BA请求消息: {ba_messages}")
            
            start_time = datetime.now()
            ba_response = client_ba.chat.completions.create(
                model="gpt-4o",
                messages=ba_messages,
                temperature=0.7
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"BA回复生成完成，耗时: {duration:.2f}秒")
            
            ba_reply = ba_response.choices[0].message.content
            logger.debug(f"BA回复: {ba_reply[:200]}...")
            
            # 更新BA历史记录（存储原始用户输入和BA回复）
            history_ba.append({"role": "user", "content": display_text})
            history_ba.append({"role": "assistant", "content": ba_reply})
        
        # Step 3: 显示结果
        if skip_ba:
            # 仅显示SF分析结果
            print(f"📊 逻辑分析结果：\n{sf_analysis}")
            return sf_analysis, sf_analysis
        elif skip_sf:
            # 仅显示BA回复
            final_reply = ba_reply
        else:
            # 显示BA回复（SF分析不直接显示给用户）
            final_reply = ba_reply
        
        # Step 4: 可选生成语音（仅当有BA回复时）
        if not skip_ba and voice_enabled and selected_voice and ba_reply:
            speech_file_path = Path(__file__).parent / "ai_reply.mp3"
            if generate_speech(client_sf, ba_reply, selected_voice['uri'], speech_file_path):
                print(f"AI: {final_reply}")
                print("🔊 正在播放语音回复...")
                play_audio(speech_file_path)
            else:
                print(f"AI: {final_reply}")
                print("⚠️ 语音生成失败，仅显示文字回复")
        elif not skip_ba:
            print(f"AI: {final_reply}")
        
        return final_reply if not skip_ba else sf_analysis, sf_analysis
        
    except Exception as e:
        logger.error(f"对话处理出错: {str(e)}", exc_info=True)
        return "抱歉，处理您的请求时出现了错误，请稍后再试。", None

def conversation_loop(client_sf, client_ba, system_prompt, voice_enabled=False, selected_voice=None):
    """对话循环"""
    # 初始化独立的对话历史
    history_sf = []  # SF的对话历史
    history_ba = []  # BA的对话历史
    
    mode_text = "文字 + 语音模式" if voice_enabled else "纯文字模式"
    print(f"\n=== 对话开始 ({mode_text}) ===")
    if voice_enabled and selected_voice:
        print(f"当前音色: {selected_voice.get('customName', 'Unknown')}")
    print("💡 特殊命令:")
    print("   输入 'quit' 或 'exit' 返回主菜单")
    print("   ！开头 - 跳过逻辑分析，直接人性化回复")
    print("   #开头 - 仅逻辑分析，不进行人性化回复")
    print()
    
    while True:
        try:
            user_input = input("用户: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                logger.info("用户选择返回主菜单")
                break
            
            if not user_input:
                print("请输入有效内容")
                continue
            
            # 记录对话开始时间
            start_time = datetime.now()
            
            # 处理对话
            ba_reply, sf_analysis = handle_conversation(
                user_input, client_sf, client_ba, system_prompt, 
                history_sf, history_ba, voice_enabled, selected_voice
            )
            
            # 记录对话完成时间
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"完整对话处理耗时: {duration:.2f}秒")
            
            # 如果没有启用语音且不是特殊命令，显示分隔符
            if not voice_enabled and not user_input.startswith(('#', '！')):
                print()
            elif user_input.startswith('#'):
                print()  # SF分析结果后加换行
            
        except KeyboardInterrupt:
            logger.info("用户中断对话")
            break
        except Exception as e:
            logger.error(f"对话循环出错: {str(e)}", exc_info=True)
            print("发生错误，请重试。")

def main():
    """主函数"""
    logger.info("程序启动")
    
    try:
        # 初始化API客户端
        client_sf, client_ba = get_api_clients()
        
        # 获取用户偏好
        user_preferences = get_user_preferences()
        
        # 创建系统提示词（仅用于BA）
        system_prompt = create_system_prompt(user_preferences)
        
        # 尝试加载缓存的音色选择
        cached_data = load_cached_data()
        voice_list = []
        selected_voice = cached_data.get('selected_voice', None) if cached_data else None
        
        if selected_voice:
            logger.info(f"从缓存加载音色: {selected_voice.get('customName', 'Unknown')}")
        
        while True:
            try:
                show_menu()
                choice = get_menu_choice()
                
                if choice == 1:
                    # 纯文字对话
                    conversation_loop(client_sf, client_ba, system_prompt, False, None)
                    
                elif choice == 2:
                    # 文字 + 语音对话
                    if not selected_voice:
                        print("请先选择语音音色")
                        # 获取音色列表
                        if not voice_list:
                            logger.info("正在获取音色列表...")
                            voice_list = get_voice_list(client_sf.api_key)
                        
                        if voice_list:
                            selected_voice = select_voice(voice_list)
                            if not selected_voice:
                                print("未选择音色，将使用纯文字模式")
                                conversation_loop(client_sf, client_ba, system_prompt, False, None)
                            else:
                                conversation_loop(client_sf, client_ba, system_prompt, True, selected_voice)
                        else:
                            print("无法获取音色列表，将使用纯文字模式")
                            conversation_loop(client_sf, client_ba, system_prompt, False, None)
                    else:
                        conversation_loop(client_sf, client_ba, system_prompt, True, selected_voice)
                        
                elif choice == 3:
                    # 选择语音音色
                    logger.info("正在获取音色列表...")
                    voice_list = get_voice_list(client_sf.api_key)
                    if voice_list:
                        selected_voice = select_voice(voice_list)
                        if selected_voice:
                            print(f"✅ 音色设置成功: {selected_voice.get('customName', 'Unknown')}")
                        else:
                            print("❌ 未选择音色")
                    else:
                        print("❌ 无法获取音色列表，请检查网络连接和API密钥")
                        
                elif choice == 4:
                    # 更新用户偏好
                    logger.info("用户选择更新偏好设置")
                    user_preferences = get_user_preferences()
                    system_prompt = create_system_prompt(user_preferences)
                    print("✅ 用户偏好已更新")
                    
                elif choice == 5:
                    # 退出程序
                    logger.info("用户选择退出程序")
                    print("感谢使用，再见！")
                    break
                    
            except KeyboardInterrupt:
                logger.info("用户中断程序")
                print("\n程序已中断，再见！")
                break
            except Exception as e:
                logger.error(f"主程序出错: {str(e)}", exc_info=True)
                print("发生错误，请重试。")
    except Exception as e:
        logger.error(f"程序初始化失败: {str(e)}", exc_info=True)
        print("程序初始化失败，请检查日志文件。")

if __name__ == "__main__":
    main()