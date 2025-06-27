# AI Agent MCP 待办事项应用 - Python调用关系分析

## 🏗️ 整体架构概览

```
┌─────────────────────────────────────────────────────────────────────┐
│                         用户交互层                                    │
├─────────────────────────────────────────────────────────────────────┤
│  main.py (CLI界面)           demo.py (演示脚本)                      │
│  └─ TodoApp                  └─ 演示函数                             │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ 调用
┌─────────────────────────────────────────────────────────────────────┐
│                         AI 代理层                                     │
├─────────────────────────────────────────────────────────────────────┤
│  ai_agent.py                enhanced_ai_agent.py (增强版)            │
│  └─ AIAgent                 └─ EnhancedAIAgent                       │
│     ├─ process_user_input       ├─ analyze_user_intent                │
│     ├─ call_azure_openai        ├─ extract_parameters                 │
│     └─ execute_function_call    └─ process_user_input_with_intent     │
└─────────────────────────────────────────────────────────────────────┘
                    │                              │
            调用Azure OpenAI                   调用MCP服务器
                    │                              │
                    ▼                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Azure OpenAI                        MCP 服务器层                      │
│ GPT-4.1 模型                                                          │
│ Function Calling                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ HTTP API调用
┌─────────────────────────────────────────────────────────────────────┐
│                         MCP HTTP 服务器                               │
├─────────────────────────────────────────────────────────────────────┤
│  mcp_server.py                                                        │
│  └─ FastAPI 应用                                                      │
│     ├─ handle_mcp_request (POST /mcp)                                │
│     └─ health_check (GET /health)                                     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ 调用数据库管理器
┌─────────────────────────────────────────────────────────────────────┐
│                         数据访问层                                    │
├─────────────────────────────────────────────────────────────────────┤
│  database.py              models.py                                   │
│  └─ DatabaseManager       └─ 数据模型                                 │
│     ├─ create_todo           ├─ Todo                                  │
│     ├─ get_todos            ├─ TodoCreate                            │
│     ├─ update_todo          ├─ TodoUpdate                            │
│     ├─ delete_todo          ├─ MCPRequest                            │
│     └─ search_todos         └─ MCPResponse                           │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ SQL查询
┌─────────────────────────────────────────────────────────────────────┐
│                         数据存储层                                    │
├─────────────────────────────────────────────────────────────────────┤
│  PostgreSQL 数据库 (Docker容器)                                       │
│  └─ todos 表                                                          │
│     ├─ id (主键)                                                      │
│     ├─ title (标题)                                                   │
│     ├─ content (内容)                                                 │
│     ├─ due_date (截止日期)                                            │
│     ├─ completed (完成状态)                                           │
│     ├─ created_at (创建时间)                                          │
│     └─ updated_at (更新时间)                                          │
└─────────────────────────────────────────────────────────────────────┘
```

## 📁 文件详细调用关系

### 1. **main.py** (主入口点)
```python
main.py
├─ 导入：ai_agent.AIAgent
├─ 导入：typer, rich (UI库)
└─ 类：TodoApp
   ├─ __init__(): 创建 AIAgent 实例
   ├─ run_interactive(): 交互式循环
   └─ 调用：agent.process_user_input(user_input)
```

**作用**: CLI用户界面，处理用户交互

### 2. **ai_agent.py** (AI代理核心)
```python
ai_agent.py
├─ 导入：httpx, json, os
├─ 导入：dotenv (环境变量)
└─ 类：AIAgent
   ├─ __init__(): 初始化Azure OpenAI配置和工具定义
   ├─ call_azure_openai(): 调用Azure OpenAI API
   ├─ call_mcp_server(): HTTP调用MCP服务器
   ├─ execute_function_call(): 执行函数调用
   └─ process_user_input(): 主处理逻辑
      ├─ 构建消息 → Azure OpenAI
      ├─ 解析tool_calls → function_name + arguments
      └─ 调用 execute_function_call()
```

**作用**: AI智能代理，协调用户输入、AI决策和函数执行

### 3. **mcp_server.py** (MCP HTTP服务器)
```python
mcp_server.py
├─ 导入：FastAPI, HTTPException
├─ 导入：models.*, database.DatabaseManager
└─ FastAPI应用
   ├─ POST /mcp: handle_mcp_request()
   │  ├─ 解析MCPRequest
   │  ├─ 根据method调用DatabaseManager方法
   │  └─ 返回MCPResponse
   └─ GET /health: health_check()
      └─ 测试数据库连接
```

**作用**: MCP协议HTTP服务器，提供RESTful API接口

### 4. **database.py** (数据库管理器)
```python
database.py
├─ 导入：psycopg2, psycopg2.extras
├─ 导入：models.Todo, TodoCreate, TodoUpdate
└─ 类：DatabaseManager
   ├─ __init__(): 读取数据库连接字符串
   ├─ get_connection(): 创建PostgreSQL连接
   ├─ create_todo(TodoCreate) → Todo
   ├─ get_todos(completed?) → List[Todo]
   ├─ get_todo_by_id(id) → Todo?
   ├─ update_todo(id, TodoUpdate) → Todo?
   ├─ delete_todo(id) → bool
   └─ search_todos(query) → List[Todo]
```

**作用**: 数据访问层，封装所有数据库操作

### 5. **models.py** (数据模型)
```python
models.py
├─ 导入：pydantic.BaseModel
├─ 导入：typing, datetime
└─ 数据模型
   ├─ TodoBase: 基础待办事项字段
   ├─ TodoCreate: 创建待办事项请求
   ├─ TodoUpdate: 更新待办事项请求
   ├─ Todo: 完整的待办事项模型
   ├─ MCPRequest: MCP请求格式
   └─ MCPResponse: MCP响应格式
```

**作用**: 数据模型定义，类型验证和序列化

### 6. **demo.py** (演示脚本)
```python
demo.py
├─ 导入：ai_agent.AIAgent
└─ 演示函数
   ├─ 创建AIAgent实例
   ├─ 模拟用户输入
   └─ 调用agent.process_user_input()
```

**作用**: 功能演示和测试

## 🔄 典型调用流程

### 用户创建待办事项的完整流程：

```
1. 用户输入: "创建一个任务：学习Python"
   ↓
2. main.py → TodoApp.run_interactive()
   ↓
3. ai_agent.py → AIAgent.process_user_input()
   ├─ 构建消息发送给Azure OpenAI
   ├─ GPT-4.1分析用户意图，选择create_todo函数
   ├─ 提取参数: {"title": "学习Python"}
   └─ 调用execute_function_call("create_todo", params)
   ↓
4. ai_agent.py → AIAgent.call_mcp_server()
   ├─ HTTP POST to localhost:8000/mcp
   ├─ 请求体: {"method": "create_todo", "params": {"title": "学习Python"}}
   ↓
5. mcp_server.py → handle_mcp_request()
   ├─ 解析MCPRequest
   ├─ 创建TodoCreate对象
   └─ 调用db.create_todo(todo_data)
   ↓
6. database.py → DatabaseManager.create_todo()
   ├─ 建立PostgreSQL连接
   ├─ 执行INSERT SQL语句
   └─ 返回新创建的Todo对象
   ↓
7. 响应返回路径 (逆向)
   database.py → mcp_server.py → ai_agent.py → main.py → 用户
```

## 🧩 关键设计模式

### 1. **分层架构模式**
- **表现层**: main.py (CLI界面)
- **业务逻辑层**: ai_agent.py (AI处理)
- **服务层**: mcp_server.py (API服务)
- **数据访问层**: database.py (数据库操作)
- **数据模型层**: models.py (数据结构)

### 2. **代理模式**
- `AIAgent`作为用户和各种服务之间的代理
- 协调Azure OpenAI、MCP服务器的调用

### 3. **工厂模式**
- `DatabaseManager`根据环境变量创建数据库连接
- 模型类根据输入数据创建对象实例

### 4. **策略模式**
- `enhanced_ai_agent.py`提供了两种function选择策略：
  - 基于规则的意图分析
  - 基于AI模型的智能选择

## 🔧 依赖关系总结

```
main.py
└─ ai_agent.py
   ├─ httpx (HTTP客户端)
   ├─ Azure OpenAI API
   └─ MCP Server (localhost:8000)

mcp_server.py
├─ FastAPI (Web框架)
├─ models.py
└─ database.py
   ├─ psycopg2 (PostgreSQL驱动)
   ├─ models.py
   └─ PostgreSQL数据库

models.py
└─ pydantic (数据验证)

demo.py
└─ ai_agent.py
```

## 💡 架构优势

1. **松耦合**: 每个组件职责单一，便于维护和测试
2. **可扩展**: 可以轻松添加新的功能或替换组件
3. **标准化**: 使用MCP协议，符合行业标准
4. **容错性**: 每层都有错误处理机制
5. **可测试**: 模块化设计便于单元测试

这个架构体现了现代软件开发的最佳实践，将AI能力、Web服务、数据库操作有机结合在一起。
