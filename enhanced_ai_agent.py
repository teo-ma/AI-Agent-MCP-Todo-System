import httpx
import json
import os
import re
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class EnhancedAIAgent:
    def __init__(self):
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.mcp_server_url = f"http://localhost:{os.getenv('MCP_SERVER_PORT', 8000)}/mcp"
        
        # 扩展的工具定义，包含更详细的描述和关键词
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "create_todo",
                    "description": "创建新的待办事项。关键词：创建、添加、新建、新增、建立、制作",
                    "keywords": ["创建", "添加", "新建", "新增", "建立", "制作", "做", "任务"],
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
                    "description": "获取待办事项列表。关键词：显示、查看、列表、所有、全部、未完成、已完成",
                    "keywords": ["显示", "查看", "列表", "所有", "全部", "未完成", "已完成", "任务"],
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
                    "description": "更新待办事项。关键词：修改、更新、编辑、改变、调整",
                    "keywords": ["修改", "更新", "编辑", "改变", "调整", "改", "换"],
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
                    "description": "删除待办事项。关键词：删除、移除、清除、去掉、取消",
                    "keywords": ["删除", "移除", "清除", "去掉", "取消", "删", "除"],
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
                    "description": "搜索待办事项。关键词：搜索、查找、寻找、找",
                    "keywords": ["搜索", "查找", "寻找", "找", "搜", "包含"],
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
                    "description": "标记待办事项为已完成。关键词：完成、标记、完成了、做完",
                    "keywords": ["完成", "标记", "完成了", "做完", "finished", "done"],
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
        
        # 意图模式匹配
        self.intent_patterns = {
            "create_todo": [
                r"创建.*任务",
                r"添加.*待办",
                r"新建.*事项",
                r"做.*任务",
                r"我要.*做",
                r"需要.*完成"
            ],
            "get_todos": [
                r"显示.*任务",
                r"查看.*列表",
                r"所有.*待办",
                r"我的.*任务",
                r"未完成.*",
                r"已完成.*"
            ],
            "search_todos": [
                r"搜索.*",
                r"查找.*",
                r"包含.*的任务",
                r"找.*相关"
            ],
            "update_todo": [
                r"修改.*任务",
                r"更新.*",
                r"改.*标题",
                r"调整.*"
            ],
            "delete_todo": [
                r"删除.*任务",
                r"移除.*",
                r"取消.*"
            ],
            "mark_completed": [
                r"完成.*任务",
                r"标记.*完成",
                r"做完.*",
                r".*完成了"
            ]
        }
    
    def analyze_user_intent(self, user_input: str) -> Optional[str]:
        """
        分析用户意图，返回最可能的功能名称
        """
        user_input_lower = user_input.lower()
        
        # 1. 基于正则表达式的模式匹配
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input, re.IGNORECASE):
                    return intent
        
        # 2. 基于关键词匹配
        intent_scores = {}
        for tool in self.tools:
            function_name = tool["function"]["name"]
            keywords = tool["function"].get("keywords", [])
            score = 0
            
            for keyword in keywords:
                if keyword in user_input_lower:
                    score += 1
            
            if score > 0:
                intent_scores[function_name] = score
        
        # 返回得分最高的意图
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        
        return None
    
    def extract_parameters(self, user_input: str, function_name: str) -> Dict[str, Any]:
        """
        从用户输入中提取参数
        """
        params = {}
        
        if function_name == "create_todo":
            # 提取标题
            title_patterns = [
                r"创建.*?[：:\"'](.*?)[\"']",
                r"添加.*?[：:\"'](.*?)[\"']",
                r"任务[：:\"'](.*?)[\"']",
                r"做.*?[：:\"'](.*?)[\"']"
            ]
            
            for pattern in title_patterns:
                match = re.search(pattern, user_input)
                if match:
                    params["title"] = match.group(1).strip()
                    break
            
            # 如果没有引号，尝试提取整个描述
            if "title" not in params:
                # 简单的启发式方法
                if "创建" in user_input:
                    title_start = user_input.find("创建") + 2
                    title = user_input[title_start:].strip()
                    if title:
                        params["title"] = title
            
            # 提取日期
            date_pattern = r"(\d{4}-\d{2}-\d{2})"
            date_match = re.search(date_pattern, user_input)
            if date_match:
                params["due_date"] = date_match.group(1)
        
        elif function_name == "get_todos":
            if "未完成" in user_input:
                params["completed"] = False
            elif "已完成" in user_input:
                params["completed"] = True
        
        elif function_name == "search_todos":
            # 提取搜索关键词
            search_patterns = [
                r"搜索[：:\"\']?(.*?)[\"\']*",
                r"查找[：:\"\']?(.*?)[\"\']*",
                r"包含[：:\"\']?(.*?)[\"\']*的"
            ]
            
            for pattern in search_patterns:
                match = re.search(pattern, user_input)
                if match:
                    query = match.group(1).strip()
                    if query:
                        params["query"] = query
                        break
        
        elif function_name in ["update_todo", "delete_todo", "mark_completed"]:
            # 提取ID
            id_patterns = [
                r"任务(\d+)",
                r"ID(\d+)",
                r"编号(\d+)",
                r"第(\d+)个"
            ]
            
            for pattern in id_patterns:
                match = re.search(pattern, user_input)
                if match:
                    params["id"] = int(match.group(1))
                    break
        
        return params
    
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
    
    async def process_user_input_with_intent_analysis(self, user_input: str) -> str:
        """
        使用意图分析处理用户输入
        """
        # 1. 分析用户意图
        predicted_intent = self.analyze_user_intent(user_input)
        
        if predicted_intent:
            # 2. 提取参数
            params = self.extract_parameters(user_input, predicted_intent)
            
            # 3. 验证必需参数
            tool = next((t for t in self.tools if t["function"]["name"] == predicted_intent), None)
            if tool:
                required_params = tool["function"]["parameters"].get("required", [])
                missing_params = [p for p in required_params if p not in params]
                
                if missing_params:
                    return f"缺少必需参数：{', '.join(missing_params)}。请提供更多信息。"
            
            # 4. 执行函数
            try:
                result = await self.execute_function_call(predicted_intent, params)
                return f"预测意图: {predicted_intent}\n提取参数: {params}\n\n执行结果:\n{result}"
            except Exception as e:
                return f"执行时出错: {str(e)}"
        
        # 如果无法确定意图，回退到AI模型决策
        return await self.process_user_input_with_ai(user_input)
    
    async def process_user_input_with_ai(self, user_input: str) -> str:
        """
        使用AI模型处理用户输入（原始方法）
        """
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
    
    async def process_user_input(self, user_input: str, use_intent_analysis: bool = True) -> str:
        """
        处理用户输入的主方法
        
        Args:
            user_input: 用户输入的文本
            use_intent_analysis: 是否使用意图分析（True）还是完全依赖AI模型（False）
        """
        if use_intent_analysis:
            return await self.process_user_input_with_intent_analysis(user_input)
        else:
            return await self.process_user_input_with_ai(user_input)
