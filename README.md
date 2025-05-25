# Agritech Project

This repository contains multiple agricultural technology applications:

## 1. Plant Species Identification
An application that allows users to upload plant images and identify plant species with detailed information.

### Important Note About Model File
The machine learning model file is not included in this repository due to size limitations. To use the Plant Identification app, you need to:

1. Create a directory at `Plant_Identification_App/backend/model/` if it doesn't exist
2. Download the model file from [this Google Drive link](https://drive.google.com/drive/folders/your-folder-id) (replace with your actual link)
3. Place the downloaded model file in the model directory

## 2. Agricultural Chatbot
A chatbot that answers questions about agriculture and can process PDF documents to provide information based on their content.

## Features
- Plant species identification with image upload
- Agricultural knowledge base with information about plants, soil, fertilizer, irrigation, and pests
- PDF document processing and question answering
- Unified interface to access both applications

## Files
- `simplified_langchain_chatbot.py` - Streamlit-based agricultural chatbot with PDF processing
- `standalone_chatbot.py` - Flask-based agricultural chatbot
- `integrated_solution.py` - Unified application that combines both plant identification and chatbot
- `browser_preview_solution.py` - Simplified solution for browser preview
- `direct_launcher.py` - Direct launcher for original applications

## Usage
To run the simplified Langchain chatbot:
```
streamlit run simplified_langchain_chatbot.py
```

To run the integrated solution:
```
python integrated_solution.py
```
