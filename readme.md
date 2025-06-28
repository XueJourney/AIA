# AIA - AI Assistant

> 智能双模式AI对话系统，集成逻辑分析与人性化回复

## 📖 项目简介

AIA（AI Assistant）是一个创新的双模式AI对话系统，通过集成两个不同特性的AI模型，为用户提供既有深度逻辑分析又有温暖人性化交流的对话体验。

### ✨ 核心特性

- 🧠 **双模式对话**：逻辑分析 + 人性化回复
- 🎯 **智能前缀控制**：快速切换对话模式
- 🔊 **语音合成**：支持多种音色的语音回复
- 👤 **个性化定制**：根据用户偏好调整回复风格
- 💾 **智能缓存**：自动保存用户设置和API密钥
- 🖥️ **双界面支持**：图形界面(GUI) + 命令行界面(CLI)

## 🚀 工作原理

AIA采用独特的双AI协作模式：

1. **逻辑分析层**（DeepSeek-R1）：对用户问题进行深入的逻辑分析，提取核心要点和解决思路
2. **人性化回复层**（GPT-4o）：基于逻辑分析结果，结合用户偏好生成温暖、个性化的回复

### 对话模式

- **标准模式**：完整的双层处理（逻辑分析 → 人性化回复）
- **直接模式**（前缀 `！`）：跳过逻辑分析，直接人性化回复
- **分析模式**（前缀 `#`）：仅进行逻辑分析，不生成人性化回复

## 🛠️ 安装与配置

### 环境要求

- Python 3.8+
- tkinter（GUI版本）
- 所需Python包：`openai`, `requests`, `pydub`, `simpleaudio`

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/XueJourney/AIA.git
   cd AIA
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行程序**
   ```bash
   # GUI版本
   python mainUI.py
   
   # CLI版本
   python mainCLI.py
   ```

### API配置

程序需要以下API密钥：

- [**SiliconFlow API**](https://cloud.siliconflow.cn/i/Rvi7CUIa)：用于逻辑分析和语音合成
- [**BestAPI**](https://aigcbest.top/register?aff=tk8E)：用于人性化回复

首次运行时，程序会引导您完成API密钥配置。

## 📱 使用界面

### GUI版本特性
- 直观的图形界面
- 实时状态显示
- 语音音色选择
- 对话历史管理
- 用户偏好设置

### CLI版本特性
- 轻量级命令行界面
- 快速启动和响应
- 支持所有核心功能
- 适合服务器环境


## ⚙️ 配置选项

### 用户偏好设置
- **职业信息**：影响专业词汇和建议类型
- **称呼偏好**：个性化称呼方式
- **回复风格**：正式/轻松/专业等风格
- **补充信息**：其他个人偏好

### 语音设置
- 支持多种音色选择
- 可开启/关闭语音回复
- 自动音频播放

## 🔧 技术栈

- **GUI框架**：tkinter
- **AI接口**：OpenAI API兼容
- **语音合成**：CosyVoice2
- **音频处理**：pydub, simpleaudio
- **数据存储**：JSON本地缓存
- **日志系统**：Python logging

## 🚧 开发计划

- [ ] 支持更多AI模型
- [ ] 增加对话导出功能
- [ ] 支持插件系统
- [ ] Web版本界面
- [ ] 多语言支持
- [ ] 云端同步功能

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出改进建议！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 GUN3.0 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- 项目地址：[https://github.com/XueJourney/AIA](https://github.com/XueJourney/AIA)
- 问题反馈：[Issues](https://github.com/XueJourney/AIA/issues)

## 🙏 致谢

感谢以下项目和服务：
- aigcbest OpenAI GPT-4o
- SiliconFlow DeepSeek-R1
- SiliconFlow CosyVoice2语音合成

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！