import os
import sys
import subprocess
import webbrowser
import time
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
import urllib.parse

# Global variables to track running processes
plant_process = None
chatbot_process = None
server_process = None

# HTML content for our launcher page
HTML = """
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
            cursor: pointer;
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
        
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        
        .success {
            background-color: #d4edda;
            color: #155724;
        }
        
        .error {
            background-color: #f8d7da;
            color: #721c24;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Agritech Hub</h1>
            <p class="subtitle">Your one-stop solution for agricultural technology</p>
        </header>
        
        <div id="status-message"></div>
        
        <div class="app-grid">
            <div class="app-card" onclick="launchApp('plant')">
                <div class="app-image">🌿</div>
                <div class="app-content">
                    <h2 class="app-title">Plant Species Identification</h2>
                    <p class="app-description">Upload a leaf image to identify plant species and get detailed information about the plant.</p>
                    <button class="app-button">Launch App</button>
                </div>
            </div>
            
            <div class="app-card" onclick="launchApp('chatbot')">
                <div class="app-image">🤖</div>
                <div class="app-content">
                    <h2 class="app-title">Agriculture Chatbot</h2>
                    <p class="app-description">Get answers to your agriculture-related questions using our AI-powered chatbot.</p>
                    <button class="app-button">Launch App</button>
                </div>
            </div>
        </div>
        
        <footer>
            <p>&copy; 2025 Agritech Hub. All rights reserved.</p>
        </footer>
    </div>
    
    <script>
        function launchApp(appType) {
            // Show loading message
            const statusDiv = document.getElementById('status-message');
            statusDiv.className = 'status';
            statusDiv.innerHTML = `<p>Starting ${appType === 'plant' ? 'Plant Identification' : 'Agriculture Chatbot'} application. Please wait...</p>`;
            
            // Make request to launch the app
            fetch(`/launch?app=${appType}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        statusDiv.className = 'status success';
                        statusDiv.innerHTML = `<p>${data.message}</p>`;
                        
                        // Redirect after a short delay
                        setTimeout(() => {
                            window.location.href = data.redirect_url;
                        }, 1500);
                    } else {
                        statusDiv.className = 'status error';
                        statusDiv.innerHTML = `<p>Error: ${data.message}</p>`;
                    }
                })
                .catch(error => {
                    statusDiv.className = 'status error';
                    statusDiv.innerHTML = `<p>Error: Could not start the application. Please try again.</p>`;
                    console.error('Error:', error);
                });
        }
    </script>
</body>
</html>
"""

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode())
        elif self.path.startswith('/launch'):
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            app_type = query_params.get('app', [''])[0]
            
            response = {}
            
            if app_type == 'plant':
                success, message, url = launch_plant_app()
                response = {
                    'success': success,
                    'message': message,
                    'redirect_url': url
                }
            elif app_type == 'chatbot':
                success, message, url = launch_chatbot_app()
                response = {
                    'success': success,
                    'message': message,
                    'redirect_url': url
                }
            else:
                response = {
                    'success': False,
                    'message': 'Invalid application type',
                    'redirect_url': ''
                }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(str(response).replace("'", '"').encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Not Found')

def launch_plant_app():
    global plant_process
    
    # Stop any running processes
    stop_all_processes()
    
    try:
        # Start the Plant Identification App
        plant_app_path = os.path.join(os.getcwd(), 'Plant_Identification_App', 'backend', 'app.py')
        print(f"Starting plant app from: {plant_app_path}")
        
        # Check if the file exists
        if not os.path.exists(plant_app_path):
            return False, f"File not found: {plant_app_path}", ''
        
        plant_process = subprocess.Popen(
            [sys.executable, plant_app_path],
            cwd=os.path.join(os.getcwd(), 'Plant_Identification_App'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        # Check if process is still running
        if plant_process.poll() is not None:
            error = plant_process.stderr.read().decode('utf-8')
            return False, f"Failed to start Plant Identification App: {error}", ''
        
        return True, "Plant Identification App started successfully", 'http://localhost:5000'
    except Exception as e:
        return False, f"Error starting Plant Identification App: {str(e)}", ''

def launch_chatbot_app():
    global chatbot_process
    
    # Stop any running processes
    stop_all_processes()
    
    try:
        # Start the Agriculture Chatbot
        chatbot_app_path = os.path.join(os.getcwd(), 'Langchain_PLD', 'app.py')
        print(f"Starting chatbot app from: {chatbot_app_path}")
        
        # Check if the file exists
        if not os.path.exists(chatbot_app_path):
            return False, f"File not found: {chatbot_app_path}", ''
        
        chatbot_process = subprocess.Popen(
            [sys.executable, '-m', 'streamlit', 'run', chatbot_app_path],
            cwd=os.path.join(os.getcwd(), 'Langchain_PLD'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        # Check if process is still running
        if chatbot_process.poll() is not None:
            error = chatbot_process.stderr.read().decode('utf-8')
            return False, f"Failed to start Agriculture Chatbot: {error}", ''
        
        return True, "Agriculture Chatbot started successfully", 'http://localhost:8501'
    except Exception as e:
        return False, f"Error starting Agriculture Chatbot: {str(e)}", ''

def stop_all_processes():
    global plant_process, chatbot_process
    
    # Stop Plant Identification process if running
    if plant_process:
        try:
            plant_process.terminate()
            print("Stopped plant identification process")
        except Exception as e:
            print(f"Error stopping plant process: {e}")
        plant_process = None
    
    # Stop Agriculture Chatbot process if running
    if chatbot_process:
        try:
            chatbot_process.terminate()
            print("Stopped chatbot process")
        except Exception as e:
            print(f"Error stopping chatbot process: {e}")
        chatbot_process = None

def run_server():
    port = 5050
    handler = CustomHandler
    
    with socketserver.TCPServer(("0.0.0.0", port), handler) as httpd:
        print(f"Server started at http://localhost:{port}")
        httpd.serve_forever()

def main():
    # Start the server in a separate thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Open the browser
    webbrowser.open(f"http://localhost:5050")
    
    # Keep the main thread running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        stop_all_processes()

if __name__ == "__main__":
    main()
