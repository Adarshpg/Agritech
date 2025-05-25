import os
import sys
import subprocess
import webbrowser
import time
from flask import Flask, render_template_string, redirect

app = Flask(__name__)

# Global variable to track the Langchain process
langchain_process = None

# HTML Template
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
        .instructions {
            margin-top: 30px;
            padding: 15px;
            border-radius: 5px;
            background-color: #E3F2FD;
            color: #1565C0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Agritech Hub - Langchain PDF Chatbot</h1>
        <p style="text-align: center;">Upload PDFs and ask questions about their content</p>
        
        <div class="options">
            <a href="/launch_langchain" style="width: 100%;">
                <div class="option">
                    <h2>Launch Langchain PDF Chatbot</h2>
                    <p>Upload agricultural PDFs and ask questions</p>
                </div>
            </a>
        </div>
        
        <div id="langchainStatus" class="status">
            Checking Langchain service status...
        </div>
        
        <div class="instructions">
            <h3>How to use the Langchain PDF Chatbot:</h3>
            <ol>
                <li>Click "Launch Langchain PDF Chatbot" to start the application</li>
                <li>Upload a PDF document using the file uploader</li>
                <li>Type your question in the text box</li>
                <li>Click "Submit Query" to get answers based on the PDF content</li>
            </ol>
            <p><strong>Note:</strong> The chatbot can also answer general agricultural questions using Wikipedia and research papers.</p>
        </div>
    </div>
    
    <script>
        // Check Langchain service status
        function checkStatus() {
            fetch('/langchain_status')
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('langchainStatus');
                    if (data.running) {
                        statusDiv.className = 'status online';
                        statusDiv.innerHTML = '✅ Langchain service is online and ready at <a href="' + data.url + '" target="_blank">' + data.url + '</a>';
                    } else {
                        statusDiv.className = 'status offline';
                        statusDiv.innerHTML = '⚠️ Langchain service is offline. Click "Launch Langchain PDF Chatbot" to start it.';
                    }
                });
        }
        
        // Check status immediately and then every 5 seconds
        checkStatus();
        setInterval(checkStatus, 5000);
    </script>
</body>
</html>
'''

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
        
        # Open the browser
        webbrowser.open('http://localhost:8501')
        
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

@app.route('/launch_langchain')
def launch_langchain():
    success, url = start_langchain_service()
    if success:
        return redirect(url)
    else:
        return f"<h1>Error starting Langchain service</h1><p>{url}</p><a href='/'>Back to Home</a>"

# Langchain service management
@app.route('/langchain_status')
def langchain_status():
    running, url = is_langchain_running()
    return {'running': running, 'url': url}

if __name__ == '__main__':
    print("Starting Langchain Launcher on http://127.0.0.1:5050")
    app.run(host='127.0.0.1', port=5050, debug=False)
