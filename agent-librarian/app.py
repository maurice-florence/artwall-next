# app.py
import streamlit as st
import pandas as pd
import os
import datetime
import re
import logging
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from vector import retriever, get_book_details
from stats import get_author_stats, get_top_authors_simple, get_reading_stats, get_genre_stats

# Configure logging
logging.basicConfig(
    filename='goodreads_assistant.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Model configuration
model_name = "llama3:8b"
embedding_model = "mxbai-embed-large"
temperature = 0.2

# Set page title and layout
st.set_page_config(layout="wide", page_title="Goodreads Library Assistant")

# Title and model info in two columns
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📚 Goodreads Library Assistant")
with col2:
    st.write(f"**Model:** {model_name}")
    st.write(f"**Temperature:** {temperature}")
    st.write(f"**Embeddings:** {embedding_model}")

# Load the dataset
@st.cache_data
def load_data():
    return pd.read_csv("context/goodreads_library_export.csv")

df = load_data()

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

# Initialize LLM and chain
@st.cache_resource
def get_llm():
    return OllamaLLM(model=model_name, temperature=temperature)

@st.cache_resource
def get_chain():
    model = get_llm()
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
    return prompt | model | output_parser

chain = get_chain()

# Split the screen into two main sections
col_left, col_right = st.columns([1, 2])

# Left column - Dataset display
with col_left:
    st.subheader("Your Library Data")
    st.dataframe(df.head(100), height=650)

# Right column - Split into question and answer sections
with col_right:
    # Question section
    st.subheader("Ask About Your Books")
    question = st.text_input("Enter your question:", placeholder="e.g., Which author do I read the most?")
    
    # Initialize session state for storing chat history if not exists
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Process question when submitted
    if question and st.button("Ask"):
        # Classify the question
        question_info = classify_question(question)
        question_type = question_info["type"]
        number = question_info["number"] or 10  # Default to 10 if no number found
        simple_display = question_info["simple"]
        
        # Log the question
        logger.info(f"Question: {question}")
        logger.info(f"Question type: {question_type}, Number: {number}, Simple: {simple_display}")
        
        # Process based on question type
        if question_type == "author_stats":
            if simple_display:
                answer = get_top_authors_simple(limit=number)
                st.session_state.chat_history.insert(0, {"question": question, "answer": answer, "type": f"Author List (Top {number})"})
            else:
                answer = get_author_stats(limit=number)
                st.session_state.chat_history.insert(0, {"question": question, "answer": answer, "type": f"Author Statistics (Top {number})"})
            
        elif question_type == "reading_stats":
            answer = get_reading_stats()
            st.session_state.chat_history.insert(0, {"question": question, "answer": answer, "type": "Reading Statistics"})
            
        elif question_type == "genre_stats":
            answer = get_genre_stats()
            st.session_state.chat_history.insert(0, {"question": question, "answer": answer, "type": "Genre Statistics"})
            
        else:  # RAG approach
            retrieved_docs = retriever.invoke(question)
            if not retrieved_docs:
                answer = "No relevant books found in your library. Please try a different question."
                st.session_state.chat_history.insert(0, {"question": question, "answer": answer, "type": "RAG (No results)"})
            else:
                context = get_book_details(retrieved_docs)
                answer = chain.invoke({
                    "context": context,
                    "question": question
                })
                st.session_state.chat_history.insert(0, {
                    "question": question, 
                    "answer": answer, 
                    "type": f"RAG ({len(retrieved_docs)} books)"
                })
        
        # Log the answer
        logger.info(f"Answer: {answer}")
        logger.info("-" * 50)
    
    # Display chat history
    st.subheader("Answers")
    answer_container = st.container(height=550)
    
    with answer_container:
        for i, item in enumerate(st.session_state.chat_history):
            if i > 0:
                st.markdown("---")
            
            st.markdown(f"**Question:** {item['question']}")
            st.markdown(f"**Type:** {item['type']}")
            st.markdown(f"**Answer:**\n{item['answer']}")

# Add footer
st.markdown("---")
st.markdown("*Powered by LangChain and Ollama*")