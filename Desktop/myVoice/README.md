# Growth Engine

语音驱动的个人成长量化系统

## 项目结构

```
myVoice/
├── voice-server/     # 后端服务 (FastAPI)
├── voice-client/     # 客户端 (PySide6)
├── docs/            # 文档
├── start_server.sh   # 服务器启动脚本
└── start_sprite.sh   # 桌面精灵启动脚本
```

## 快速开始

### 1. 安装依赖

**服务器端:**
```bash
cd voice-server
pip install -r requirements.txt
```

**客户端 (macOS):**
```bash
cd voice-client
../install_client.sh  # 自动安装Homebrew依赖
pip install -r requirements.txt
```

**客户端 (其他系统):**
```bash
cd voice-client
pip install -r requirements.txt
# Portaudio需要手动安装
```

### 2. 配置 API Keys

复制示例配置并填写你的 API Keys:

```bash
cd voice-server
cp config.yaml.example config.yaml
# 编辑 config.yaml,填写 deepseek API key
# whisper key是可选的(使用本地faster-whisper)
```

### 3. 启动服务器

```bash
./start_server.sh
# 或
cd voice-server && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

服务器将在 http://127.0.0.1:8000 启动

API 文档: http://127.0.0.1:8000/docs

**终端输出示例**:
```
[STEP 1] 提取活动中...
[STEP 1] ✓ 提取完成 (2个活动)
[STEP 2] 分类活动 (2个)...
[STEP 2] ✓ 分类完成
[STEP 3] 评估活动强度...
[STEP 3] ✓ 评估完成
```

### 4. 启动桌面精灵

```bash
./start_sprite.sh
# 或
cd voice-client && python sprite_pro.py
```

## 桌面精灵

Growth Engine 提供一个可爱的Q版桌面精灵，支持语音交互。

### 精灵状态

- 🌱 **待机状态** (normal) - 准备就绪，绿色
- 🎙 **录音状态** (recording) - 正在录音，红色
- 💭 **思考状态** (thinking) - AI分析中，蓝色
- 🎉 **庆祝状态** (success) - 分析完成，黄色
- 😢 **错误状态** (error) - 处理失败，灰色

### 交互方式

1. **点击精灵身体** → 弹出圆形菜单
2. **选择功能按钮**（录音/分析/设置/帮助）
3. **点击外部区域** → 收起菜单
4. **拖动精灵** → 移动窗口位置

### 圆形菜单

- 🎤 **录音按钮** - 开始/停止录音
- 🚀 **分析按钮** - 分析录音内容
- ⚙️ **设置按钮** - 打开设置（开发中）
- ❓ **帮助按钮** - 查看帮助信息

### 自定义精灵

你可以替换 `voice-client/assets/sprites/` 中的图片来自定义精灵外观。

详细指南: [精灵图片生成指南](docs/sprite-generation-guide.md)

图片要求:
- 尺寸: 256x256 像素
- 格式: PNG, 透明背景
- 风格: 宝可梦Q版风格

## 功能特性

### 后端
- 🎤 语音转文本 (faster-whisper 本地运行)
- 🤖 AI 活动解析 (DeepSeek 多步骤推理)
- 📊 成长增量计算 (规则引擎)
- 💾 数据持久化 (SQLite)
- 📈 推理过程可视化 (终端输出)

### 前端
- 🌱 Q版桌面精灵
- 🎨 5种表情状态
- 🎯 圆形菜单交互
- ✨ 流畅动画效果
- 🖱️ 拖拽移动

## 技术栈

- **后端**: FastAPI, SQLite, httpx, Jinja2, faster-whisper
- **前端**: PySide6 (Qt6), PyAudio
- **AI**: DeepSeek Chat, faster-whisper
- **架构**: REST API, 多步骤推理 Agent

## 开发

### 运行测试
```bash
cd voice-server
pytest tests/
```

### 系统检查
```bash
./check_system.sh
```

### 查看日志
- 后端推理过程: 终端输出
- 前端错误: 查看控制台

## 文档

- [精灵图片生成指南](docs/sprite-generation-guide.md)
- [测试记录](TESTING.md)
- [设计文档](docs/plans/)
- [API文档](http://127.0.0.1:8000/docs)

## License

MIT