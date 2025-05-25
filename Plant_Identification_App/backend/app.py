from flask import Flask, render_template, request, jsonify
import os
import tensorflow as tf
from PIL import Image
import numpy as np
import pandas as pd

# App setup
app = Flask(__name__, template_folder='../templates', static_folder='../static')
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'backend', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load model
model_path = os.path.join('backend', 'model', '4th_year_final_project_10-02-25_14-55.h5')
model = tf.keras.models.load_model(model_path)

# Load class labels
df_labels = pd.read_csv(os.path.join('backend', 'data', 'tree_names.csv'), header=None)
class_labels = df_labels.iloc[0].tolist()

# Load plant info
plant_info_path = os.path.join('backend', 'data', 'plant_info.csv')
df_info = pd.read_csv(plant_info_path)
df_info['Scientific Name Normalized'] = df_info['Scientific Name'].str.strip().str.lower()

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
    img_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(img_path)

    # Preprocess
    img = Image.open(img_path).convert('RGB')
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Predict
    predictions = model.predict(img_array)
    predicted_idx = np.argmax(predictions, axis=1)[0]
    predicted_label = class_labels[predicted_idx]
    confidence = np.max(predictions) * 100

    # Match plant info
    label_norm = predicted_label.strip().lower()
    match = df_info[df_info['Scientific Name Normalized'] == label_norm]

    # Prepare response
    result = {
        'prediction': predicted_label,
        'confidence': f"{confidence:.2f}%",
        'details': match.iloc[0].to_dict() if not match.empty else "No info available"
    }

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)