import os
import sys
import subprocess
import time
from flask import Flask, render_template, redirect

app = Flask(__name__)

# Global variables to track running processes
plant_process = None
chatbot_process = None

@app.route('/')
def index():
    # Stop any running processes when returning to the main page
    stop_all_processes()
    return render_template('launcher.html')

@app.route('/launch_plant')
def launch_plant():
    global plant_process
    
    # Stop any running processes
    stop_all_processes()
    
    # Start the Plant Identification App
    plant_app_path = os.path.join(os.getcwd(), 'Plant_Identification_App', 'backend', 'app.py')
    print(f"Starting plant app from: {plant_app_path}")
    
    plant_process = subprocess.Popen(
        [sys.executable, plant_app_path],
        cwd=os.path.join(os.getcwd(), 'Plant_Identification_App')
    )
    
    # Give it a moment to start
    time.sleep(2)
    
    return redirect('http://localhost:5000')

@app.route('/launch_chatbot')
def launch_chatbot():
    global chatbot_process
    
    # Stop any running processes
    stop_all_processes()
    
    # Start the Agriculture Chatbot
    chatbot_app_path = os.path.join(os.getcwd(), 'Langchain_PLD', 'app.py')
    print(f"Starting chatbot app from: {chatbot_app_path}")
    
    chatbot_process = subprocess.Popen(
        [sys.executable, '-m', 'streamlit', 'run', chatbot_app_path],
        cwd=os.path.join(os.getcwd(), 'Langchain_PLD')
    )
    
    # Give it a moment to start
    time.sleep(2)
    
    return redirect('http://localhost:8501')

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

# Ensure processes are stopped when the application exits
import atexit
atexit.register(stop_all_processes)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create the launcher HTML file
    with open('templates/launcher.html', 'w') as f:
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
            cursor: pointer;
        }
        
        .app-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
        }
        
        .app-image {
            height: 200px;
            background-size: cover;
            background-position: center;
        }
        
        .plant-id-image {
            background-image: url('https://images.unsplash.com/photo-1520412099551-62b6bafeb5bb?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=687&q=80');
        }
        
        .chatbot-image {
            background-image: url('https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1470&q=80');
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
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Agritech Hub</h1>
            <p class="subtitle">Your one-stop solution for agricultural technology</p>
        </header>
        
        <div class="app-grid">
            <a href="/launch_plant" class="app-link">
                <div class="app-card">
                    <div class="app-image plant-id-image"></div>
                    <div class="app-content">
                        <h2 class="app-title">Plant Species Identification</h2>
                        <p class="app-description">Upload a leaf image to identify plant species and get detailed information about the plant.</p>
                        <button class="app-button">Launch App</button>
                    </div>
                </div>
            </a>
            
            <a href="/launch_chatbot" class="app-link">
                <div class="app-card">
                    <div class="app-image chatbot-image"></div>
                    <div class="app-content">
                        <h2 class="app-title">Agriculture Chatbot</h2>
                        <p class="app-description">Get answers to your agriculture-related questions using our AI-powered chatbot.</p>
                        <button class="app-button">Launch App</button>
                    </div>
                </div>
            </a>
        </div>
        
        <footer>
            <p>&copy; 2025 Agritech Hub. All rights reserved.</p>
        </footer>
    </div>
</body>
</html>
''')
    
    print("Starting Agritech Hub Launcher...")
    app.run(host='0.0.0.0', port=5050, debug=True)
