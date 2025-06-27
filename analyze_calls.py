#!/usr/bin/env python3
"""
可视化Python调用关系分析工具
"""

import os
import ast
import json
from pathlib import Path

class CallGraphAnalyzer:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.call_graph = {}
        self.imports = {}
        
    def analyze_file(self, file_path: Path):
        """分析单个Python文件的调用关系"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            
            file_name = file_path.name
            self.call_graph[file_name] = {
                'imports': [],
                'classes': [],
                'functions': [],
                'calls': []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.call_graph[file_name]['imports'].append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        import_name = f"{module}.{alias.name}" if module else alias.name
                        self.call_graph[file_name]['imports'].append(import_name)
                
                elif isinstance(node, ast.ClassDef):
                    self.call_graph[file_name]['classes'].append(node.name)
                
                elif isinstance(node, ast.FunctionDef):
                    self.call_graph[file_name]['functions'].append(node.name)
                
                elif isinstance(node, ast.Call):
                    if hasattr(node.func, 'id'):
                        self.call_graph[file_name]['calls'].append(node.func.id)
                    elif hasattr(node.func, 'attr'):
                        if hasattr(node.func, 'value') and hasattr(node.func.value, 'id'):
                            call_name = f"{node.func.value.id}.{node.func.attr}"
                            self.call_graph[file_name]['calls'].append(call_name)
        
        except Exception as e:
            print(f"分析文件 {file_path} 时出错: {e}")
    
    def analyze_project(self):
        """分析整个项目"""
        python_files = list(self.project_path.glob("*.py"))
        
        for file_path in python_files:
            if file_path.name.startswith('.'):
                continue
            self.analyze_file(file_path)
    
    def print_call_graph(self):
        """打印调用关系图"""
        print("🐍 Python 文件调用关系分析")
        print("=" * 60)
        
        for file_name, info in self.call_graph.items():
            print(f"\n📄 {file_name}")
            print("-" * 40)
            
            if info['imports']:
                print("📦 导入模块:")
                for imp in info['imports']:
                    # 识别项目内部导入
                    if any(imp.startswith(f.stem) for f in self.project_path.glob("*.py")):
                        print(f"   🔗 {imp} (项目内部)")
                    else:
                        print(f"   📋 {imp} (外部库)")
            
            if info['classes']:
                print("🏗️ 定义的类:")
                for cls in info['classes']:
                    print(f"   📝 {cls}")
            
            if info['functions']:
                print("⚙️ 定义的函数:")
                for func in info['functions'][:5]:  # 只显示前5个
                    print(f"   🔧 {func}")
                if len(info['functions']) > 5:
                    print(f"   ... 还有 {len(info['functions']) - 5} 个函数")
    
    def generate_mermaid_diagram(self):
        """生成Mermaid流程图"""
        print("\n🎨 Mermaid 调用关系图")
        print("=" * 60)
        print("```mermaid")
        print("graph TD")
        
        # 定义节点
        for file_name, info in self.call_graph.items():
            clean_name = file_name.replace('.py', '').replace('-', '_')
            if info['classes']:
                print(f"    {clean_name}[{file_name}<br/>📋 {', '.join(info['classes'][:2])}]")
            else:
                print(f"    {clean_name}[{file_name}]")
        
        print()
        
        # 定义关系
        for file_name, info in self.call_graph.items():
            clean_name = file_name.replace('.py', '').replace('-', '_')
            for imp in info['imports']:
                # 检查是否是项目内部导入
                for other_file in self.call_graph.keys():
                    if imp.startswith(other_file.replace('.py', '')):
                        other_clean = other_file.replace('.py', '').replace('-', '_')
                        print(f"    {clean_name} --> {other_clean}")
        
        print("```")
    
    def print_dependency_summary(self):
        """打印依赖关系总结"""
        print("\n📊 依赖关系总结")
        print("=" * 60)
        
        # 统计外部依赖
        external_deps = set()
        internal_deps = {}
        
        for file_name, info in self.call_graph.items():
            internal_deps[file_name] = []
            for imp in info['imports']:
                # 检查是否是项目内部导入
                is_internal = False
                for other_file in self.call_graph.keys():
                    if imp.startswith(other_file.replace('.py', '')):
                        internal_deps[file_name].append(other_file)
                        is_internal = True
                        break
                
                if not is_internal and not imp.startswith('.'):
                    # 提取顶级模块名
                    top_level = imp.split('.')[0]
                    external_deps.add(top_level)
        
        print("🌐 外部依赖库:")
        for dep in sorted(external_deps):
            if dep in ['fastapi', 'uvicorn']:
                print(f"   🌐 {dep} (Web框架)")
            elif dep in ['psycopg2', 'sqlalchemy']:
                print(f"   🗄️ {dep} (数据库)")
            elif dep in ['pydantic']:
                print(f"   ✅ {dep} (数据验证)")
            elif dep in ['httpx', 'requests']:
                print(f"   🔗 {dep} (HTTP客户端)")
            elif dep in ['rich', 'typer']:
                print(f"   🎨 {dep} (CLI界面)")
            elif dep in ['asyncio', 'json', 'os', 'sys']:
                print(f"   🐍 {dep} (Python内置)")
            else:
                print(f"   📦 {dep}")
        
        print("\n🔗 内部文件依赖:")
        for file_name, deps in internal_deps.items():
            if deps:
                deps_str = " → ".join(deps)
                print(f"   📄 {file_name} → {deps_str}")

def main():
    analyzer = CallGraphAnalyzer("/Users/tema/projects/MCP-test-py")
    analyzer.analyze_project()
    analyzer.print_call_graph()
    analyzer.generate_mermaid_diagram()
    analyzer.print_dependency_summary()

if __name__ == "__main__":
    main()
