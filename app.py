# app.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from utilities.simple_rag import simple_rag_call
from dotenv import load_dotenv
import io

load_dotenv()
app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def serve_frontend():
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>RAG Chat</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            height: 100vh;
            background-color: #f0f2f5;
        }
        .chat-container {
            flex-grow: 1;
            overflow-y: auto;
            padding: 20px;
        }
        .message {
            max-width: 80%;
            margin: 10px 0;
            padding: 10px;
            border-radius: 10px;
            clear: both;
        }
        .human-message {
            background-color: #007bff;
            color: white;
            float: right;
            text-align: right;
        }
        .ai-message {
            background-color: #e9ecef;
            color: black;
            float: left;
            text-align: left;
        }
        .input-area {
            display: flex;
            padding: 10px;
            background-color: white;
            border-top: 1px solid #ddd;
        }
        #query-input {
            flex-grow: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        #send-btn {
            padding: 10px 15px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            margin-left: 10px;
        }
        #clear-btn {
            padding: 10px 15px;
            background-color: #dc3545;
            color: white;
            border: none;
            border-radius: 4px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <button id="clear-btn">Clear Chat</button>
    <div class="chat-container" id="chat-container"></div>
    <div class="input-area">
        <input type="text" id="query-input" placeholder="Ask a question...">
        <button id="send-btn">Send</button>
    </div>

    <script>
        const queryInput = document.getElementById('query-input');
        const sendBtn = document.getElementById('send-btn');
        const chatContainer = document.getElementById('chat-container');
        const clearBtn = document.getElementById('clear-btn');
        let sessionId = null;

        sendBtn.addEventListener('click', sendMessage);
        queryInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
        clearBtn.addEventListener('click', clearChat);

        function sendMessage() {
    const query = queryInput.value.trim();
    if (!query) return;

    // Add human message
    addMessage(query, 'human');
    queryInput.value = '';

    // Send to backend
    fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query,
            session_id: sessionId
        }),
    })
    .then(response => response.json())
    .then(data => {
        // Update session ID if not set
        if (!sessionId) sessionId = data.session_id;

        // Clear previous messages
        chatContainer.innerHTML = '';

        // Display last 5 chats from history
        const lastFiveChats = data.chat_history.slice(-10); // 10 because it includes both human and AI messages
        lastFiveChats.forEach(message => {
            if (message.role !== 'system') {
                addMessage(message.content, message.role);
            }
        });

        // Add current AI response
        addMessage(data.response, 'ai');
    })
    .catch(error => {
        console.error('Error:', error);
        addMessage('Sorry, there was an error.', 'ai');
    });
}

        function addMessage(content, role) {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message', `${role}-message`);
            messageDiv.textContent = content;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function clearChat() {
            chatContainer.innerHTML = '';
            sessionId = null;
        }
    </script>
</body>
</html>
    '''

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        session_id = data.get('session_id', None)  # Optional session_id
        
        response, chat_history, new_session_id = simple_rag_call(query, session_id)
        
        return jsonify({
            'response': response,
            'session_id': new_session_id,
            'chat_history': [
                {
                    'role': message.type,
                    'content': message.content
                } for message in chat_history
            ]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)