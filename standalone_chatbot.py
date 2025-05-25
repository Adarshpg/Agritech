import os
import random
from flask import Flask, render_template_string, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Create upload folder for PDFs
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'pdf_uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store uploaded PDFs and their content (in a real app, this would use a database)
uploaded_pdfs = {}
pdf_content = {
    'agriculture_basics.pdf': [
        "Crop rotation is the practice of growing different types of crops in the same area across different growing seasons.",
        "Sustainable agriculture focuses on producing long-term crops and livestock while minimizing environmental impacts.",
        "Irrigation is the artificial application of water to land or soil to assist in the growth of agricultural crops.",
        "Fertilizers provide essential nutrients like nitrogen, phosphorus, and potassium to help plants grow.",
        "Organic farming avoids the use of synthetic fertilizers and pesticides, relying on techniques such as crop rotation and compost."
    ],
    'plant_diseases.pdf': [
        "Powdery mildew appears as white powdery spots on leaves and stems, caused by fungal pathogens.",
        "Leaf spot diseases are characterized by brown or black spots on leaves, often caused by fungi or bacteria.",
        "Root rot is a condition that causes the roots of plants to decay, often due to poor drainage or overwatering.",
        "Verticillium wilt is a fungal disease that affects over 350 plant species, causing wilting and yellowing of leaves.",
        "Integrated Pest Management (IPM) combines different pest control methods to minimize economic, health, and environmental risks."
    ],
    'soil_science.pdf': [
        "Soil pH affects nutrient availability to plants, with most crops preferring a slightly acidic to neutral pH (6.0-7.0).",
        "Soil texture refers to the proportion of sand, silt, and clay particles, which affects drainage and nutrient retention.",
        "Organic matter improves soil structure, water retention, and provides nutrients for plants and soil organisms.",
        "Soil compaction reduces pore space and restricts root growth, often caused by heavy machinery or livestock.",
        "Cover crops protect soil from erosion, add organic matter, and can help suppress weeds and pests."
    ]
}

# HTML Templates
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Agricultural PDF Chatbot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1, h2 {
            color: #4CAF50;
            text-align: center;
        }
        .upload-section {
            margin: 30px 0;
            padding: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background-color: #f9f9f9;
        }
        .pdf-list {
            margin: 30px 0;
        }
        .pdf-item {
            padding: 10px;
            margin: 10px 0;
            background-color: #E8F5E9;
            border-radius: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .pdf-item button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
        }
        .sample-pdfs {
            margin: 30px 0;
            padding: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background-color: #f9f9f9;
        }
        .sample-pdf-item {
            padding: 10px;
            margin: 10px 0;
            background-color: #E3F2FD;
            border-radius: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .sample-pdf-item button {
            background-color: #2196F3;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
        }
        .chat-button {
            display: block;
            width: 200px;
            margin: 30px auto;
            padding: 10px;
            background-color: #4CAF50;
            color: white;
            text-align: center;
            border-radius: 4px;
            text-decoration: none;
        }
        form {
            margin: 20px 0;
        }
        input[type="file"] {
            display: block;
            margin: 10px 0;
        }
        input[type="submit"] {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Agricultural PDF Chatbot</h1>
        <p style="text-align: center;">Upload PDFs and ask questions about their content</p>
        
        <div class="upload-section">
            <h2>Upload a PDF</h2>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="pdf" accept=".pdf">
                <input type="submit" value="Upload PDF">
            </form>
        </div>
        
        <div class="pdf-list">
            <h2>Your Uploaded PDFs</h2>
            <div id="uploadedPdfs">
                <!-- Uploaded PDFs will be listed here -->
                {% if uploaded_pdfs %}
                    {% for pdf_name in uploaded_pdfs %}
                        <div class="pdf-item">
                            <span>{{ pdf_name }}</span>
                            <button onclick="window.location.href='/chat?pdf={{ pdf_name }}';">Chat with this PDF</button>
                        </div>
                    {% endfor %}
                {% else %}
                    <p>No PDFs uploaded yet.</p>
                {% endif %}
            </div>
        </div>
        
        <div class="sample-pdfs">
            <h2>Sample PDFs</h2>
            <p>Don't have a PDF? Try our sample agricultural PDFs:</p>
            <div class="sample-pdf-item">
                <span>Agriculture Basics</span>
                <button onclick="window.location.href='/chat?pdf=agriculture_basics.pdf';">Chat with this PDF</button>
            </div>
            <div class="sample-pdf-item">
                <span>Plant Diseases</span>
                <button onclick="window.location.href='/chat?pdf=plant_diseases.pdf';">Chat with this PDF</button>
            </div>
            <div class="sample-pdf-item">
                <span>Soil Science</span>
                <button onclick="window.location.href='/chat?pdf=soil_science.pdf';">Chat with this PDF</button>
            </div>
        </div>
    </div>
</body>
</html>
'''

CHAT_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Chat with {{ pdf_name }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1000px;
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
        .pdf-info {
            margin: 20px 0;
            padding: 15px;
            background-color: #E8F5E9;
            border-radius: 8px;
            text-align: center;
        }
        .chat-container {
            height: 500px;
            display: flex;
            flex-direction: column;
            margin: 20px 0;
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
            margin-top: 20px;
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
        <h1>Chat with PDF</h1>
        
        <div class="pdf-info">
            <h3>{{ pdf_name }}</h3>
            <p>Ask questions about the content of this PDF</p>
        </div>
        
        <div class="chat-container">
            <div class="chat-messages" id="chatMessages">
                <div class="message bot-message">
                    Hello! I'm your agricultural assistant. Ask me any questions about the content in "{{ pdf_name }}".
                </div>
            </div>
            
            <div class="chat-input">
                <input type="text" id="userInput" placeholder="Ask a question about the PDF..." autocomplete="off">
                <button id="sendBtn">Send</button>
            </div>
        </div>
        
        <a href="/" class="back-link">Back to PDF List</a>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const chatMessages = document.getElementById('chatMessages');
            const userInput = document.getElementById('userInput');
            const sendBtn = document.getElementById('sendBtn');
            const pdfName = "{{ pdf_name }}";
            
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
                loadingText.textContent = 'Searching PDF';
                
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
                fetch('/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ question: message, pdf: pdfName })
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
                    addMessage(data.answer, 'bot');
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
    return render_template_string(HOME_TEMPLATE, uploaded_pdfs=uploaded_pdfs)

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['pdf']
    if file.filename == '':
        return redirect(url_for('index'))
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # In a real app, we would extract text from the PDF here
        # For this demo, we'll just store the filename
        uploaded_pdfs[filename] = file_path
        
        # Add some dummy content for the uploaded PDF
        if filename not in pdf_content:
            pdf_content[filename] = [
                "This is sample content extracted from your uploaded PDF.",
                "In a real application, we would use a PDF parser to extract the actual text.",
                "The chatbot would then use this extracted text to answer your questions.",
                "For demonstration purposes, we're using pre-defined responses.",
                "You can ask questions about agriculture, plants, soil, or farming practices."
            ]
        
        return redirect(url_for('index'))

@app.route('/chat')
def chat():
    pdf_name = request.args.get('pdf', '')
    if not pdf_name or (pdf_name not in uploaded_pdfs and pdf_name not in pdf_content):
        return redirect(url_for('index'))
    
    return render_template_string(CHAT_TEMPLATE, pdf_name=pdf_name)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question', '').lower()
    pdf_name = data.get('pdf', '')
    
    # Get content for the PDF
    content = pdf_content.get(pdf_name, [])
    
    # Simple keyword matching to find relevant content
    relevant_content = []
    for line in content:
        # Check if any word in the question appears in the line
        question_words = question.split()
        for word in question_words:
            if len(word) > 3 and word in line.lower():  # Only consider words longer than 3 characters
                relevant_content.append(line)
                break
    
    # Generate an answer based on relevant content
    if relevant_content:
        # Use the most relevant content as the answer
        answer = random.choice(relevant_content)
    else:
        # Fallback responses if no relevant content is found
        fallback_responses = [
            f"I couldn't find specific information about '{question}' in the PDF. Could you try rephrasing your question?",
            f"The PDF doesn't seem to contain details about '{question}'. Is there something else you'd like to know?",
            "I don't have enough information in the PDF to answer that question accurately. Could you ask something else?",
            "That topic doesn't appear to be covered in this PDF. Would you like to ask about something else?"
        ]
        answer = random.choice(fallback_responses)
    
    return jsonify({'answer': answer})

if __name__ == '__main__':
    print("Starting Agricultural PDF Chatbot on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=False)
