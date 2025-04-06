# main.py
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from vector import retriever, get_book_details
from stats import get_author_stats, get_reading_stats, get_genre_stats
import re

# Initialize the Ollama LLM
model = OllamaLLM(model="llama3", temperature=0.2)

# Create a more detailed prompt template
template = """
You are a helpful assistant that specializes in book recommendations and literary analysis based on the user's personal Goodreads library.

The user has asked: {question}

Here are the most relevant books from their personal library:

{context}

Based on this information from their library, please provide a thoughtful and personalized response.
Consider details like their ratings, shelves they use, and their reading history when crafting your answer.

If the information provided isn't sufficient to answer their question, feel free to say so and ask for clarification.
"""

# Create the prompt and chain
prompt = ChatPromptTemplate.from_template(template)
output_parser = StrOutputParser()

# Build the chain
chain = prompt | model | output_parser

# More comprehensive patterns for better question recognition
author_stat_patterns = [
    r"author.*most.*book",
    r"which author.*read.*most",
    r"most read author",
    r"favorite author",
    r"top author",
    r"writer.*highest.*count",  # Catches your example
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

def classify_question(question):
    """
    Classifies a question into one of the categories: author_stats, reading_stats, genre_stats, or rag
    """
    question = question.lower()
    
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
    
    # More precise pattern matching
    is_author_stat = any(re.search(pattern, question) for pattern in author_stat_patterns)
    is_reading_stat = any(re.search(pattern, question) for pattern in reading_stat_patterns)
    is_genre_stat = any(re.search(pattern, question) for pattern in genre_stat_patterns)
    
    # Make the decision
    if is_author_stat or (has_author_keyword and has_stat_phrase):
        return "author_stats"
    elif is_reading_stat or (has_reading_keyword and has_stat_phrase):
        return "reading_stats"
    elif is_genre_stat or (has_genre_keyword and has_stat_phrase):
        return "genre_stats"
    else:
        return "rag"  # Default to RAG for anything else

print("\n📚 Welcome to Your Personal Goodreads Library Assistant 📚")
print("Ask questions about your reading habits, get recommendations, or analyze your library")

while True:
    print("\n" + "="*60)
    # Get user input for question
    question = input("Your Question (type 'q' to quit): ")
    
    if question.lower() in ['q', 'quit', 'exit']:
        print("Thank you for using your library assistant! Goodbye.")
        break
    
    # Classify the question
    question_type = classify_question(question)
    
    if question_type == "author_stats":
        print("Calculating author statistics...")
        author_stats = get_author_stats()
        print("\n🔍 ANSWER:\n")
        print(author_stats)
        
    elif question_type == "reading_stats":
        print("Calculating reading statistics...")
        reading_stats = get_reading_stats()
        print("\n🔍 ANSWER:\n")
        print(reading_stats)
        
    elif question_type == "genre_stats":
        print("Calculating genre statistics...")
        genre_stats = get_genre_stats()
        print("\n🔍 ANSWER:\n")
        print(genre_stats)
        
    else:  # RAG approach for non-statistical questions
        print("Searching your library...")
        retrieved_docs = retriever.invoke(question)
        
        if not retrieved_docs:
            print("No relevant books found. Try a different question.")
            continue
        
        # Format the retrieved documents using the helper function
        context = get_book_details(retrieved_docs)
        
        print(f"Found {len(retrieved_docs)} relevant books. Generating response...")
        
        # Run the chain with retrieved context
        result = chain.invoke({
            "context": context,
            "question": question
        })
        
        print("\n🔍 ANSWER:\n")
        print(result)