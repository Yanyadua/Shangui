#!/bin/bash
# Growth Engine 服务器启动脚本

cd /Users/yaoduanyang/Desktop/myVoice/voice-server

echo "======================================"
echo "🚀 Growth Engine 服务器启动中..."
echo "======================================"
echo ""
echo "📂 工作目录: $(pwd)"
echo "📡 服务地址: http://127.0.0.1:8000"
echo "📚 API 文档: http://127.0.0.1:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "======================================"
echo ""

python run.py
