# 智能待办事项管理系统

基于AI Agent MCP的Python待办事项应用，支持Azure OpenAI和标准OpenAI模型，提供自然语言交互管理日常任务。

## 功能特性

- 🤖 **AI智能交互** - 使用自然语言创建、查询、修改、删除待办事项
- 📝 **完整任务管理** - 支持标题、内容、完成日期的完整任务信息
- 🗄️ **PostgreSQL数据库** - 可靠的数据持久化存储
- 🌐 **MCP HTTP服务器** - 标准的MCP协议接口
- 💻 **美观终端界面** - 使用Rich库的现代化命令行界面
- 🔍 **智能搜索** - 支持关键词搜索任务

## 系统架构

```
┌─────────────────┐    ┌───────────────────┐    ┌─────────────────┐
│   Terminal UI   │───▶│   AI Agent        │───▶│  Azure OpenAI   │
│   (Rich CLI)    │    │   (客户端)        │    │  或 OpenAI       │
└─────────────────┘    └───────────────────┘    └─────────────────┘
         │                        │
         │                        ▼
         │              ┌───────────────────┐    ┌─────────────────┐
         └─────────────▶│  MCP HTTP Server  │───▶│   PostgreSQL    │
                        │   (FastAPI)       │    │   (Docker)      │
                        └───────────────────┘    └─────────────────┘
```

## 文件结构

```
AI-Agent-MCP-Todo-System/
├── main.py              # 主程序和CLI界面
├── ai_agent.py          # AI Agent客户端
├── mcp_server.py        # MCP HTTP服务器
├── database.py          # 数据库操作
├── models.py            # 数据模型
├── docker-compose.yml   # Docker配置
├── init.sql            # 数据库初始化脚本
├── requirements.txt    # Python依赖
├── .env.example        # 环境变量配置模板
├── .env               # 环境变量配置（需要自行创建）
├── start.sh          # 启动脚本
└── README.md         # 说明文档
```

## 安装和使用

### 1. 环境要求

- Python 3.8+
- Docker 和 Docker Compose
- pip (Python包管理器)

### 2. 环境配置

在启动应用之前，需要配置环境变量：

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入您的实际配置
vi .env  # 或使用其他编辑器
```

### 3. 快速启动（推荐）

使用一键启动脚本，自动完成所有设置：

```bash
# 克隆或下载项目
git clone https://github.com/teo-ma/AI-Agent-MCP-Todo-System.git
cd AI-Agent-MCP-Todo-System

# 给启动脚本执行权限
chmod +x start.sh

# 运行启动脚本（会自动安装依赖、启动数据库、启动服务）
./start.sh
```

### 4. 手动启动（高级用户）

如果您希望分步控制启动过程，可以选择手动启动：

如果您希望分步控制启动过程，可以选择手动启动：

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动数据库
docker-compose up -d postgres

# 3. 等待数据库准备就绪
sleep 10

# 4. 启动MCP服务器（新终端窗口）
python mcp_server.py

# 5. 启动AI助手（另一个新终端窗口）
python main.py interactive
```

> **注意**: 快速启动和手动启动二选一即可，推荐使用快速启动方式。

### 5. 使用CLI命令

```bash
# 启动交互式助手
python main.py interactive

# 仅启动MCP服务器
python main.py server

# 环境设置
python main.py setup
```

## 使用示例

启动应用后，您可以使用自然语言与AI助手交互：

### 创建任务
```
您: 创建一个任务：明天上午开会讨论项目进度
您: 添加一个待办事项，标题是"买菜"，内容是"买胡萝卜、土豆、鸡蛋"，完成日期是2025-06-27
```

### 查看任务
```
您: 显示我的所有任务
您: 查看未完成的任务
您: 显示已完成的任务
```

### 更新任务
```
您: 修改任务1的标题为"完成项目设计"
您: 将任务2的完成日期改为2025-06-28
您: 更新任务3的内容
```

### 删除任务
```
您: 删除任务5
您: 移除ID为3的任务
```

### 搜索任务
```
您: 搜索包含"项目"的任务
您: 查找关于"会议"的待办事项
```

### 标记完成
```
您: 标记任务1为已完成
您: 完成任务4
```

## 配置说明

### 环境变量配置

项目使用环境变量来管理配置，请按以下步骤设置：

1. **复制环境变量模板**：
   ```bash
   cp .env.example .env
   ```

2. **编辑 .env 文件**，填入您的实际配置：

#### 方式一：使用 Azure OpenAI（推荐）

```env
# 数据库配置
DATABASE_URL=postgresql://todouser:todopass123@localhost:5432/todoapp
MCP_SERVER_PORT=8000

# Azure OpenAI 配置
AZURE_OPENAI_ENDPOINT=https://你的资源名.openai.azure.com/openai/deployments/你的部署名/chat/completions?api-version=2024-02-01
AZURE_OPENAI_API_KEY=你的Azure_OpenAI_API_密钥
AZURE_OPENAI_DEPLOYMENT_NAME=你的模型部署名称
```

**获取 Azure OpenAI 配置信息**：
1. 登录 [Azure 门户](https://portal.azure.com)
2. 找到您的 Azure OpenAI 资源
3. 在"密钥和终结点"页面获取 API 密钥和终结点
4. 在"模型部署"页面查看部署名称

#### 方式二：使用标准 OpenAI

```env
# 数据库配置
DATABASE_URL=postgresql://todouser:todopass123@localhost:5432/todoapp
MCP_SERVER_PORT=8000

# OpenAI 配置
OPENAI_API_KEY=你的OpenAI_API_密钥
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview
```

**获取 OpenAI API 密钥**：
1. 访问 [OpenAI 平台](https://platform.openai.com)
2. 登录并前往 API 密钥页面
3. 创建新的 API 密钥

#### 支持的模型

- **Azure OpenAI**: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo
- **标准 OpenAI**: gpt-4-turbo-preview, gpt-4, gpt-3.5-turbo

### 旧版环境变量格式（已弃用）

```env
# 数据库配置
DATABASE_URL=postgresql://todouser:todopass123@localhost:5432/todoapp
MCP_SERVER_PORT=8000

# Azure OpenAI配置
AZURE_OPENAI_ENDPOINT=你的完整终结点URL
AZURE_OPENAI_API_KEY=你的API密钥
AZURE_OPENAI_DEPLOYMENT_NAME=你的模型部署名称
```

### 数据库配置

PostgreSQL数据库运行在Docker容器中：
- 端口：5432
- 数据库名：todoapp
- 用户名：todouser  
- 密码：todopass123

## API接口

MCP服务器提供以下接口：

### POST /mcp
处理MCP请求，支持的方法：
- `create_todo` - 创建待办事项
- `get_todos` - 获取待办事项列表
- `get_todo` - 获取单个待办事项
- `update_todo` - 更新待办事项
- `delete_todo` - 删除待办事项
- `search_todos` - 搜索待办事项
- `mark_completed` - 标记为完成

### GET /health
健康检查接口

## 故障排除

### 1. 数据库连接问题
```bash
# 检查PostgreSQL容器状态
docker-compose ps

# 重启数据库容器
docker-compose restart postgres
```

### 2. MCP服务器无法启动
```bash
# 检查端口是否被占用
lsof -i :8000

# 修改端口配置
# 编辑 .env 文件中的 MCP_SERVER_PORT
```

### 3. Python依赖问题
```bash
# 重新安装依赖
pip install -r requirements.txt --upgrade
```

### 4. OpenAI连接问题

#### Azure OpenAI 问题：
- 检查 `AZURE_OPENAI_ENDPOINT` 格式是否正确
- 确认 `AZURE_OPENAI_API_KEY` 是否有效
- 验证 `AZURE_OPENAI_DEPLOYMENT_NAME` 与实际部署名称一致
- 确保 Azure OpenAI 资源有足够的配额

#### 标准 OpenAI 问题：
- 检查 `OPENAI_API_KEY` 是否正确
- 确认账户有足够的余额
- 验证选择的模型是否可用
- 检查网络连接是否正常

#### 通用调试方法：
```bash
# 测试 Azure OpenAI 连接
curl -X POST "你的AZURE_OPENAI_ENDPOINT" \
     -H "Content-Type: application/json" \
     -H "api-key: 你的API密钥" \
     -d '{"messages":[{"role":"user","content":"Hello"}],"max_tokens":10}'

# 测试标准 OpenAI 连接
curl -X POST "https://api.openai.com/v1/chat/completions" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer 你的API密钥" \
     -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"Hello"}],"max_tokens":10}'
```

## 开发说明

### 添加新功能
1. 在 `models.py` 中定义数据模型
2. 在 `database.py` 中实现数据库操作
3. 在 `mcp_server.py` 中添加MCP方法
4. 在 `ai_agent.py` 中添加工具定义

### 测试
```bash
# 测试数据库连接
python -c "from database import DatabaseManager; db = DatabaseManager(); print('数据库连接成功:', len(db.get_todos()))"

# 测试MCP服务器
curl -X POST http://localhost:8000/health
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
