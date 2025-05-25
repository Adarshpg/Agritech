import os
import sys
import subprocess
import webbrowser
from flask import Flask, redirect

app = Flask(__name__)

# Global variables to track running processes
plant_process = None
chatbot_process = None

@app.route('/')
def index():
    return '''
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Agritech Hub</h1>
            <p style="text-align: center;">Your one-stop solution for agricultural technology</p>
            
            <div class="options">
                <div class="option" onclick="window.location.href='/launch_plant'">
                    <h2>Plant Species Identification</h2>
                    <p>Identify plant species from images</p>
                </div>
                
                <div class="option" onclick="window.location.href='/launch_chatbot'">
                    <h2>Agriculture Chatbot</h2>
                    <p>Get answers to your agriculture questions</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/launch_plant')
def launch_plant():
    global plant_process
    
    # Stop any running processes
    stop_all_processes()
    
    try:
        # Start the modified Plant Identification App that doesn't require TensorFlow
        plant_app_path = os.path.join(os.getcwd(), 'modified_plant_app.py')
        print(f"Starting modified plant app from: {plant_app_path}")
        
        # Check if the file exists
        if not os.path.exists(plant_app_path):
            return f"Error: File not found: {plant_app_path}"
        
        # Start the process
        plant_process = subprocess.Popen(
            [sys.executable, plant_app_path],
            cwd=os.getcwd()
        )
        
        # Wait a moment for the app to start
        import time
        time.sleep(2)
        
        # Open the browser directly
        webbrowser.open('http://localhost:5000')
        
        # Redirect to the plant app
        return redirect('http://localhost:5000')
    
    except Exception as e:
        return f"Error starting Plant Identification App: {str(e)}"

@app.route('/launch_chatbot')
def launch_chatbot():
    global chatbot_process
    
    # Stop any running processes
    stop_all_processes()
    
    try:
        # Start the Agriculture Chatbot
        chatbot_app_path = os.path.join(os.getcwd(), 'Langchain_PLD', 'app.py')
        print(f"Starting chatbot app from: {chatbot_app_path}")
        
        # Check if the file exists
        if not os.path.exists(chatbot_app_path):
            return f"Error: File not found: {chatbot_app_path}"
        
        # Start the process
        chatbot_process = subprocess.Popen(
            [sys.executable, '-m', 'streamlit', 'run', chatbot_app_path],
            cwd=os.path.join(os.getcwd(), 'Langchain_PLD')
        )
        
        # Wait a moment for the app to start
        import time
        time.sleep(2)
        
        # Open the browser directly
        webbrowser.open('http://localhost:8501')
        
        # Redirect to the chatbot app
        return redirect('http://localhost:8501')
    
    except Exception as e:
        return f"Error starting Agriculture Chatbot: {str(e)}"

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
    # Make sure we're not using a port that's already in use
    port = 5555  # Using a different port to avoid conflicts
    print(f"Starting Agritech Hub Launcher on http://localhost:{port}")
    webbrowser.open(f"http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)  # Debug mode off for stability
