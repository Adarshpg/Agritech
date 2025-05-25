import os
import random
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Sample chatbot responses
responses = {
    'fertilizer': 'For most plants, a balanced NPK (Nitrogen, Phosphorus, Potassium) fertilizer works well. Apply fertilizer during the growing season according to package instructions.',
    'watering': 'Most plants need consistent watering. Water when the top inch of soil feels dry. Avoid overwatering as it can lead to root rot.',
    'pests': 'Common garden pests include aphids, spider mites, and caterpillars. You can use neem oil or insecticidal soap as organic solutions.',
    'soil': 'Good soil is crucial for plant health. Most plants prefer well-draining soil rich in organic matter.',
    'corn': 'Corn (Zea mays) is a cereal crop that needs full sun and regular watering. Plant in well-draining soil after the last frost. Corn requires high nitrogen fertilizer for optimal growth.',
    'tomato': 'Tomatoes need full sun and consistent watering. They benefit from support structures like cages or stakes. Feed with balanced fertilizer and watch for pests like hornworms.',
    'rice': 'Rice is a grain crop that thrives in flooded conditions. It requires warm temperatures and high humidity. Rice is a staple food for more than half the world\'s population.',
    'wheat': 'Wheat is a cereal grain that prefers cool, dry conditions. It\'s one of the world\'s most important food crops and is used to make flour for bread, pasta, and other foods.',
    'default': 'I\'m your agriculture assistant. You can ask me about plant care, fertilizers, pest control, and more!'
}

# HTML Template
CHATBOT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agriculture Chatbot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            text-align: center;
            margin-bottom: 40px;
        }
        h1 {
            color: #388E3C;
        }
        .chat-container {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
            padding: 20px;
            height: 500px;
            display: flex;
            flex-direction: column;
        }
        .chat-messages {
            flex-grow: 1;
            overflow-y: auto;
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background-color: #f9f9f9;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 18px;
            max-width: 70%;
            word-wrap: break-word;
        }
        .user-message {
            background-color: #E8F5E9;
            color: #263238;
            margin-left: auto;
            border: 1px solid #C8E6C9;
        }
        .bot-message {
            background-color: #F5F5F5;
            color: #263238;
            border: 1px solid #E0E0E0;
        }
        .chat-input {
            display: flex;
            gap: 10px;
        }
        .chat-input input {
            flex-grow: 1;
            padding: 12px;
            border: 1px solid #BDBDBD;
            border-radius: 24px;
            font-size: 16px;
            outline: none;
        }
        .chat-input button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 24px;
            cursor: pointer;
        }
        .loading {
            display: inline-block;
            margin-left: 10px;
        }
        .dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #888;
            margin-right: 3px;
            animation: wave 1.3s linear infinite;
        }
        .dot:nth-child(2) {
            animation-delay: -1.1s;
        }
        .dot:nth-child(3) {
            animation-delay: -0.9s;
        }
        @keyframes wave {
            0%, 60%, 100% { transform: initial; }
            30% { transform: translateY(-10px); }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Agriculture Chatbot</h1>
            <p>Get answers to your agriculture-related questions</p>
        </header>
        
        <div class="chat-container">
            <div class="chat-messages" id="chatMessages">
                <div class="message bot-message">
                    Hello! I'm your agriculture assistant. How can I help you today? You can ask me about plant care, fertilizers, pest control, and more!
                </div>
            </div>
            
            <div class="chat-input">
                <input type="text" id="userInput" placeholder="Type your question here..." autocomplete="off">
                <button id="sendBtn">Send</button>
            </div>
        </div>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const chatMessages = document.getElementById('chatMessages');
            const userInput = document.getElementById('userInput');
            const sendBtn = document.getElementById('sendBtn');
            
            function addMessage(text, sender) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}-message`;
                messageDiv.textContent = text;
                
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            function addLoadingIndicator() {
                const loadingDiv = document.createElement('div');
                loadingDiv.className = 'message bot-message';
                loadingDiv.id = 'loadingIndicator';
                
                const loadingText = document.createElement('span');
                loadingText.textContent = 'Thinking';
                
                const loadingDots = document.createElement('span');
                loadingDots.className = 'loading';
                
                for (let i = 0; i < 3; i++) {
                    const dot = document.createElement('span');
                    dot.className = 'dot';
                    loadingDots.appendChild(dot);
                }
                
                loadingDiv.appendChild(loadingText);
                loadingDiv.appendChild(loadingDots);
                
                chatMessages.appendChild(loadingDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            function removeLoadingIndicator() {
                const loadingDiv = document.getElementById('loadingIndicator');
                if (loadingDiv) {
                    loadingDiv.remove();
                }
            }
            
            function sendMessage() {
                const message = userInput.value.trim();
                if (message === '') return;
                
                // Add user message to chat
                addMessage(message, 'user');
                
                // Clear input
                userInput.value = '';
                
                // Show loading indicator
                addLoadingIndicator();
                
                // Send message to server
                fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message: message })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    // Remove loading indicator
                    removeLoadingIndicator();
                    
                    // Add bot response
                    addMessage(data.response, 'bot');
                })
                .catch(error => {
                    console.error('Error:', error);
                    
                    // Remove loading indicator
                    removeLoadingIndicator();
                    
                    // Add error message
                    addMessage('Sorry, I\'m having trouble processing your request. Please try again.', 'bot');
                });
            }
            
            // Add event listeners
            sendBtn.addEventListener('click', sendMessage);
            
            userInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(CHATBOT_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Get the message from the request
        data = request.get_json()
        message = data.get('message', '').lower()
        
        # Log the received message
        print(f"Received message: {message}")
        
        # Find a response based on keywords
        response = responses['default']
        for keyword, answer in responses.items():
            if keyword in message and keyword != 'default':
                response = answer
                break
        
        # Log the response being sent
        print(f"Sending response: {response}")
        
        # Return the response as JSON
        return jsonify({'response': response})
    except Exception as e:
        # Log any errors
        print(f"Error processing request: {str(e)}")
        return jsonify({'response': 'Sorry, I encountered an error processing your request.'}), 500

if __name__ == '__main__':
    print("Starting Agriculture Chatbot on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=False)
