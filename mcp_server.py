from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import MCPRequest, MCPResponse, TodoCreate, TodoUpdate
from database import DatabaseManager
import uvicorn
import os
from dotenv import load_dotenv
from datetime import datetime, date
import json

load_dotenv()

app = FastAPI(title="Todo MCP Server", version="1.0.0")

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DatabaseManager()

def serialize_datetime(obj):
    """JSON序列化日期时间对象"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

@app.post("/mcp", response_model=MCPResponse)
async def handle_mcp_request(request: MCPRequest):
    """处理MCP请求"""
    try:
        method = request.method
        params = request.params
        
        if method == "create_todo":
            todo_data = TodoCreate(**params)
            todo = db.create_todo(todo_data)
            result = json.loads(json.dumps(todo.dict(), default=serialize_datetime))
            return MCPResponse(result={"todo": result, "message": "待办事项创建成功"})
        
        elif method == "get_todos":
            completed = params.get("completed")
            todos = db.get_todos(completed=completed)
            result = [json.loads(json.dumps(todo.dict(), default=serialize_datetime)) for todo in todos]
            return MCPResponse(result={"todos": result})
        
        elif method == "get_todo":
            todo_id = params.get("id")
            if not todo_id:
                raise HTTPException(status_code=400, detail="缺少todo ID")
            
            todo = db.get_todo_by_id(todo_id)
            if not todo:
                return MCPResponse(error="待办事项不存在")
            
            result = json.loads(json.dumps(todo.dict(), default=serialize_datetime))
            return MCPResponse(result={"todo": result})
        
        elif method == "update_todo":
            todo_id = params.get("id")
            if not todo_id:
                raise HTTPException(status_code=400, detail="缺少todo ID")
            
            update_data = {k: v for k, v in params.items() if k != "id"}
            todo_update = TodoUpdate(**update_data)
            todo = db.update_todo(todo_id, todo_update)
            
            if not todo:
                return MCPResponse(error="待办事项不存在或更新失败")
            
            result = json.loads(json.dumps(todo.dict(), default=serialize_datetime))
            return MCPResponse(result={"todo": result, "message": "待办事项更新成功"})
        
        elif method == "delete_todo":
            todo_id = params.get("id")
            if not todo_id:
                raise HTTPException(status_code=400, detail="缺少todo ID")
            
            success = db.delete_todo(todo_id)
            if success:
                return MCPResponse(result={"message": "待办事项删除成功"})
            else:
                return MCPResponse(error="待办事项不存在或删除失败")
        
        elif method == "search_todos":
            query = params.get("query", "")
            todos = db.search_todos(query)
            result = [json.loads(json.dumps(todo.dict(), default=serialize_datetime)) for todo in todos]
            return MCPResponse(result={"todos": result})
        
        elif method == "mark_completed":
            todo_id = params.get("id")
            if not todo_id:
                raise HTTPException(status_code=400, detail="缺少todo ID")
            
            todo_update = TodoUpdate(completed=True)
            todo = db.update_todo(todo_id, todo_update)
            
            if not todo:
                return MCPResponse(error="待办事项不存在或标记失败")
            
            result = json.loads(json.dumps(todo.dict(), default=serialize_datetime))
            return MCPResponse(result={"todo": result, "message": "待办事项已标记为完成"})
        
        else:
            return MCPResponse(error=f"不支持的方法: {method}")
    
    except Exception as e:
        return MCPResponse(error=f"服务器错误: {str(e)}")

@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        # 测试数据库连接
        todos = db.get_todos()
        return {"status": "healthy", "database": "connected", "todos_count": len(todos)}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    port = int(os.getenv("MCP_SERVER_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
