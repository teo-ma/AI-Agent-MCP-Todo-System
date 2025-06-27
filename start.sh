#!/bin/bash

echo "🚀 启动待办事项应用..."

# 检查是否安装了Docker
if ! command -v docker &> /dev/null; then
    echo "❌ 请先安装Docker"
    exit 1
fi

# 检查是否安装了docker compose
if ! docker compose version &> /dev/null; then
    echo "❌ 请先安装Docker Compose"
    exit 1
fi

# 安装Python依赖
echo "📦 安装Python依赖..."
pip install -r requirements.txt

# 启动数据库
echo "🗄️ 启动PostgreSQL数据库..."
docker compose up -d postgres

# 等待数据库启动
echo "⏳ 等待数据库准备就绪..."
sleep 10

# 启动MCP服务器（后台运行）
echo "🔧 启动MCP服务器..."
python mcp_server.py &
MCP_PID=$!

# 等待服务器启动
sleep 3

# 启动交互式客户端
echo "🤖 启动AI助手..."
python main.py interactive

# 清理
echo "🧹 清理进程..."
kill $MCP_PID 2>/dev/null
