from flask import Flask, render_template_string, request, jsonify, redirect
import random
import os

app = Flask(__name__)

# Sample plant data for demonstration
sample_plants = [
    {
        'Scientific Name': 'Ficus benjamina',
        'Common Name': 'Weeping Fig',
        'Plant Type': 'Tree',
        'Lifetime': 'Perennial',
        'Watering': 'Medium',
        'Sunlight': 'Partial',
        'Soil Type': 'Well-drained',
        'Growth Rate': 'Moderate',
        'Maintenance': '500',
        'Planting Cost': '1200',
        'Fertilizer Cost': '300'
    },
    {
        'Scientific Name': 'Ocimum basilicum',
        'Common Name': 'Sweet Basil',
        'Plant Type': 'Herb',
        'Lifetime': 'Annual',
        'Watering': 'Regular',
        'Sunlight': 'Full',
        'Soil Type': 'Rich, moist',
        'Growth Rate': 'Fast',
        'Maintenance': '200',
        'Planting Cost': '150',
        'Fertilizer Cost': '100'
    },
    {
        'Scientific Name': 'Aloe vera',
        'Common Name': 'Aloe',
        'Plant Type': 'Succulent',
        'Lifetime': 'Perennial',
        'Watering': 'Low',
        'Sunlight': 'Full to partial',
        'Soil Type': 'Sandy, well-drained',
        'Growth Rate': 'Slow',
        'Maintenance': '100',
        'Planting Cost': '250',
        'Fertilizer Cost': '50'
    }
]

# Sample chatbot responses
sample_responses = {
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

# HTML Templates
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Agritech Hub</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #4CAF50;
            text-align: center;
        }
        .options {
            display: flex;
            justify-content: space-around;
            margin-top: 40px;
        }
        .option {
            text-align: center;
            padding: 20px;
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            cursor: pointer;
            width: 40%;
        }
        .option:hover {
            background-color: #388E3C;
        }
        a {
            text-decoration: none;
            color: inherit;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Agritech Hub</h1>
        <p style="text-align: center;">Your one-stop solution for agricultural technology</p>
        
        <div class="options">
            <a href="/plant_identification" style="width: 40%;">
                <div class="option">
                    <h2>Plant Species Identification</h2>
                    <p>Identify plant species from images</p>
                </div>
            </a>
            
            <a href="/chatbot" style="width: 40%;">
                <div class="option">
                    <h2>Agriculture Chatbot</h2>
                    <p>Get answers to your agriculture questions</p>
                </div>
            </a>
        </div>
    </div>
</body>
</html>
'''

PLANT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plant Species Identification</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 1000px;
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
        .upload-section {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
        }
        .upload-box {
            border: 2px dashed #81C784;
            border-radius: 12px;
            padding: 30px;
            margin: 30px 0;
            cursor: pointer;
        }
        #imagePreview {
            max-width: 300px;
            max-height: 300px;
            margin: 20px auto;
            display: none;
            border-radius: 12px;
        }
        .button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 12px;
            cursor: pointer;
        }
        .button:disabled {
            background-color: #607D8B;
            cursor: not-allowed;
        }
        .results-section {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
            padding: 30px;
            display: none;
        }
        .plant-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 30px;
        }
        .detail-card {
            background-color: #f5f5f5;
            border-radius: 12px;
            padding: 20px;
        }
        .back-link {
            display: block;
            text-align: center;
            margin-top: 30px;
            color: #4CAF50;
            text-decoration: none;
        }
        .loading {
            display: none;
            text-align: center;
            margin: 30px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Plant Species Identification</h1>
            <p>Upload a leaf image to identify plant species and get detailed information</p>
            <a href="/" class="back-link">Back to Home</a>
        </header>
        
        <div class="upload-section">
            <h2>Upload Image</h2>
            <form id="uploadForm" enctype="multipart/form-data">
                <input type="file" id="imageInput" name="image" accept="image/*" hidden>
                <div class="upload-box" id="dropArea" onclick="document.getElementById('imageInput').click()">
                    <p>Click to upload or drag and drop</p>
                    <p>Supports: JPG, PNG, JPEG</p>
                </div>
                <img id="imagePreview" src="#" alt="Preview">
                <button type="button" id="identifyBtn" class="button" disabled>Identify Plant</button>
            </form>
        </div>
        
        <div class="loading" id="loadingSection">
            <p>Analyzing your plant image...</p>
        </div>
        
        <div class="results-section" id="resultsSection">
            <div style="text-align: center;">
                <h2 id="plantName">Plant Name</h2>
                <p id="confidenceLevel">Confidence: 95%</p>
            </div>
            
            <div class="plant-details" id="plantDetails">
                <!-- Plant details will be inserted here -->
            </div>
        </div>
    </div>
    
    <script>
        const imageInput = document.getElementById('imageInput');
        const imagePreview = document.getElementById('imagePreview');
        const identifyBtn = document.getElementById('identifyBtn');
        const loadingSection = document.getElementById('loadingSection');
        const resultsSection = document.getElementById('resultsSection');
        const plantName = document.getElementById('plantName');
        const confidenceLevel = document.getElementById('confidenceLevel');
        const plantDetails = document.getElementById('plantDetails');
        const dropArea = document.getElementById('dropArea');
        const uploadForm = document.getElementById('uploadForm');
        
        // Handle file selection
        imageInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                    identifyBtn.disabled = false;
                }
                
                reader.readAsDataURL(this.files[0]);
            }
        });
        
        // Handle identify button click
        identifyBtn.addEventListener('click', identifyPlant);
        
        function identifyPlant() {
            if (!imageInput.files || !imageInput.files[0]) return;
            
            // Show loading
            loadingSection.style.display = 'block';
            resultsSection.style.display = 'none';
            
            const formData = new FormData(uploadForm);
            
            fetch('/predict', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Hide loading
                loadingSection.style.display = 'none';
                
                // Show results
                plantName.textContent = data.prediction;
                confidenceLevel.textContent = `Confidence: ${data.confidence}`;
                
                // Clear previous details
                plantDetails.innerHTML = '';
                
                // Add plant details
                const details = data.details;
                for (const key in details) {
                    if (key !== 'Scientific Name') {
                        const detailCard = document.createElement('div');
                        detailCard.className = 'detail-card';
                        
                        const detailTitle = document.createElement('h3');
                        detailTitle.textContent = key;
                        
                        const detailValue = document.createElement('p');
                        detailValue.textContent = details[key];
                        
                        detailCard.appendChild(detailTitle);
                        detailCard.appendChild(detailValue);
                        
                        plantDetails.appendChild(detailCard);
                    }
                }
                
                resultsSection.style.display = 'block';
            })
            .catch(error => {
                console.error('Error:', error);
                loadingSection.style.display = 'none';
                alert('An error occurred while identifying the plant. Please try again.');
            });
        }
    </script>
</body>
</html>
'''

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
            max-width: 1000px;
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
        .back-link {
            display: block;
            text-align: center;
            margin-top: 30px;
            color: #4CAF50;
            text-decoration: none;
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
            <a href="/" class="back-link">Back to Home</a>
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

# Routes
@app.route('/')
def index():
    return render_template_string(HOME_TEMPLATE)

# Plant Identification routes
@app.route('/plant_identification')
def plant_identification():
    return render_template_string(PLANT_TEMPLATE)

@app.route('/predict', methods=['POST'])
def predict():
    # Simulate plant identification without using the model
    plant = random.choice(sample_plants)
    confidence = random.uniform(85.0, 98.0)

    # Prepare response
    result = {
        'prediction': plant['Scientific Name'],
        'confidence': f"{confidence:.2f}%",
        'details': plant
    }

    return jsonify(result)

# Chatbot routes
@app.route('/chatbot')
def chatbot():
    return render_template_string(CHATBOT_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '').lower()
    
    # Simple keyword matching for demo purposes
    response = sample_responses['default']
    for keyword, answer in sample_responses.items():
        if keyword in message and keyword != 'default':
            response = answer
            break
    
    return jsonify({'response': response})

# For Vercel serverless deployment
if __name__ == '__main__':
    app.run()
