import os
import sys
import random
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'agritech_secret_key'

# Create upload folder for plant images
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Create templates directory if it doesn't exist
os.makedirs('templates', exist_ok=True)

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
    'default': 'I\'m your agriculture assistant. You can ask me about plant care, fertilizers, pest control, and more!'
}

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Plant Identification routes
@app.route('/plant_identification')
def plant_identification():
    return render_template('plant_app.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    # Save image
    filename = secure_filename(file.filename)
    img_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(img_path)

    # Instead of using TensorFlow, just return a random plant from our sample data
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
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    query = data.get('query', '').lower()
    
    # Simple keyword matching for demo purposes
    response = sample_responses['default']
    for keyword, answer in sample_responses.items():
        if keyword in query and keyword != 'default':
            response = answer
            break
    
    return jsonify({'response': response})

# Create HTML templates
def create_templates():
    # Create index.html
    with open('templates/index.html', 'w') as f:
        f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agritech Hub</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1000px;
            width: 100%;
            padding: 20px;
        }
        
        header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        h1 {
            color: #388E3C;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #607D8B;
            font-size: 18px;
        }
        
        .app-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }
        
        .app-card {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .app-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
        }
        
        .app-image {
            height: 200px;
            background-color: #4CAF50;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 48px;
        }
        
        .app-content {
            padding: 30px;
        }
        
        .app-title {
            font-size: 24px;
            color: #388E3C;
            margin-bottom: 10px;
        }
        
        .app-description {
            color: #607D8B;
            margin-bottom: 20px;
        }
        
        .app-button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 12px;
            font-family: Arial, sans-serif;
            font-weight: 500;
            cursor: pointer;
            transition: background-color 0.3s ease;
            width: 100%;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }
        
        .app-button:hover {
            background-color: #388E3C;
        }
        
        .app-link {
            text-decoration: none;
            color: inherit;
            display: block;
        }
        
        footer {
            text-align: center;
            margin-top: 40px;
            color: #607D8B;
            font-size: 14px;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Agritech Hub</h1>
            <p class="subtitle">Your one-stop solution for agricultural technology</p>
        </header>
        
        <div class="app-grid">
            <div class="app-card">
                <div class="app-image">🌿</div>
                <div class="app-content">
                    <h2 class="app-title">Plant Species Identification</h2>
                    <p class="app-description">Upload a leaf image to identify plant species and get detailed information about the plant.</p>
                    <a href="/plant_identification" class="app-button">Launch App</a>
                </div>
            </div>
            
            <div class="app-card">
                <div class="app-image">🤖</div>
                <div class="app-content">
                    <h2 class="app-title">Agriculture Chatbot</h2>
                    <p class="app-description">Get answers to your agriculture-related questions using our AI-powered chatbot.</p>
                    <a href="/chatbot" class="app-button">Launch App</a>
                </div>
            </div>
        </div>
        
        <footer>
            <p>&copy; 2025 Agritech Hub. All rights reserved.</p>
        </footer>
    </div>
</body>
</html>
''')
    
    # Create plant_app.html
    with open('templates/plant_app.html', 'w') as f:
        f.write('''
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
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1000px;
            width: 100%;
            padding: 20px;
        }
        
        header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        h1 {
            color: #388E3C;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #607D8B;
            font-size: 18px;
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
            transition: border-color 0.3s ease;
        }
        
        .upload-box:hover {
            border-color: #4CAF50;
        }
        
        .upload-icon {
            font-size: 48px;
            color: #4CAF50;
            margin-bottom: 20px;
        }
        
        .upload-text {
            color: #607D8B;
            margin-bottom: 20px;
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
            font-family: Arial, sans-serif;
            font-weight: 500;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        
        .button:hover {
            background-color: #388E3C;
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
        
        .result-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .plant-name {
            color: #388E3C;
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .confidence {
            color: #607D8B;
            font-size: 18px;
            margin-bottom: 20px;
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
        
        .detail-title {
            color: #388E3C;
            margin-bottom: 10px;
            font-size: 20px;
        }
        
        .detail-value {
            color: #263238;
        }
        
        .back-link {
            display: block;
            text-align: center;
            margin-top: 30px;
            color: #4CAF50;
            text-decoration: none;
        }
        
        .back-link:hover {
            text-decoration: underline;
        }
        
        .loading {
            display: none;
            text-align: center;
            margin: 30px 0;
        }
        
        .spinner {
            border: 4px solid rgba(0, 0, 0, 0.1);
            width: 36px;
            height: 36px;
            border-radius: 50%;
            border-left-color: #4CAF50;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Plant Species Identification</h1>
            <p class="subtitle">Upload a leaf image to identify plant species and get detailed information</p>
            <a href="/" class="back-link">← Back to Home</a>
        </header>
        
        <div class="upload-section">
            <h2>Upload Image</h2>
            <input type="file" id="imageInput" accept="image/*" hidden>
            <div class="upload-box" id="dropArea" onclick="document.getElementById('imageInput').click()">
                <div class="upload-icon">📷</div>
                <p class="upload-text">Click to upload or drag and drop</p>
                <p class="upload-text">Supports: JPG, PNG, JPEG</p>
            </div>
            <img id="imagePreview" src="#" alt="Preview">
            <button id="identifyBtn" class="button" disabled>Identify Plant</button>
        </div>
        
        <div class="loading" id="loadingSection">
            <div class="spinner"></div>
            <p>Analyzing your plant image...</p>
        </div>
        
        <div class="results-section" id="resultsSection">
            <div class="result-header">
                <h2 class="plant-name" id="plantName">Plant Name</h2>
                <p class="confidence" id="confidenceLevel">Confidence: 95%</p>
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
        
        // Handle drag and drop
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            dropArea.style.borderColor = '#388E3C';
        }
        
        function unhighlight() {
            dropArea.style.borderColor = '#81C784';
        }
        
        dropArea.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files && files[0]) {
                imageInput.files = files;
                const event = new Event('change');
                imageInput.dispatchEvent(event);
            }
        }
        
        // Handle identify button click
        identifyBtn.addEventListener('click', identifyPlant);
        
        function identifyPlant() {
            if (!imageInput.files || !imageInput.files[0]) return;
            
            // Show loading
            loadingSection.style.display = 'block';
            resultsSection.style.display = 'none';
            
            const formData = new FormData();
            formData.append('image', imageInput.files[0]);
            
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
                        detailTitle.className = 'detail-title';
                        detailTitle.textContent = key;
                        
                        const detailValue = document.createElement('p');
                        detailValue.className = 'detail-value';
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
''')
    
    # Create chatbot.html
    with open('templates/chatbot.html', 'w') as f:
        f.write('''
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
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1000px;
            width: 100%;
            padding: 20px;
        }
        
        header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        h1 {
            color: #388E3C;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #607D8B;
            font-size: 18px;
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
            align-self: flex-end;
            margin-left: auto;
        }
        
        .bot-message {
            background-color: #F5F5F5;
            color: #263238;
            align-self: flex-start;
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
        
        .chat-input input:focus {
            border-color: #4CAF50;
        }
        
        .chat-input button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 24px;
            font-family: Arial, sans-serif;
            font-weight: 500;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        
        .chat-input button:hover {
            background-color: #388E3C;
        }
        
        .back-link {
            display: block;
            text-align: center;
            margin-top: 30px;
            color: #4CAF50;
            text-decoration: none;
        }
        
        .back-link:hover {
            text-decoration: underline;
        }
        
        .typing-indicator {
            display: none;
            padding: 10px 15px;
            background-color: #F5F5F5;
            border-radius: 18px;
            width: fit-content;
            margin-bottom: 15px;
        }
        
        .typing-indicator span {
            height: 8px;
            width: 8px;
            background-color: #757575;
            border-radius: 50%;
            display: inline-block;
            margin-right: 5px;
            animation: typing 1s infinite;
        }
        
        .typing-indicator span:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .typing-indicator span:nth-child(3) {
            animation-delay: 0.4s;
            margin-right: 0;
        }
        
        @keyframes typing {
            0% { opacity: 0.3; }
            50% { opacity: 1; }
            100% { opacity: 0.3; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Agriculture Chatbot</h1>
            <p class="subtitle">Get answers to your agriculture-related questions</p>
            <a href="/" class="back-link">← Back to Home</a>
        </header>
        
        <div class="chat-container">
            <div class="chat-messages" id="chatMessages">
                <div class="message bot-message">
                    Hello! I'm your agriculture assistant. How can I help you today? You can ask me about plant care, fertilizers, pest control, and more!
                </div>
            </div>
            
            <div class="typing-indicator" id="typingIndicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
            
            <div class="chat-input">
                <input type="text" id="userInput" placeholder="Type your question here..." autocomplete="off">
                <button id="sendBtn">Send</button>
            </div>
        </div>
    </div>
    
    <script>
        const chatMessages = document.getElementById('chatMessages');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');
        const typingIndicator = document.getElementById('typingIndicator');
        
        // Add event listeners
        sendBtn.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        function sendMessage() {
            const message = userInput.value.trim();
            if (message === '') return;
            
            // Add user message to chat
            addMessage(message, 'user');
            
            // Clear input
            userInput.value = '';
            
            // Show typing indicator
            typingIndicator.style.display = 'block';
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // Send message to server
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: message })
            })
            .then(response => response.json())
            .then(data => {
                // Hide typing indicator
                setTimeout(() => {
                    typingIndicator.style.display = 'none';
                    
                    // Add bot response to chat
                    addMessage(data.response, 'bot');
                }, 1000);
            })
            .catch(error => {
                console.error('Error:', error);
                
                // Hide typing indicator
                typingIndicator.style.display = 'none';
                
                // Add error message
                addMessage('Sorry, I\'m having trouble processing your request. Please try again later.', 'bot');
            });
        }
        
        function addMessage(text, sender) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.textContent = text;
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    </script>
</body>
</html>
''')

# Create templates when the app starts
create_templates()

if __name__ == '__main__':
    print("Starting Agritech Hub on http://localhost:5050")
    app.run(host='0.0.0.0', port=5050, debug=True)
