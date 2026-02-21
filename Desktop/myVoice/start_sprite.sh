#!/bin/bash
# Growth Engine 桌面精灵启动脚本

cd /Users/yaoduanyang/Desktop/myVoice/voice-client

echo "======================================"
echo "🌱 Growth Engine 桌面精灵启动中..."
echo "======================================"
echo ""
echo "📂 工作目录: $(pwd)"
echo "🔗 连接到: http://127.0.0.1:8000"
echo ""
echo "请确保服务器已启动!"
echo "======================================"
echo ""

# 启动专业版桌面精灵
python sprite_pro.py
