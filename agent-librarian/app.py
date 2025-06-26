# app.py
import streamlit as st
import pandas as pd
import os
import datetime
import re
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from stats import get_author_stats, get_top_authors_simple, get_reading_stats, get_genre_stats
import vector

# Configure logging
logging.basicConfig(
    filename='goodreads_assistant.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Set page title and layout
st.set_page_config(layout="wide", page_title="Goodreads Library Assistant")

# Title section
st.title("📚 Goodreads Library Assistant")

# Function to determine temperature based on question type
def get_adaptive_temperature(question_type, question_subtype=None):
    """
    Set temperature based on question classification:
    - Statistics: low temp (0.1)
    - Recommendations: medium temp (0.5)
    - Analysis/Exploratory: higher temp (0.7)
    """
    if question_type in ["author_stats", "reading_stats", "genre_stats"]:
        # Statistical questions need precision
        return 0.1, "Statistical Query (Temperature: 0.1)"
    
    # Check for recommendation patterns
    recommendation_patterns = [
        r"recommend", r"suggest", r"similar to", 
        r"like .+\?", r"books (like|similar)", r"should i read"
    ]
    
    if any(re.search(pattern, question.lower()) for pattern in recommendation_patterns):
        return 0.5, "Recommendation Query (Temperature: 0.5)"
    
    # Check for analysis/exploratory patterns
    exploratory_patterns = [
        r"what .+ patterns", r"analyze", r"explore", 
        r"what do you think", r"interesting", r"unique"
    ]
    
    if any(re.search(pattern, question.lower()) for pattern in exploratory_patterns):
        return 0.7, "Exploratory Query (Temperature: 0.7)"
    
    # Default to medium temperature for other RAG queries
    return 0.4, "General Query (Temperature: 0.4)"

# Load the dataset
@st.cache_data
def load_data():
    try:
        return pd.read_csv("context/goodreads_library_export.csv")
    except Exception as e:
        st.error(f"Error loading the dataset: {str(e)}")
        # Return empty dataframe if file not found
        return pd.DataFrame()

df = load_data()

# Sidebar for model selection and database view
with st.sidebar:
    st.header("Model Settings")
    model_option = st.selectbox(
        "Select LLM Provider",
        ["OpenAI", "Ollama", "Hugging Face"],
        index=1  # Default to Ollama
    )
    
    llm = None
    embeddings = None
    base_temperature = 0.4  # Default starting temperature
    
    if model_option == "OpenAI":
        openai_api_key = st.text_input("OpenAI API Key", type="password")
        openai_model = st.selectbox(
            "OpenAI Model",
            ["gpt-3.5-turbo", "gpt-4o"],
            index=0
        )
        base_temperature = st.slider("Base Temperature", 0.0, 1.0, 0.4, 0.1, 
                                    help="This will be adjusted based on question type")
        embedding_model = "text-embedding-3-small"
        
        # Set up OpenAI models
        if openai_api_key:
            try:
                from langchain_openai import ChatOpenAI, OpenAIEmbeddings
                os.environ["OPENAI_API_KEY"] = openai_api_key
                # Temperature will be set per query
                llm = ChatOpenAI(model=openai_model, temperature=base_temperature)
                embeddings = OpenAIEmbeddings()
                st.success("OpenAI API connected!")
            except Exception as e:
                st.error(f"Failed to connect to OpenAI: {str(e)}")
                llm = None
                embeddings = None
        else:
            st.warning("Please enter your OpenAI API key")
            
    elif model_option == "Ollama":
        ollama_base_url = st.text_input("Ollama API URL", value="http://localhost:11434")
        ollama_model = st.selectbox(
            "Ollama Model",
            ["llama3", "llama3:8b", "mistral"],
            index=1
        )
        base_temperature = st.slider("Base Temperature", 0.0, 1.0, 0.4, 0.1,
                                    help="This will be adjusted based on question type")
        embedding_model = "mxbai-embed-large"
        
        # Set up Ollama models
        if ollama_base_url:
            try:
                from langchain_ollama import OllamaLLM, OllamaEmbeddings
                # Temperature will be set per query
                llm = OllamaLLM(model=ollama_model, temperature=base_temperature, base_url=ollama_base_url)
                embeddings = OllamaEmbeddings(model=embedding_model, base_url=ollama_base_url)
                st.success(f"Connected to Ollama at {ollama_base_url}")
            except Exception as e:
                st.error(f"Failed to connect to Ollama: {str(e)}")
                llm = None
                embeddings = None
    
    elif model_option == "Hugging Face":
        huggingface_token = st.text_input("Hugging Face Token", type="password")
        base_temperature = st.slider("Base Temperature", 0.0, 1.0, 0.4, 0.1,
                                   help="This will be adjusted based on question type")
        
        # Set up Hugging Face models
        if huggingface_token:
            try:
                from langchain_huggingface import HuggingFaceEndpoint
                os.environ["HUGGINGFACEHUB_API_TOKEN"] = huggingface_token
                # Temperature will be set per query
                llm = HuggingFaceEndpoint(
                    repo_id="mistralai/Mistral-7B-Instruct-v0.2",
                    temperature=base_temperature
                )
                # Using MiniLM for embeddings
                from langchain_community.embeddings import HuggingFaceEmbeddings
                embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                embedding_model = "all-MiniLM-L6-v2"
                st.success("Hugging Face API connected!")
            except Exception as e:
                st.error(f"Failed to connect to Hugging Face: {str(e)}")
                llm = None
                embeddings = None
    
    # Database viewer in sidebar
    st.header("Library Data")
    if st.button("View Library Data"):
        if not df.empty:
            st.dataframe(df.head(100), height=400)
        else:
            st.error("No data loaded. Please place goodreads_library_export.csv in the context folder.")

# Extract number from query
def extract_number(query):
    """Extract a number from a query string like 'top 3 authors'"""
    number_words = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
    }
    
    # Try to find written numbers (one, two, three, etc.)
    for word, number in number_words.items():
        if word in query.lower():
            return number
    
    # Try to find numeric digits (1, 2, 3, etc.)
    matches = re.findall(r'\b(\d+)\b', query)
    if matches:
        return int(matches[0])
    
    return None  # Default to None if no number found

# Question classification function with improved number detection
def classify_question(question):
    """
    Classifies a question into one of the categories: author_stats, reading_stats, genre_stats, or rag
    Also extracts any numbers that might be limiting the results
    """
    question = question.lower()
    
    # Extract any numbers in the query (e.g., "top 3 authors")
    number = extract_number(question)
    
    # Key words that strongly suggest each category
    author_keywords = ["author", "writer", "novelist", "wrote"]
    reading_keywords = ["read", "books", "complete", "finish"]
    genre_keywords = ["genre", "category", "shelf", "type"]
    
    # Statistical phrases that suggest counting/ranking
    stat_phrases = ["most", "highest", "top", "list", "count", "how many", "statistics", "stats"]
    
    # Check for keyword combinations that suggest statistical questions
    has_author_keyword = any(word in question for word in author_keywords)
    has_reading_keyword = any(word in question for word in reading_keywords)
    has_genre_keyword = any(word in question for word in genre_keywords)
    has_stat_phrase = any(phrase in question for phrase in stat_phrases)
    
    # Check for simple display requests
    simple_display = ("only" in question or "just" in question or "names" in question) and number is not None
    
    # Comprehensive patterns for better question recognition
    author_stat_patterns = [
        r"author.*most.*book",
        r"which author.*read.*most",
        r"most read author",
        r"favorite author",
        r"top author",
        r"writer.*highest.*count",
        r"writer.*most",
        r"author.*list",
        r"most popular author",
        r"author.*statistics",
        r"author.*ranking",
        r"author.*count"
    ]

    reading_stat_patterns = [
        r"read.*per year",
        r"how many.*book",
        r"reading stats",
        r"reading statistics",
        r"book.*count",
        r"number of books",
        r"books per month",
        r"reading frequency",
        r"reading habits",
        r"reading history",
        r"books completed"
    ]

    genre_stat_patterns = [
        r"genre",
        r"bookshelf",
        r"category",
        r"shelf",
        r"type.*book",
        r"book.*type",
        r"fiction.*non-fiction",
        r"fiction vs non-fiction", 
        r"topics",
        r"subject"
    ]
    
    # More precise pattern matching
    is_author_stat = any(re.search(pattern, question) for pattern in author_stat_patterns)
    is_reading_stat = any(re.search(pattern, question) for pattern in reading_stat_patterns)
    is_genre_stat = any(re.search(pattern, question) for pattern in genre_stat_patterns)
    
    # Make the decision
    result = {"type": "rag", "number": number, "simple": False}
    
    if is_author_stat or (has_author_keyword and has_stat_phrase):
        result["type"] = "author_stats"
        result["simple"] = simple_display
    elif is_reading_stat or (has_reading_keyword and has_stat_phrase):
        result["type"] = "reading_stats"
    elif is_genre_stat or (has_genre_keyword and has_stat_phrase):
        result["type"] = "genre_stats"
    
    return result

# Create the prompt template for RAG
def get_chain(llm_model, temp):
    if not llm_model:
        return None
    
    # Create a new instance of the LLM with the adaptive temperature
    if isinstance(llm_model, OllamaLLM):
        adaptive_llm = OllamaLLM(
            model=llm_model.model,
            temperature=temp,
            base_url=llm_model.base_url
        )
    elif isinstance(llm_model, ChatOpenAI):
        adaptive_llm = ChatOpenAI(
            model=llm_model.model_name,
            temperature=temp
        )
    elif hasattr(llm_model, 'repo_id'):  # HuggingFaceEndpoint
        adaptive_llm = HuggingFaceEndpoint(
            repo_id=llm_model.repo_id,
            temperature=temp
        )
    else:
        # Fallback
        adaptive_llm = llm_model
        
    template = """
    You are a helpful assistant that specializes in book recommendations and literary analysis based on the user's personal Goodreads library.

    The user has asked: {question}

    Here are the most relevant books from their personal library:

    {context}

    Based on this information from their library, please provide a thoughtful and personalized response.
    Consider details like their ratings, shelves they use, and their reading history when crafting your answer.

    If the information provided isn't sufficient to answer their question, feel free to say so and ask for clarification.
    """
    prompt = ChatPromptTemplate.from_template(template)
    output_parser = StrOutputParser()
    return prompt | adaptive_llm | output_parser

# Create vector store and retriever if embeddings are available
if embeddings and not df.empty:
    vector_store = vector.get_vector_store(_embeddings=embeddings, df=df)
    if vector_store:
        vector.retriever = vector_store.as_retriever(search_kwargs={"k": 5})

# Main content area
# Check if the models are ready
models_ready = (llm is not None and embeddings is not None)

# Display a warning if models aren't ready
if not models_ready:
    st.warning("Please configure your model settings in the sidebar before asking questions.")

# Question input
st.subheader("Ask About Your Books")
question = st.text_input(
    "Enter your question:", 
    placeholder="e.g., Which author do I read the most?",
    disabled=not models_ready
)

# Initialize session state for storing chat history if not exists
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Process question when submitted
if question and st.button("Ask", disabled=not models_ready):
    # Classify the question
    question_info = classify_question(question)
    question_type = question_info["type"]
    number = question_info["number"] or 10  # Default to 10 if no number found
    simple_display = question_info["simple"]
    
    # Determine appropriate temperature based on question type
    adaptive_temp, query_type_info = get_adaptive_temperature(question_type, question)
    
    # Log the question and temperature
    logger.info(f"Question: {question}")
    logger.info(f"Question type: {question_type}, Number: {number}, Simple: {simple_display}")
    logger.info(f"Using temperature: {adaptive_temp}")
    
    # Process based on question type
    if question_type == "author_stats":
        if simple_display:
            answer = get_top_authors_simple(limit=number)
            st.session_state.chat_history.insert(0, {
                "question": question, 
                "answer": answer, 
                "type": f"Author List (Top {number})",
                "query_type": query_type_info
            })
        else:
            answer = get_author_stats(limit=number)
            st.session_state.chat_history.insert(0, {
                "question": question, 
                "answer": answer, 
                "type": f"Author Statistics (Top {number})",
                "query_type": query_type_info
            })
        
    elif question_type == "reading_stats":
        answer = get_reading_stats()
        st.session_state.chat_history.insert(0, {
            "question": question, 
            "answer": answer, 
            "type": "Reading Statistics",
            "query_type": query_type_info
        })
        
    elif question_type == "genre_stats":
        answer = get_genre_stats()
        st.session_state.chat_history.insert(0, {
            "question": question, 
            "answer": answer, 
            "type": "Genre Statistics",
            "query_type": query_type_info
        })
        
    else:  # RAG approach
        if vector.retriever:
            retrieved_docs = vector.retriever.invoke(question)
            if not retrieved_docs:
                answer = "No relevant books found in your library. Please try a different question."
                st.session_state.chat_history.insert(0, {
                    "question": question, 
                    "answer": answer, 
                    "type": "RAG (No results)",
                    "query_type": query_type_info
                })
            else:
                context = vector.get_book_details(retrieved_docs)
                # Create a chain with the adaptive temperature
                chain = get_chain(llm, adaptive_temp)
                answer = chain.invoke({
                    "context": context,
                    "question": question
                })
                st.session_state.chat_history.insert(0, {
                    "question": question, 
                    "answer": answer, 
                    "type": f"RAG ({len(retrieved_docs)} books)",
                    "query_type": query_type_info
                })
        else:
            answer = "Vector retrieval system is not available. Please check your model configuration."
            st.session_state.chat_history.insert(0, {
                "question": question, 
                "answer": answer, 
                "type": "Error",
                "query_type": "N/A"
            })
    
    # Log the answer
    logger.info(f"Answer: {answer}")
    logger.info("-" * 50)

# Display chat history
st.subheader("Answers")
answer_container = st.container(height=600)

with answer_container:
    for i, item in enumerate(st.session_state.chat_history):
        if i > 0:
            st.markdown("---")
        
        st.markdown(f"**Question:** {item['question']}")
        st.markdown(f"**Type:** {item['type']}")
        st.markdown(f"**Query Classification:** {item.get('query_type', 'N/A')}")
        st.markdown(f"**Answer:**\n{item['answer']}")

# Add footer
st.markdown("---")
st.markdown("*Powered by LangChain and Streamlit*")