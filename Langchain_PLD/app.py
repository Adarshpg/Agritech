import streamlit as st
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.tools import WikipediaQueryRun, ArxivQueryRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain.tools.retriever import create_retriever_tool
import os
from dotenv import load_dotenv #to call all the environment variables in which one contains api key
load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("google_api_key")

# Function to load PDF document, process and return retriever
def process_pdf(file_path):
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documents_txt = text_splitter.split_documents(docs)

    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-MiniLM-L3-v2")
    retriev_pdf = FAISS.from_documents(documents_txt, embedding=embedding_model)
    retriever_pdf = retriev_pdf.as_retriever()

    retriever_tool = create_retriever_tool(
        retriever_pdf,
        "plant_info_search",
        "Search for information about plants, fertilization, and other plant-related topics. Use this tool to answer any plant-related queries."
    )
    
    return retriever_tool

# Function to set up tools (including Wikipedia and Arxiv)
def setup_tools():
    # Wiki Tool
    api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=4000)
    wiki = WikipediaQueryRun(api_wrapper=api_wrapper)
    
    # Arxiv Tool
    arxiv_wrapper = ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=200)
    arxiv = ArxivQueryRun(api_wrapper=arxiv_wrapper)
    
    tools = [wiki, arxiv]
    return tools

# Setup Streamlit UI
st.title('Langchain Document Search and Query System')

# Step 1: Upload PDF
uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

# Step 2: Input box for query
query = st.text_input("Enter your query:")

# Step 3: Set up submit button (initially disabled)
submit_button_disabled = True
if query:
    submit_button_disabled = False

submit_button = st.button("Submit Query", disabled=submit_button_disabled)

# Add visual feedback for submit button
if query:
    submit_button_color = 'green'
else:
    submit_button_color = 'gray'

st.markdown(
    f"""
    <style>
        .stButton > button {{
            background-color: {submit_button_color};
        }}
    </style>
    """, unsafe_allow_html=True)

# Step 4: Process query and return result
if submit_button:
    # Setup tools (Wikipedia and Arxiv don't need document upload)
    tools = setup_tools()

    if uploaded_file:
        # If a file is uploaded, process it and add the retriever tool
        file_path = os.path.join("D:/pythonn alll/langchain_practice/Langchain_PLD/upload", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        retriever_tool = process_pdf(file_path)
        tools.append(retriever_tool)

    # Use Google LLM for handling queries
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    
    # Assuming you have a prompt from Langchain Hub or you can define a custom one
    from langchain import hub
    prompt = hub.pull("hwchase17/openai-functions-agent")

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # Invoke the agent with the query
    response = agent_executor.invoke({"input": query})

    # Step 5: Display response
    st.write("Response:")
    st.write(response)
