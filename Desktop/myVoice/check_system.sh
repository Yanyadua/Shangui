#!/bin/bash
# Growth Engine 系统检查脚本

echo "======================================"
echo "🔍 Growth Engine 系统检查"
echo "======================================"
echo ""

cd /Users/yaoduanyang/Desktop/myVoice

# 检查 Python
echo "1️⃣ Python 环境:"
python --version
echo ""

# 检查服务器依赖
echo "2️⃣ 服务器依赖:"
cd voice-server
python -c "import fastapi, uvicorn, httpx, pydantic, aiosqlite" 2>/dev/null && echo "   ✅ 所有服务器依赖已安装" || echo "   ❌ 缺少服务器依赖"
echo ""

# 检查客户端依赖
echo "3️⃣ 客户端依赖:"
cd ../voice-client
python -c "import PySide6, pyaudio" 2>/dev/null && echo "   ✅ 所有客户端依赖已安装" || echo "   ❌ 缺少客户端依赖"
echo ""

# 检查配置文件
echo "4️⃣ 配置文件:"
cd ../voice-server
if [ -f "config.yaml" ]; then
    echo "   ✅ config.yaml 存在"
    # 检查 API key
    if grep -q "YOUR_DEEPSEEK_API_KEY" config.yaml 2>/dev/null; then
        echo "   ⚠️  API Key 未配置"
    else
        echo "   ✅ API Key 已配置"
    fi
else
    echo "   ❌ config.yaml 不存在"
fi
echo ""

# 检查模块导入
echo "5️⃣ 服务器模块:"
cd voice-server
python -c "from app.main import app" 2>/dev/null && echo "   ✅ 服务器模块可导入" || echo "   ❌ 服务器模块导入失败"
echo ""

echo "6️⃣ 客户端模块:"
cd ../voice-client
python -c "import sys; sys.path.insert(0, '.'); from ui.main_window import MainWindow" 2>/dev/null && echo "   ✅ 客户端模块可导入" || echo "   ❌ 客户端模块导入失败"
echo ""

echo "======================================"
echo "✅ 系统检查完成!"
echo ""
echo "启动服务器: ./start_server.sh"
echo "启动客户端: ./start_client.sh"
echo "======================================"
