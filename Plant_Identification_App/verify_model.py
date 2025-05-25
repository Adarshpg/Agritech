import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import pandas as pd
import os

# Load the model
model_path = r'D:\pythonn alll\plf_dl\Plant_Identification_App\backend\model\4th_year_final_project_10-02-25_14-55.h5'  # Use absolute path
model = tf.keras.models.load_model(model_path)

# Define the image path
img_path = r'D:\pythonn alll\plf_dl\Plant_Identification_App\download55.jpeg'  # Adjust the image path

# Load the image
img = Image.open(img_path)

# Preprocess the image (same as used in the model training)
img = img.resize((224, 224))  # Resize to 224x224 as used in the model
img_array = np.array(img) / 255.0  # Rescale pixel values to [0, 1]

# Add batch dimension (for single image input, batch size of 1)
img_array = np.expand_dims(img_array, axis=0)

# Predict the class probabilities
predictions = model.predict(img_array)

# Get the class with the highest probability
predicted_class = np.argmax(predictions, axis=1)

# Get the probability (confidence) of the prediction for the predicted class
confidence = np.max(predictions) * 100  # Multiply by 100 to express as percentage

# Load class labels from the CSV file
csv_path = r'D:\pythonn alll\plf_dl\Plant_Identification_App\backend\data\tree_names.csv'  # Path to CSV file
df = pd.read_csv(csv_path, header=None)  # Read CSV without header row
class_labels = df.iloc[0].tolist()  # Convert the first row into a list

# Get the predicted label
predicted_label = class_labels[predicted_class[0]]

# Load the CSV file with plant details
plant_info_csv_path = r'D:\pythonn alll\plf_dl\Plant_Identification_App\backend\data\plant_info.csv'  # Replace with actual path to your CSV file
df_plant_info = pd.read_csv(plant_info_csv_path)

# Normalize both predicted label and CSV names for comparison
predicted_label_normalized = predicted_label.strip().lower()

# Normalize the 'Scientific Name' column of the CSV
df_plant_info['Scientific Name Normalized'] = df_plant_info['Scientific Name'].str.strip().str.lower()

# Retrieve the row corresponding to the predicted plant
plant_info_row = df_plant_info[df_plant_info['Scientific Name Normalized'] == predicted_label_normalized]

# Print the predicted class
print(f"The model predicts the class of the image as: {predicted_label}")
print(f"Confidence: {confidence:.2f}%")  # Display the confidence level

# Display the plant details for the predicted plant
if not plant_info_row.empty:
    print(plant_info_row.to_string(index=False))  # Display the full row without the index
else:
    print("No details available for the predicted plant.")
