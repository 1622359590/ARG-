#!/usr/bin/env python3
from flask import Flask, request, jsonify, render_template_string
import os
import ollama
import datetime

app = Flask(__name__)

# 手动处理CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

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
            return "📝 暂无文档内容，请先在docs文件夹中添加文档文件"
        
        all_content = "\n".join([f"【{name}】\n{content}" for name, content in self.documents.items()])
        
        prompt = f"""基于以下文档内容回答问题：

{all_content}

问题：{question}

请用中文给出准确、有用的回答："""
        
        try:
            response = ollama.chat(
                model='qwen2.5:3b',
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.1}
            )
            return response['message']['content']
        except Exception as e:
            return f"❌ 系统错误: {e}"

assistant = DocumentAssistant()

# 美观的HTML模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📚 智能文档助手</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }
        
        .stats {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        
        .stat-item {
            background: rgba(255,255,255,0.2);
            padding: 10px 20px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        
        .chat-container {
            padding: 30px;
            min-height: 400px;
        }
        
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        #questionInput {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e1e5e9;
            border-radius: 15px;
            font-size: 16px;
            outline: none;
            transition: all 0.3s ease;
        }
        
        #questionInput:focus {
            border-color: #4facfe;
            box-shadow: 0 0 0 3px rgba(79, 172, 254, 0.1);
        }
        
        #askBtn {
            padding: 15px 30px;
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            border: none;
            border-radius: 15px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        #askBtn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(79, 172, 254, 0.3);
        }
        
        #askBtn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .response-area {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            min-height: 200px;
            border: 2px dashed #e1e5e9;
        }
        
        .loading {
            display: none;
            text-align: center;
            color: #6c757d;
        }
        
        .loading-spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #4facfe;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .answer-content {
            line-height: 1.6;
            color: #2c3e50;
        }
        
        .answer-content p {
            margin-bottom: 15px;
        }
        
        .history {
            margin-top: 30px;
        }
        
        .history-item {
            background: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #4facfe;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .question {
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
        }
        
        .answer {
            color: #6c757d;
        }
        
        .timestamp {
            font-size: 0.8em;
            color: #adb5bd;
            text-align: right;
            margin-top: 5px;
        }
        
        .error {
            color: #e74c3c;
            background: #ffeaea;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #e74c3c;
        }
        
        .success {
            color: #27ae60;
            background: #eafaf1;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #27ae60;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 智能文档助手</h1>
            <p>基于本地AI的智能文档问答系统</p>
            <div class="stats">
                <div class="stat-item">📄 已加载文档: <span id="docCount">{{ documents_count }}</span></div>
                <div class="stat-item">🤖 模型: Qwen2.5-3B</div>
                <div class="stat-item">⚡ 本地运行</div>
            </div>
        </div>
        
        <div class="chat-container">
            <div class="input-group">
                <input type="text" id="questionInput" placeholder="请输入关于文档的问题，例如：公司年假政策是什么？" autocomplete="off">
                <button id="askBtn" onclick="askQuestion()">发送</button>
            </div>
            
            <div class="loading" id="loading">
                <div class="loading-spinner"></div>
                <p>AI正在思考中...</p>
            </div>
            
            <div class="response-area" id="responseArea">
                <div style="text-align: center; color: #6c757d; padding: 50px 0;">
                    <div style="font-size: 3em; margin-bottom: 20px;">💭</div>
                    <p>请输入问题开始对话</p>
                </div>
            </div>
            
            <div class="history" id="historySection" style="display: none;">
                <h3 style="margin-bottom: 15px; color: #2c3e50;">📝 对话历史</h3>
                <div id="historyList"></div>
            </div>
        </div>
    </div>

    <script>
        let conversationHistory = [];
        
        function askQuestion() {
            const questionInput = document.getElementById('questionInput');
            const askBtn = document.getElementById('askBtn');
            const loading = document.getElementById('loading');
            const responseArea = document.getElementById('responseArea');
            const question = questionInput.value.trim();
            
            if (!question) {
                showMessage('请输入问题', 'error');
                return;
            }
            
            // 禁用按钮，显示加载
            askBtn.disabled = true;
            loading.style.display = 'block';
            responseArea.innerHTML = '';
            
            // 调用API
            fetch('/ask?q=' + encodeURIComponent(question))
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        showMessage(data.error, 'error');
                    } else {
                        displayAnswer(question, data.answer);
                        addToHistory(question, data.answer);
                    }
                })
                .catch(error => {
                    showMessage('网络错误: ' + error, 'error');
                })
                .finally(() => {
                    askBtn.disabled = false;
                    loading.style.display = 'none';
                    questionInput.value = '';
                    questionInput.focus();
                });
        }
        
        function displayAnswer(question, answer) {
            const responseArea = document.getElementById('responseArea');
            responseArea.innerHTML = `
                <div style="margin-bottom: 20px;">
                    <div class="question">🙋 你的问题: ${question}</div>
                </div>
                <div class="answer-content">
                    <div style="color: #4facfe; font-weight: 600; margin-bottom: 10px;">🤖 助手回答:</div>
                    <div>${formatAnswer(answer)}</div>
                </div>
            `;
        }
        
        function formatAnswer(answer) {
            // 简单的格式处理
            return answer.replace(/\\n/g, '<br>')
                        .replace(/(\\d+)\\./g, '<br>$1.')
                        .replace(/^\\s*<br>/, '');
        }
        
        function showMessage(message, type) {
            const responseArea = document.getElementById('responseArea');
            responseArea.innerHTML = `<div class="${type}">${message}</div>`;
        }
        
        function addToHistory(question, answer) {
            const historyItem = {
                question: question,
                answer: answer,
                timestamp: new Date().toLocaleTimeString()
            };
            
            conversationHistory.unshift(historyItem);
            updateHistoryDisplay();
        }
        
        function updateHistoryDisplay() {
            const historySection = document.getElementById('historySection');
            const historyList = document.getElementById('historyList');
            
            if (conversationHistory.length > 0) {
                historySection.style.display = 'block';
                historyList.innerHTML = conversationHistory.map(item => `
                    <div class="history-item">
                        <div class="question">${item.question}</div>
                        <div class="answer">${item.answer.substring(0, 100)}${item.answer.length > 100 ? '...' : ''}</div>
                        <div class="timestamp">${item.timestamp}</div>
                    </div>
                `).join('');
            }
        }
        
        // 支持回车键发送
        document.getElementById('questionInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                askQuestion();
            }
        });
        
        // 页面加载完成后自动聚焦输入框
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('questionInput').focus();
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    """首页"""
    return render_template_string(HTML_TEMPLATE, documents_count=len(assistant.documents))

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'running', 
        'service': '智能文档助手',
        'documents_loaded': len(assistant.documents),
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.route('/ask', methods=['POST', 'GET', 'OPTIONS'])
def ask_endpoint():
    """问答接口"""
    if request.method == 'OPTIONS':
        return '', 200
    
    if request.method == 'GET':
        question = request.args.get('q', '')
    else:
        data = request.get_json(silent=True) or {}
        question = data.get('question', '')
    
    if not question:
        return jsonify({'error': '请提供问题'}), 400
    
    print(f"🤔 收到问题: {question}")
    answer = assistant.ask_question(question)
    print(f"📖 生成回答: {answer[:100]}...")
    
    return jsonify({
        'question': question, 
        'answer': answer,
        'documents_count': len(assistant.documents),
        'timestamp': datetime.datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🎨 启动美观版文档助手API服务...")
    print("🌟 访问地址: http://localhost:8886")
    print("📊 健康检查: http://localhost:8886/health")
    print("💫 界面特性: 渐变背景、动画效果、对话历史")
    
    app.run(
        host='0.0.0.0',
        port=8886, 
        debug=False,
        threaded=True
    )