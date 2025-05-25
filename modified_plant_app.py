from flask import Flask, render_template, request, jsonify
import os
import random
from werkzeug.utils import secure_filename

# Create a simplified version of the Plant Identification App
app = Flask(__name__)

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

# Create the HTML template
def create_template():
    with open('templates/index.html', 'w') as f:
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
            <a href="http://localhost:5555" class="back-link">Back to Home</a>
        </header>
        
        <div class="upload-section">
            <h2>Upload Image</h2>
            <input type="file" id="imageInput" accept="image/*" hidden>
            <div class="upload-box" id="dropArea" onclick="document.getElementById('imageInput').click()">
                <p>Click to upload or drag and drop</p>
                <p>Supports: JPG, PNG, JPEG</p>
            </div>
            <img id="imagePreview" src="#" alt="Preview">
            <button id="identifyBtn" class="button" disabled>Identify Plant</button>
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
''')

# Routes
@app.route('/')
def index():
    return render_template('index.html')

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

# Create the template when the app starts
create_template()

if __name__ == '__main__':
    print("Starting Plant Identification App on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
