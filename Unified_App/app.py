from flask import Flask, render_template, redirect, url_for, request, flash
import subprocess
import threading
import os
import signal
import sys
import time

app = Flask(__name__)
app.secret_key = 'agritech_secret_key'

# Global variables to track running processes
plant_identification_process = None
agri_chatbot_process = None

@app.route('/')
def index():
    # Stop any running processes when returning to the main page
    stop_all_processes()
    return render_template('index.html')

@app.route('/launch_app', methods=['POST'])
def launch_app():
    app_choice = request.form.get('app_choice')
    
    if app_choice == 'plant_identification':
        # Start the Plant Identification App
        if start_plant_identification():
            return redirect('http://localhost:5000')
        else:
            flash('Failed to start Plant Identification App. Check console for details.')
            return redirect(url_for('index'))
    
    elif app_choice == 'agri_chatbot':
        # Start the Agriculture Chatbot
        if start_agri_chatbot():
            return redirect('http://localhost:8501')
        else:
            flash('Failed to start Agriculture Chatbot. Check console for details.')
            return redirect(url_for('index'))
    
    return redirect(url_for('index'))

def start_plant_identification():
    global plant_identification_process
    
    # Stop any running processes first
    stop_all_processes()
    
    try:
        # Start the simplified Plant Identification App
        plant_app_path = os.path.join(os.getcwd(), 'plant_app.py')
        plant_identification_process = subprocess.Popen(
            [sys.executable, plant_app_path],
            cwd=os.getcwd(),
            stderr=subprocess.PIPE
        )
        
        # Wait a moment to check for immediate errors
        time.sleep(1)
        
        # Check if the process is still running
        if plant_identification_process.poll() is not None:
            error = plant_identification_process.stderr.read().decode('utf-8')
            print(f"Error starting Plant Identification App: {error}")
            return False
            
        # Wait for the server to start
        time.sleep(2)
        return True
    except Exception as e:
        print(f"Exception starting Plant Identification App: {e}")
        return False

def start_agri_chatbot():
    global agri_chatbot_process
    
    # Stop any running processes first
    stop_all_processes()
    
    try:
        # Start the Agriculture Chatbot
        chatbot_app_path = os.path.join(os.getcwd(), '..', 'Langchain_PLD', 'app.py')
        agri_chatbot_process = subprocess.Popen(
            [sys.executable, '-m', 'streamlit', 'run', chatbot_app_path],
            cwd=os.path.join(os.getcwd(), '..', 'Langchain_PLD'),
            stderr=subprocess.PIPE
        )
        
        # Wait a moment to check for immediate errors
        time.sleep(1)
        
        # Check if the process is still running
        if agri_chatbot_process.poll() is not None:
            error = agri_chatbot_process.stderr.read().decode('utf-8')
            print(f"Error starting Agriculture Chatbot: {error}")
            return False
            
        # Wait for the server to start
        time.sleep(2)
        return True
    except Exception as e:
        print(f"Exception starting Agriculture Chatbot: {e}")
        return False

def stop_all_processes():
    global plant_identification_process, agri_chatbot_process
    
    # Stop Plant Identification process if running
    if plant_identification_process:
        try:
            if sys.platform == 'win32':
                plant_identification_process.terminate()
            else:
                os.killpg(os.getpgid(plant_identification_process.pid), signal.SIGTERM)
        except Exception as e:
            print(f"Error stopping plant identification process: {e}")
        plant_identification_process = None
    
    # Stop Agriculture Chatbot process if running
    if agri_chatbot_process:
        try:
            if sys.platform == 'win32':
                agri_chatbot_process.terminate()
            else:
                os.killpg(os.getpgid(agri_chatbot_process.pid), signal.SIGTERM)
        except Exception as e:
            print(f"Error stopping agriculture chatbot process: {e}")
        agri_chatbot_process = None

# Ensure processes are stopped when the application exits
import atexit
atexit.register(stop_all_processes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
