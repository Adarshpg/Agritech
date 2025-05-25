# Agritech Hub - Unified Application

This application combines two projects into a single interface:
1. Plant Species Identification
2. Agriculture Chatbot (Langchain)

## Setup Instructions

### 1. Install Dependencies

Before running the application, make sure to install all the required dependencies:

```bash
pip install -r requirements.txt
```

This will install all the necessary packages for both applications.

### 2. Run the Unified Application

To start the unified application, run:

```bash
python app.py
```

This will start the main interface on http://localhost:5050

### 3. Using the Application

- From the main interface, you can choose which application to launch
- When you click on "Plant Species Identification", it will start the plant identification server and redirect you to it
- When you click on "Agriculture Chatbot", it will start the Streamlit-based chatbot and redirect you to it
- To switch between applications, return to the main interface at http://localhost:5050

## Troubleshooting

If you encounter issues with either application not starting:

1. Check that all dependencies are installed correctly
2. Ensure that both original applications work independently
3. Check the console output for specific error messages

## Project Structure

- `app.py` - Main Flask application that serves as the entry point
- `templates/` - Contains the HTML templates for the unified interface
- `static/` - Contains static assets like CSS and JavaScript files
- `requirements.txt` - Lists all dependencies for both applications
