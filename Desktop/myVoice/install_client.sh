#!/bin/bash
# Growth Engine 客户端依赖安装脚本

echo "======================================"
echo "📦 安装客户端依赖..."
echo "======================================"

cd /Users/yaoduanyang/Desktop/myVoice/voice-client

# 1. 安装 PySide6
echo ""
echo "1️⃣ 安装 PySide6..."
pip install PySide6 -i https://pypi.tuna.tsinghua.edu.cn/simple

# 2. 安装 requests
echo ""
echo "2️⃣ 安装 requests..."
pip install requests

# 3. 安装 python-dotenv
echo ""
echo "3️⃣ 安装 python-dotenv..."
pip install python-dotenv

# 4. 安装 PyAudio (macOS 需要 portaudio)
echo ""
echo "4️⃣ 安装 PyAudio..."
echo "   检测到 macOS,使用 brew 安装 portaudio..."

if ! command -v brew &> /dev/null; then
    echo "   ❌ Homebrew 未安装"
    echo "   请先安装 Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo ""
    echo "   或者跳过 PyAudio(录音功能将不可用)"
else
    echo "   ✅ Homebrew 已安装"
    echo "   安装 portaudio..."
    brew install portaudio 2>/dev/null || echo "   portaudio 可能已安装"

    echo "   安装 PyAudio..."
    pip install pyaudio
fi

echo ""
echo "======================================"
echo "✅ 客户端依赖安装完成!"
echo ""
echo "启动客户端: python main.py"
echo "或者: ./start_client.sh"
echo "======================================"
