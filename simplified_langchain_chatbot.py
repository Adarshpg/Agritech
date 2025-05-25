import os
import streamlit as st
import random

# Sample agricultural knowledge base
agricultural_knowledge = {
    "plants": [
        "Plants require sunlight, water, and nutrients to grow properly.",
        "Most plants perform photosynthesis, converting sunlight into energy.",
        "Plant diseases can be caused by fungi, bacteria, viruses, or environmental conditions.",
        "Crop rotation helps prevent soil depletion and reduces pest problems.",
        "Perennial plants live for multiple growing seasons, while annuals complete their lifecycle in one season."
    ],
    "soil": [
        "Soil pH affects nutrient availability to plants. Most crops prefer a pH between 6.0 and 7.0.",
        "Soil texture is determined by the proportion of sand, silt, and clay particles.",
        "Organic matter improves soil structure, water retention, and provides nutrients.",
        "Cover crops protect soil from erosion and can add valuable nutrients when tilled under.",
        "Soil testing helps determine nutrient levels and pH, guiding fertilization decisions."
    ],
    "fertilizer": [
        "Nitrogen (N), phosphorus (P), and potassium (K) are the primary nutrients in most fertilizers.",
        "Organic fertilizers release nutrients slowly as they decompose in the soil.",
        "Chemical fertilizers provide nutrients in forms immediately available to plants.",
        "Over-fertilization can lead to nutrient runoff and water pollution.",
        "Different crops have different nutrient requirements throughout their growth cycle."
    ],
    "irrigation": [
        "Drip irrigation delivers water directly to plant roots, reducing water waste.",
        "Overhead sprinklers can be less efficient due to evaporation and wind drift.",
        "Irrigation scheduling should be based on plant needs and soil moisture levels.",
        "Water conservation techniques include mulching and using drought-resistant crops.",
        "Over-watering can lead to root diseases and nutrient leaching."
    ],
    "pests": [
        "Integrated Pest Management (IPM) combines multiple strategies to control pests effectively.",
        "Beneficial insects like ladybugs and lacewings can help control harmful pests.",
        "Crop rotation disrupts pest life cycles and reduces pest populations.",
        "Some plants have natural pest-repellent properties and can be used as companion plants.",
        "Biological controls use natural enemies to manage pest populations."
    ]
}

# PDF content database (simulated)
pdf_content = {}

# Function to search the knowledge base for relevant information
def search_knowledge_base(query):
    query = query.lower()
    relevant_info = []
    
    # Check for keywords in the query
    for topic, facts in agricultural_knowledge.items():
        if topic in query or any(keyword in query for keyword in ["about", "what is", "how to", "explain"]):
            relevant_info.extend(facts)
    
    # If we found relevant information, return it
    if relevant_info:
        return random.choice(relevant_info)
    else:
        return "I don't have specific information about that topic. Please ask about plants, soil, fertilizer, irrigation, or pests."

# Function to search PDF content (simulated)
def search_pdf_content(query, pdf_name):
    if pdf_name in pdf_content:
        content = pdf_content[pdf_name]
        
        # Simple keyword matching
        query_words = query.lower().split()
        for line in content:
            for word in query_words:
                if len(word) > 3 and word in line.lower():
                    return line
        
        return f"I couldn't find specific information about that in the PDF. The PDF contains information about {', '.join(content[:2])}..."
    else:
        return "No PDF content available. Please upload a PDF first."

# Function to extract text from PDF (simulated)
def extract_pdf_text(file):
    # In a real application, this would use a PDF parser
    # For this demo, we'll generate some sample content
    filename = file.name
    content = [
        f"This PDF discusses agricultural techniques and best practices.",
        f"It covers topics like soil management, crop rotation, and pest control.",
        f"The document emphasizes sustainable farming methods.",
        f"It also provides guidelines for organic certification.",
        f"The conclusion recommends seasonal planning for optimal yields."
    ]
    
    pdf_content[filename] = content
    return filename

# Streamlit UI
st.set_page_config(page_title="Agricultural Chatbot", page_icon="🌱")

st.title("🌱 Agricultural Chatbot")
st.write("Ask questions about agriculture or upload a PDF to chat about its content")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your agricultural assistant. How can I help you today?"}
    ]

if 'current_pdf' not in st.session_state:
    st.session_state.current_pdf = None

# Sidebar for PDF upload
with st.sidebar:
    st.header("Upload PDF Document")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        if st.button("Process PDF"):
            with st.spinner("Processing PDF..."):
                # Extract text from PDF (simulated)
                filename = extract_pdf_text(uploaded_file)
                st.session_state.current_pdf = filename
                st.success(f"PDF processed: {filename}")
                
                # Add a system message about the PDF
                pdf_msg = {"role": "assistant", "content": f"I've processed the PDF '{filename}'. You can now ask questions about its content."}
                st.session_state.messages.append(pdf_msg)
    
    if st.session_state.current_pdf:
        st.info(f"Current PDF: {st.session_state.current_pdf}")
    
    st.header("About")
    st.write("This chatbot can answer questions about agriculture and analyze uploaded PDF documents.")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about agriculture..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if st.session_state.current_pdf:
                # Search PDF content first
                response = search_pdf_content(prompt, st.session_state.current_pdf)
                if "I couldn't find specific information" in response:
                    # Fall back to general knowledge
                    general_response = search_knowledge_base(prompt)
                    response = f"{response} However, I can tell you that {general_response}"
            else:
                # Use general knowledge base
                response = search_knowledge_base(prompt)
            
            st.write(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
