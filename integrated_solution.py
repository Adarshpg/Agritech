import os
import sys
import subprocess
import webbrowser
from flask import Flask, render_template_string, request, jsonify, redirect, send_from_directory
from werkzeug.utils import secure_filename
import random
import threading
import time

app = Flask(__name__)

# Create necessary folders
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

# Global variables to track running processes
langchain_process = None

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
        .status {
            margin-top: 30px;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }
        .online {
            background-color: #E8F5E9;
            color: #388E3C;
        }
        .offline {
            background-color: #FFEBEE;
            color: #D32F2F;
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
        
        <div id="langchainStatus" class="status">
            Checking Langchain service status...
        </div>
    </div>
    
    <script>
        // Check Langchain service status
        fetch('/langchain_status')
            .then(response => response.json())
            .then(data => {
                const statusDiv = document.getElementById('langchainStatus');
                if (data.running) {
                    statusDiv.className = 'status online';
                    statusDiv.innerHTML = '✅ Langchain service is online and ready';
                } else {
                    statusDiv.className = 'status offline';
                    statusDiv.innerHTML = '⚠️ Langchain service is offline. Starting service...';
                    
                    // Try to start the service
                    fetch('/start_langchain', { method: 'POST' })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                statusDiv.className = 'status online';
                                statusDiv.innerHTML = '✅ Langchain service has been started';
                            } else {
                                statusDiv.className = 'status offline';
                                statusDiv.innerHTML = '❌ Failed to start Langchain service: ' + data.error;
                            }
                        });
                }
            });
    </script>
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
        }
        .bot-message {
            background-color: #F5F5F5;
            color: #263238;
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
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }
        .online {
            background-color: #E8F5E9;
            color: #388E3C;
        }
        .offline {
            background-color: #FFEBEE;
            color: #D32F2F;
        }
        iframe {
            width: 100%;
            height: 600px;
            border: none;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
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
        
        <div id="statusSection" class="status">
            Checking Langchain service status...
        </div>
        
        <div id="iframeContainer" style="display: none; margin-top: 20px;">
            <iframe id="langchainFrame" src=""></iframe>
        </div>
        
        <div id="fallbackContainer" class="chat-container" style="display: none;">
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
        const statusSection = document.getElementById('statusSection');
        const iframeContainer = document.getElementById('iframeContainer');
        const fallbackContainer = document.getElementById('fallbackContainer');
        const langchainFrame = document.getElementById('langchainFrame');
        const chatMessages = document.getElementById('chatMessages');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');
        
        // Check Langchain service status
        fetch('/langchain_status')
            .then(response => response.json())
            .then(data => {
                if (data.running) {
                    // Show Langchain iframe
                    statusSection.className = 'status online';
                    statusSection.innerHTML = '✅ Langchain service is online and ready';
                    langchainFrame.src = data.url;
                    iframeContainer.style.display = 'block';
                } else {
                    // Try to start Langchain service
                    statusSection.className = 'status offline';
                    statusSection.innerHTML = '⚠️ Langchain service is offline. Starting service...';
                    
                    fetch('/start_langchain', { method: 'POST' })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                statusSection.className = 'status online';
                                statusSection.innerHTML = '✅ Langchain service has been started';
                                langchainFrame.src = data.url;
                                iframeContainer.style.display = 'block';
                                
                                // Check if the iframe loads correctly
                                setTimeout(checkIframeLoaded, 5000);
                            } else {
                                // Show fallback chatbot
                                statusSection.className = 'status offline';
                                statusSection.innerHTML = '❌ Failed to start Langchain service: ' + data.error + '<br>Using fallback chatbot instead.';
                                fallbackContainer.style.display = 'block';
                                setupFallbackChatbot();
                            }
                        })
                        .catch(error => {
                            // Show fallback chatbot on error
                            statusSection.className = 'status offline';
                            statusSection.innerHTML = '❌ Error connecting to server. Using fallback chatbot instead.';
                            fallbackContainer.style.display = 'block';
                            setupFallbackChatbot();
                        });
                }
            })
            .catch(error => {
                // Show fallback chatbot on error
                statusSection.className = 'status offline';
                statusSection.innerHTML = '❌ Error connecting to server. Using fallback chatbot instead.';
                fallbackContainer.style.display = 'block';
                setupFallbackChatbot();
            });
        
        function checkIframeLoaded() {
            try {
                // Try to access iframe content - if it fails, show fallback
                if (!langchainFrame.contentWindow || !langchainFrame.contentWindow.document) {
                    throw new Error('Cannot access iframe content');
                }
            } catch (e) {
                // Show fallback chatbot
                statusSection.className = 'status offline';
                statusSection.innerHTML = '❌ Langchain service is not responding correctly. Using fallback chatbot instead.';
                iframeContainer.style.display = 'none';
                fallbackContainer.style.display = 'block';
                setupFallbackChatbot();
            }
        }
        
        function setupFallbackChatbot() {
            // Add event listeners for fallback chatbot
            sendBtn.addEventListener('click', sendMessage);
            userInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        }
        
        function sendMessage() {
            const message = userInput.value.trim();
            if (message === '') return;
            
            // Add user message to chat
            addMessage(message, 'user');
            
            // Clear input
            userInput.value = '';
            
            // Show loading indicator
            const loadingMessage = document.createElement('div');
            loadingMessage.className = 'message bot-message';
            loadingMessage.id = 'loading-message';
            loadingMessage.textContent = 'Thinking...';
            chatMessages.appendChild(loadingMessage);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // Send message to server
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: message })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Remove loading message
                const loadingElement = document.getElementById('loading-message');
                if (loadingElement) {
                    loadingElement.remove();
                }
                
                // Add bot response
                if (data && data.response) {
                    addMessage(data.response, 'bot');
                } else {
                    addMessage('I received your message but couldn\'t generate a proper response.', 'bot');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                
                // Remove loading message
                const loadingElement = document.getElementById('loading-message');
                if (loadingElement) {
                    loadingElement.remove();
                }
                
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
'''

# Sample chatbot responses for fallback mode
sample_responses = {
    'fertilizer': 'For most plants, a balanced NPK (Nitrogen, Phosphorus, Potassium) fertilizer works well. Apply fertilizer during the growing season according to package instructions.',
    'watering': 'Most plants need consistent watering. Water when the top inch of soil feels dry. Avoid overwatering as it can lead to root rot.',
    'pests': 'Common garden pests include aphids, spider mites, and caterpillars. You can use neem oil or insecticidal soap as organic solutions.',
    'soil': 'Good soil is crucial for plant health. Most plants prefer well-draining soil rich in organic matter.',
    'default': 'I\'m your agriculture assistant. You can ask me about plant care, fertilizers, pest control, and more!'
}

# Function to start Langchain service
def start_langchain_service():
    global langchain_process
    try:
        # Kill any existing process
        if langchain_process:
            try:
                langchain_process.terminate()
                langchain_process = None
            except:
                pass
                
        # Start Langchain service
        langchain_dir = os.path.join(os.getcwd(), 'Langchain_PLD')
        cmd = [sys.executable, '-m', 'streamlit', 'run', os.path.join(langchain_dir, 'app.py'), '--server.port=8501']
        
        # Create process with appropriate environment
        env = os.environ.copy()
        langchain_process = subprocess.Popen(cmd, cwd=langchain_dir, env=env)
        
        # Wait a moment for the service to start
        time.sleep(2)
        
        return True, "http://localhost:8501"
    except Exception as e:
        return False, str(e)

# Function to check if Langchain service is running
def is_langchain_running():
    global langchain_process
    if langchain_process:
        return_code = langchain_process.poll()
        if return_code is None:  # Process is still running
            return True, "http://localhost:8501"
    return False, None

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
    return render_template_string(CHATBOT_TEMPLATE)

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
    
    # Add a small delay to simulate processing
    time.sleep(0.5)
    
    # Print for debugging
    print(f"Received query: {query}")
    print(f"Sending response: {response}")
    
    return jsonify({'response': response})

# Langchain service management
@app.route('/langchain_status')
def langchain_status():
    running, url = is_langchain_running()
    return jsonify({'running': running, 'url': url})

@app.route('/start_langchain', methods=['POST'])
def start_langchain():
    success, result = start_langchain_service()
    if success:
        return jsonify({'success': True, 'url': result})
    else:
        return jsonify({'success': False, 'error': result})

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    print("Starting Agritech Hub on http://127.0.0.1:5050")
    app.run(host='127.0.0.1', port=5050, debug=False)
