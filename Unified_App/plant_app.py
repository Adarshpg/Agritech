from flask import Flask, render_template, request, jsonify
import os
import random

# Create a simplified version of the Plant Identification App
app = Flask(__name__)
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

@app.route('/')
def index():
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

if __name__ == '__main__':
    app.run(debug=True)
