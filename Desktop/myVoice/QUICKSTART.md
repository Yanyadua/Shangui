# Growth Engine - 快速启动指南

## ✅ 环境检查

依赖已安装完成!系统已就绪。

---

## 🚀 启动步骤

### 1️⃣ 启动服务器 (Terminal 1)

```bash
cd /Users/yaoduanyang/Desktop/myVoice/voice-server
python run.py
```

**期望输出:**
```
Loading Whisper model (base) on cpu...
Whisper model loaded successfully!
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**访问 API 文档:** http://127.0.0.1:8000/docs

---

### 2️⃣ 启动客户端 (Terminal 2 - 新开一个终端)

```bash
cd /Users/yaoduanyang/Desktop/myVoice/voice-client
python main.py
```

**期望输出:** PySide6 窗口打开,显示录音界面

---

## 🎤 使用流程

1. **点击 "开始录音"** 按钮
2. **说话** (例如: "今天刷了两小时LeetCode")
3. **点击 "停止录音"**
4. **点击 "上传并处理"**
5. **查看结果** - 系统会显示:
   - 转写文本
   - 识别的活动
   - 成长增量数据

---

## 📊 数据流

```
录音 → Whisper转写 → DeepSeek解析 → 计算Delta → 存储数据库
```

---

## 🔧 故障排查

### 服务器启动失败
```bash
# 检查端口是否被占用
lsof -i :8000

# 查看详细错误
python run.py --log-level debug
```

### 客户端连接失败
- 确认服务器已启动
- 确认服务器运行在 http://127.0.0.1:8000

### Whisper 模型下载慢
- 首次运行会下载模型 (~150MB)
- 如下载失败,可手动下载:
  ```bash
  # 设置镜像 (可选)
  export HF_ENDPOINT=https://hf-mirror.com
  ```

---

## 📁 项目文件

- **服务器**: `/Users/yaoduanyang/Desktop/myVoice/voice-server`
- **客户端**: `/Users/yaoduanyang/Desktop/myVoice/voice-client`
- **数据库**: `/Users/yaoduanyang/Desktop/myVoice/voice-server/data/growth_engine.db`
- **配置**: `/Users/yaoduanyang/Desktop/myVoice/voice-server/config.yaml`

---

## 🎯 测试命令

**测试 DeepSeek API:**
```bash
cd /Users/yaoduanyang/Desktop/myVoice/voice-server
python test_deepseek_direct.py
```

**查看历史记录:**
```bash
curl http://127.0.0.1:8000/api/v1/records
```

---

## 💡 提示

- 首次录音前,确保麦克风已授权
- DeepSeek API 按使用量计费,注意控制使用
- 本地 Whisper 免费,无需担心
- 数据存储在本地 SQLite,隐私安全

---

**需要帮助?** 检查 `docs/plans/` 目录下的设计文档
