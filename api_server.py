#!/usr/bin/env python3
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  # 解决跨域问题
import os
import ollama

app = Flask(__name__)
CORS(app)  # 启用跨域支持

class DocumentAssistant:
    def __init__(self):
        self.documents = {}
        self.load_documents()
    
    def load_documents(self):
        """加载文档"""
        docs_folder = "./docs"
        if os.path.exists(docs_folder):
            for filename in os.listdir(docs_folder):
                if filename.endswith(('.txt', '.md')):
                    try:
                        with open(os.path.join(docs_folder, filename), 'r', encoding='utf-8') as f:
                            self.documents[filename] = f.read()
                        print(f"✅ 已加载: {filename}")
                    except Exception as e:
                        print(f"❌ 加载失败 {filename}: {e}")
        print(f"📚 总共加载 {len(self.documents)} 个文档")
    
    def ask_question(self, question):
        """回答问题"""
        if not self.documents:
            return "暂无文档内容，请先在docs文件夹中添加文档"
        
        all_content = "\n".join([f"【{name}】\n{content}" for name, content in self.documents.items()])
        
        prompt = f"""基于以下文档内容回答问题：

{all_content}

问题：{question}

请用中文回答："""
        
        try:
            response = ollama.chat(
                model='qwen2.5:3b',
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.1}
            )
            return response['message']['content']
        except Exception as e:
            return f"错误: {e}"

assistant = DocumentAssistant()

@app.route('/')
def home():
    """首页"""
    return """
    <html>
        <body>
            <h1>📚 文档助手API服务</h1>
            <p>服务正常运行中！</p>
            <p>使用方式：</p>
            <ul>
                <li>GET <a href="/health">/health</a> - 健康检查</li>
                <li>POST /ask - 提问接口</li>
            </ul>
        </body>
    </html>
    """

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'running', 
        'service': 'Document Assistant API',
        'documents_loaded': len(assistant.documents)
    })

@app.route('/ask', methods=['POST', 'GET'])  # 同时支持GET和POST
def ask_endpoint():
    """问答接口"""
    if request.method == 'GET':
        # GET请求，从URL参数获取问题
        question = request.args.get('q', '')
        if not question:
            return jsonify({'error': '请使用参数 q 提供问题，例如: /ask?q=公司年假政策'})
    else:
        # POST请求，从JSON获取问题
        data = request.get_json(silent=True) or {}
        question = data.get('question', '')
    
    if not question:
        return jsonify({'error': '请提供问题'}), 400
    
    print(f"收到问题: {question}")
    answer = assistant.ask_question(question)
    
    return jsonify({
        'question': question, 
        'answer': answer,
        'documents_count': len(assistant.documents)
    })

if __name__ == '__main__':
    print("🚀 启动文档助手API服务...")
    print("📚 访问地址: http://localhost:8808")
    print("🔧 健康检查: http://localhost:8808/health")
    print("❓ 提问示例: http://localhost:8808/ask?q=公司年假政策")
    
    # 关键配置：关闭调试模式，允许外部访问
    app.run(
        host='0.0.0.0',  # 允许所有IP访问
        port=8808, 
        debug=False,     # 生产环境关闭debug
        threaded=True    # 启用多线程
    )
