import requests
url = "https://api.siliconflow.cn/v1/audio/voice/list"

headers = {
    "Authorization": "Bearer sk-cazvorbsjaylyztxmdsasxfuxwqvnqgprmwprnoeybtjaauj" # 从https://cloud.siliconflow.cn/account/ak获取
}
response = requests.get(url, headers=headers)

# print(response.status_code)
print(response.json()) # 打印响应内容（如果是JSON格式）
# 返回例子:{'result': [{'model': 'FunAudioLLM/CosyVoice2-0.5B', 'customName': 'AIA_WZH_2025062801', 'text': '闻王昌龄左迁龙标遥有此，寄李白杨花落尽子规啼。', 'uri': 'speech:AIA_WZH_2025062801:ynhbe8nsgs:zyduxdbdynahwfcvpfil'}]}

from pathlib import Path
from openai import OpenAI

speech_file_path = Path(__file__).parent / "siliconcloud-generated-speech.mp3"

client = OpenAI(
    api_key="sk-cazvorbsjaylyztxmdsasxfuxwqvnqgprmwprnoeybtjaauj", # 从 https://cloud.siliconflow.cn/account/ak 获取
    base_url="https://api.siliconflow.cn/v1"
)

with client.audio.speech.with_streaming_response.create(
  model="FunAudioLLM/CosyVoice2-0.5B", # 支持 fishaudio / GPT-SoVITS / CosyVoice2-0.5B 系列模型
  voice="speech:AIA_WZH_2025062801:ynhbe8nsgs:zyduxdbdynahwfcvpfil", # 用户上传音色名称，参考
  # 用户输入信息
  input=" 请问你能模仿粤语的口音吗？< |endofprompt| >多保重，早休息。",
  response_format="mp3"
) as response:
    response.stream_to_file(speech_file_path)