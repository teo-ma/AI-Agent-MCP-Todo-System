#!/usr/bin/env python3
"""
测试不同的Function选择机制
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agent import AIAgent
from enhanced_ai_agent import EnhancedAIAgent

async def test_function_selection():
    """测试不同的function选择方法"""
    
    # 创建两个代理实例
    original_agent = AIAgent()
    enhanced_agent = EnhancedAIAgent()
    
    # 测试用例
    test_cases = [
        "创建一个任务：学习Python编程",
        "显示我的所有任务",
        "搜索包含'学习'的任务",
        "标记任务1为已完成",
        "修改任务2的标题",
        "删除任务3",
        "查看未完成的任务",
        "我要做一个新任务叫'买菜'",
        "找一下关于项目的任务",
        "任务5完成了"
    ]
    
    print("🧪 Function选择机制测试")
    print("=" * 60)
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n📝 测试案例 {i}: {test_input}")
        print("-" * 40)
        
        # 1. 增强版本：使用意图分析
        print("🔍 方法1：意图分析 + 参数提取")
        predicted_intent = enhanced_agent.analyze_user_intent(test_input)
        if predicted_intent:
            params = enhanced_agent.extract_parameters(test_input, predicted_intent)
            print(f"   预测意图: {predicted_intent}")
            print(f"   提取参数: {params}")
        else:
            print("   无法确定意图，将使用AI模型")
        
        # 2. 原始版本：纯AI决策
        print("\n🤖 方法2：纯AI模型决策")
        print("   将用户输入和工具定义发送给GPT-4.1进行智能选择")
        
        print()

def demonstrate_intent_patterns():
    """演示意图模式匹配"""
    enhanced_agent = EnhancedAIAgent()
    
    print("\n🎯 意图模式匹配演示")
    print("=" * 60)
    
    # 展示每个意图的模式
    for intent, patterns in enhanced_agent.intent_patterns.items():
        print(f"\n📋 {intent}:")
        for pattern in patterns:
            print(f"   • {pattern}")
    
    print("\n🔑 关键词匹配演示")
    print("=" * 60)
    
    for tool in enhanced_agent.tools:
        function_name = tool["function"]["name"]
        keywords = tool["function"].get("keywords", [])
        print(f"\n📋 {function_name}:")
        print(f"   关键词: {', '.join(keywords)}")

if __name__ == "__main__":
    print("🚀 启动Function选择机制测试")
    
    # 演示意图模式
    demonstrate_intent_patterns()
    
    # 测试function选择
    asyncio.run(test_function_selection())
    
    print("\n" + "=" * 60)
    print("📊 总结：")
    print("方法1 (意图分析)：")
    print("  ✅ 快速响应，不需要调用AI模型")
    print("  ✅ 可离线工作")
    print("  ✅ 完全可控的逻辑")
    print("  ❌ 需要手动维护规则")
    print("  ❌ 可能无法处理复杂的自然语言")
    
    print("\n方法2 (纯AI决策)：")
    print("  ✅ 自然语言理解能力强")
    print("  ✅ 能处理复杂的用户输入")
    print("  ✅ 不需要预定义规则")
    print("  ❌ 需要调用外部AI服务")
    print("  ❌ 响应时间较长")
    print("  ❌ 依赖网络连接")
    
    print("\n💡 建议：结合使用两种方法，先尝试意图分析，失败时回退到AI模型！")
