#!/usr/bin/env python3
import os
import ollama
import glob

class AccurateDocumentAssistant:
    def __init__(self, model_name="qwen2.5:3b"):
        self.model_name = model_name
        self.documents = {}
        print("🎯 精确版文档助手初始化完成")
    
    def load_documents(self, folder_path="./docs"):
        """加载文件夹中的所有文档"""
        if not os.path.exists(folder_path):
            print(f"📁 创建文档文件夹: {folder_path}")
            os.makedirs(folder_path)
            print(f"请将文档放入 {folder_path} 文件夹后重新运行")
            return False
        
        file_patterns = ["*.txt", "*.md"]
        doc_files = []
        for pattern in file_patterns:
            doc_files.extend(glob.glob(os.path.join(folder_path, pattern)))
        
        if not doc_files:
            print("📝 未找到文档文件")
            return False
        
        print(f"找到 {len(doc_files)} 个文档文件:")
        
        for file_path in doc_files:
            filename = os.path.basename(file_path)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if content and len(content.strip()) > 5:
                    self.documents[filename] = content
                    print(f"✅ 已加载: {filename}")
                    
            except Exception as e:
                print(f"❌ 加载失败 {filename}: {e}")
        
        if self.documents:
            print(f"🎉 成功加载 {len(self.documents)} 个文档")
            return True
        return False
    
    def ask_question(self, question):
        """精确回答问题 - 避免错误推断"""
        all_docs_content = "\n\n".join([
            f"【{filename}】\n{content}" 
            for filename, content in self.documents.items()
        ])
        
        # 更严格的提示词，避免错误推断
        prompt = f"""你是一个精确的文档分析助手。以下是完整的文档内容：

{all_docs_content}

用户问题：{question}

重要规则：
1. 只能基于文档中明确写出的信息回答
2. 不能对用户的个人情况做任何假设或推断
3. 如果文档中没有用户的个人信息，要明确说明
4. 只能描述文档中的政策规定，不能判断用户是否符合条件
5. 引用信息时要准确，不能修改数字或细节

请基于文档内容给出精确回答："""
        
        print("🤔 正在精确分析文档...")
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.1, "num_predict": 800}
            )
            return response['message']['content']
        except Exception as e:
            return f"出错: {e}"
    
    def chat(self):
        """开始对话"""
        print("\n" + "="*60)
        print("🤖 精确版文档助手已就绪！")
        print("💬 可以询问文档相关问题")
        print("输入 '退出' 结束对话")
        print("="*60)
        
        while True:
            try:
                question = input("\n🙋 你的问题: ").strip()
                
                if question.lower() in ['退出', 'quit', 'exit']:
                    print("👋 再见！")
                    break
                
                if not question:
                    continue
                
                answer = self.ask_question(question)
                print(f"\n🎯 助手: {answer}")
                
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")

def main():
    assistant = AccurateDocumentAssistant(model_name="qwen2.5:3b")
    
    if assistant.load_documents():
        assistant.chat()
    else:
        print("请在 docs/ 文件夹中放入文档文件")

if __name__ == "__main__":
    main()