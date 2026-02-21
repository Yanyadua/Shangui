#!/bin/bash
# Growth Engine 客户端启动脚本

cd /Users/yaoduanyang/Desktop/myVoice/voice-client

echo "======================================"
echo "🎤 Growth Engine 客户端启动中..."
echo "======================================"
echo ""
echo "📂 工作目录: $(pwd)"
echo "🔗 连接到: http://127.0.0.1:8000"
echo ""
echo "请确保服务器已启动!"
echo "======================================"
echo ""

# 确保从正确目录运行
python main.py
