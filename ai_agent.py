import httpx
import json
import os
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class AIAgent:
    def __init__(self):
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.mcp_server_url = f"http://localhost:{os.getenv('MCP_SERVER_PORT', 8000)}/mcp"
        
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "create_todo",
                    "description": "创建新的待办事项",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "待办事项标题"},
                            "content": {"type": "string", "description": "待办事项详细内容"},
                            "due_date": {"type": "string", "format": "date", "description": "完成日期，格式为YYYY-MM-DD"}
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_todos",
                    "description": "获取待办事项列表",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "completed": {"type": "boolean", "description": "是否只获取已完成的任务，null表示获取所有任务"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_todo",
                    "description": "更新待办事项",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "待办事项ID"},
                            "title": {"type": "string", "description": "新标题"},
                            "content": {"type": "string", "description": "新内容"},
                            "due_date": {"type": "string", "format": "date", "description": "新完成日期"},
                            "completed": {"type": "boolean", "description": "是否完成"}
                        },
                        "required": ["id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_todo",
                    "description": "删除待办事项",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "待办事项ID"}
                        },
                        "required": ["id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_todos",
                    "description": "搜索待办事项",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "搜索关键词"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "mark_completed",
                    "description": "标记待办事项为已完成",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "待办事项ID"}
                        },
                        "required": ["id"]
                    }
                }
            }
        ]
    
    async def call_mcp_server(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP服务器"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.mcp_server_url,
                json={"method": method, "params": params}
            )
            return response.json()
    
    async def call_azure_openai(self, messages: List[Dict[str, str]], tools: Optional[List] = None) -> Dict[str, Any]:
        """调用Azure OpenAI服务"""
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        payload = {
            "messages": messages,
            "max_tokens": 1500,
            "temperature": 0.7
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.azure_endpoint,
                headers=headers,
                json=payload,
                timeout=60.0
            )
            return response.json()
    
    async def execute_function_call(self, function_name: str, arguments: Dict[str, Any]) -> str:
        """执行函数调用"""
        try:
            result = await self.call_mcp_server(function_name, arguments)
            
            if result.get("error"):
                return f"错误: {result['error']}"
            
            return json.dumps(result.get("result", {}), ensure_ascii=False, indent=2)
        
        except Exception as e:
            return f"执行函数时出错: {str(e)}"
    
    async def process_user_input(self, user_input: str) -> str:
        """处理用户输入并返回响应"""
        messages = [
            {
                "role": "system",
                "content": """你是一个智能的待办事项助手。你可以帮助用户管理他们的日常任务。

你具有以下功能：
1. 创建待办事项 - 用户可以添加新的任务，包括标题、内容和截止日期
2. 查看待办事项 - 显示所有任务、已完成的任务或未完成的任务
3. 更新待办事项 - 修改任务的任何信息
4. 删除待办事项 - 移除不需要的任务
5. 搜索待办事项 - 根据关键词查找任务
6. 标记完成 - 将任务标记为已完成

请根据用户的需求选择合适的功能来帮助他们。回复时要友好和有帮助。

如果用户提到日期，请使用YYYY-MM-DD格式（例如：2025-06-26）。"""
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
        
        try:
            # 调用Azure OpenAI
            response = await self.call_azure_openai(messages, self.tools)
            
            if "error" in response:
                return f"AI服务错误: {response['error']['message']}"
            
            message = response["choices"][0]["message"]
            
            # 检查是否有工具调用
            if message.get("tool_calls"):
                tool_call = message["tool_calls"][0]
                function_name = tool_call["function"]["name"]
                arguments = json.loads(tool_call["function"]["arguments"])
                
                # 执行函数调用
                function_result = await self.execute_function_call(function_name, arguments)
                
                # 将函数结果发送回AI获取最终响应
                messages.append(message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": function_result
                })
                
                final_response = await self.call_azure_openai(messages)
                return final_response["choices"][0]["message"]["content"]
            
            else:
                return message["content"]
        
        except Exception as e:
            return f"处理请求时出错: {str(e)}"
