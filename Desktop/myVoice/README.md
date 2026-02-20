# Growth Engine

语音驱动的个人成长量化系统

## 项目结构

```
myVoice/
├── voice-server/     # 后端服务 (FastAPI)
├── voice-client/     # 客户端 (PySide6)
└── docs/            # 文档
```

## 快速开始

### 1. 安装依赖

**服务器端:**
```bash
cd voice-server
pip install -r requirements.txt
```

**客户端:**
```bash
cd voice-client
pip install -r requirements.txt
```

### 2. 配置 API Keys

复制示例配置并填写你的 API Keys:

```bash
cd voice-server
cp config.yaml.example config.yaml
# 编辑 config.yaml,填写 deepseek 和 whisper API keys
```

### 3. 启动服务器

```bash
cd voice-server
python run.py
```

服务器将在 http://127.0.0.1:8000 启动

API 文档: http://127.0.0.1:8000/docs

### 4. 启动客户端

```bash
cd voice-client
python main.py
```

## 功能特性

- 🎤 语音录音转文本 (Whisper API)
- 🤖 AI 活动解析 (DeepSeek 多步骤推理)
- 📊 成长增量计算 (规则引擎)
- 💾 数据持久化 (SQLite)

## 技术栈

- **后端**: FastAPI, SQLite, httpx, Jinja2
- **前端**: PySide6, PyAudio
- **AI**: OpenAI Whisper, DeepSeek Chat

## License

MIT