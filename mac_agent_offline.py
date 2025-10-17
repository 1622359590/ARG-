#!/usr/bin/env python3
import os
import ollama

print("🤖 超级简单版 - 先测试基础功能")

def simple_chat():
    print("💬 基础聊天模式（输入'退出'结束）")
    
    while True:
        question = input("\n你的问题: ").strip()
        
        if question.lower() in ['退出', 'quit', 'exit']:
            break
            
        try:
            response = ollama.chat(
                model='qwen2.5:3b',
                messages=[{'role': 'user', 'content': question}]
            )
            print("回答:", response['message']['content'])
        except Exception as e:
            print("错误:", e)

if __name__ == "__main__":
    simple_chat()
