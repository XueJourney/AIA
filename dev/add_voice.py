import requests
import json
import base64
import os
import mimetypes

def get_audio_base64(file_path):
    """
    读取音频文件并转换为base64编码
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    # 获取文件的MIME类型
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type or not mime_type.startswith('audio/'):
        # 如果无法识别MIME类型，根据文件扩展名判断
        ext = os.path.splitext(file_path)[1].lower()
        mime_map = {
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.m4a': 'audio/mp4',
            '.aac': 'audio/aac',
            '.ogg': 'audio/ogg',
            '.flac': 'audio/flac'
        }
        mime_type = mime_map.get(ext, 'audio/mpeg')
    
    # 读取文件并编码为base64
    with open(file_path, 'rb') as audio_file:
        audio_data = audio_file.read()
        base64_encoded = base64.b64encode(audio_data).decode('utf-8')
    
    return f"data:{mime_type};base64,{base64_encoded}"

def upload_audio_voice():
    """
    上传音频文件到SiliconFlow API
    """
    # 获取用户输入
    file_path = input("请输入音频文件路径: ").strip()
    
    # 去除可能的引号
    if file_path.startswith('"') and file_path.endswith('"'):
        file_path = file_path[1:-1]
    elif file_path.startswith("'") and file_path.endswith("'"):
        file_path = file_path[1:-1]
    
    try:
        # 获取音频的base64编码
        audio_base64 = get_audio_base64(file_path)
        print("音频文件读取成功!")
        
        # 获取其他必要信息
        api_key = input("请输入你的API密钥: ").strip()
        voice_name = input("请输入自定义音频名称: ").strip()
        text_content = input("请输入音频对应的文字内容: ").strip()
        
        # API配置
        url = "https://api.siliconflow.cn/v1/uploads/audio/voice"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "FunAudioLLM/CosyVoice2-0.5B",
            "customName": voice_name,
            "audio": audio_base64,
            "text": text_content
        }
        
        print("正在上传音频文件...")
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        # 打印响应结果
        print(f"\n响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("上传成功!")
            print("响应内容:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print("上传失败!")
            print("错误信息:")
            try:
                print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            except:
                print(response.text)
                
    except FileNotFoundError as e:
        print(f"错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    upload_audio_voice()