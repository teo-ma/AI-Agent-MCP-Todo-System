import asyncio
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from ai_agent import AIAgent
import signal
import sys

console = Console()
app = typer.Typer()

class TodoApp:
    def __init__(self):
        self.agent = AIAgent()
        self.running = True
        
    def signal_handler(self, signum, frame):
        """处理Ctrl+C信号"""
        self.running = False
        console.print("\n👋 再见！感谢使用待办事项助手！", style="bold yellow")
        sys.exit(0)
    
    def display_welcome(self):
        """显示欢迎界面"""
        welcome_text = """
🤖 智能待办事项助手

我可以帮助您管理日常任务！

可用功能：
• 创建新任务 - "创建一个任务：学习Python"
• 查看所有任务 - "显示我的所有任务"
• 查看未完成任务 - "显示未完成的任务"
• 更新任务 - "修改任务1的标题为'完成项目'"
• 删除任务 - "删除任务2"
• 搜索任务 - "搜索包含'学习'的任务"
• 标记完成 - "标记任务3为已完成"

输入 'quit' 或 'exit' 退出程序
        """
        
        panel = Panel(
            welcome_text,
            title="[bold blue]待办事项管理系统[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        )
        
        console.print(panel)
        console.print()
    
    def display_thinking(self):
        """显示思考动画"""
        return Text("🤔 正在处理您的请求...", style="italic yellow")
    
    async def run_interactive(self):
        """运行交互式界面"""
        # 设置信号处理器
        signal.signal(signal.SIGINT, self.signal_handler)
        
        self.display_welcome()
        
        while self.running:
            try:
                # 获取用户输入
                user_input = Prompt.ask(
                    "[bold green]您[/bold green]",
                    default=""
                ).strip()
                
                if not user_input:
                    continue
                
                # 检查退出命令
                if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                    console.print("👋 再见！感谢使用待办事项助手！", style="bold yellow")
                    break
                
                # 显示思考状态
                with console.status("[yellow]🤔 正在处理您的请求...[/yellow]"):
                    response = await self.agent.process_user_input(user_input)
                
                # 显示AI响应
                response_panel = Panel(
                    response,
                    title="[bold cyan]🤖 助手[/bold cyan]",
                    border_style="cyan",
                    padding=(1, 2)
                )
                console.print(response_panel)
                console.print()
                
            except KeyboardInterrupt:
                self.signal_handler(None, None)
            except Exception as e:
                console.print(f"[red]发生错误: {str(e)}[/red]")
                console.print()

@app.command()
def interactive():
    """启动交互式待办事项助手"""
    todo_app = TodoApp()
    asyncio.run(todo_app.run_interactive())

@app.command()
def server():
    """启动MCP服务器"""
    import subprocess
    import os
    
    console.print("🚀 启动MCP服务器...", style="bold green")
    
    try:
        # 启动MCP服务器
        subprocess.run([
            sys.executable, "mcp_server.py"
        ], cwd=os.getcwd())
    except KeyboardInterrupt:
        console.print("\n✋ MCP服务器已停止", style="bold yellow")
    except Exception as e:
        console.print(f"[red]启动服务器时出错: {str(e)}[/red]")

@app.command()
def setup():
    """设置数据库和环境"""
    import subprocess
    
    console.print("🔧 设置待办事项应用...", style="bold blue")
    
    try:
        # 启动PostgreSQL容器
        console.print("📦 启动PostgreSQL数据库...")
        result = subprocess.run([
            "docker-compose", "up", "-d", "postgres"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print("✅ PostgreSQL数据库已启动", style="bold green")
        else:
            console.print(f"❌ 启动数据库失败: {result.stderr}", style="bold red")
            return
        
        # 等待数据库准备就绪
        console.print("⏳ 等待数据库准备就绪...")
        import time
        time.sleep(5)
        
        console.print("✅ 环境设置完成！", style="bold green")
        console.print("\n现在您可以运行以下命令：")
        console.print("• [cyan]python main.py interactive[/cyan] - 启动交互式助手")
        console.print("• [cyan]python main.py server[/cyan] - 启动MCP服务器")
        
    except Exception as e:
        console.print(f"❌ 设置过程中出错: {str(e)}", style="bold red")

if __name__ == "__main__":
    app()
