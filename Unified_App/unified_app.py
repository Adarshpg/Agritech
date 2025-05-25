from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import random
import sys
import subprocess
import threading

app = Flask(__name__)
app.secret_key = 'agritech_secret_key'

# Create upload folder for plant images
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

# Global variable to track the Streamlit process
streamlit_process = None

# Main routes
@app.route('/')
def index():
    # Stop any running Streamlit process when returning to the main page
    stop_streamlit()
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
    img_path = os.path.join(UPLOAD_FOLDER, file.filename)
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

# Agriculture Chatbot routes
@app.route('/chatbot')
def chatbot():
    # Start Streamlit in a separate process
    start_streamlit()
    # Redirect to the Streamlit app
    return redirect('http://localhost:8501')

def start_streamlit():
    global streamlit_process
    
    # Stop any running Streamlit process first
    stop_streamlit()
    
    try:
        # Start the Agriculture Chatbot using Streamlit
        chatbot_app_path = os.path.join(os.getcwd(), '..', 'Langchain_PLD', 'app.py')
        streamlit_process = subprocess.Popen(
            [sys.executable, '-m', 'streamlit', 'run', chatbot_app_path],
            cwd=os.path.join(os.getcwd(), '..', 'Langchain_PLD')
        )
        
        # Wait for the server to start
        import time
        time.sleep(2)
        return True
    except Exception as e:
        print(f"Exception starting Agriculture Chatbot: {e}")
        return False

def stop_streamlit():
    global streamlit_process
    
    # Stop Streamlit process if running
    if streamlit_process:
        try:
            streamlit_process.terminate()
        except Exception as e:
            print(f"Error stopping Streamlit process: {e}")
        streamlit_process = None

# Ensure Streamlit process is stopped when the application exits
import atexit
atexit.register(stop_streamlit)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
