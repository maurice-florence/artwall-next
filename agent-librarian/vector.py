# vector.py
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd

# Load the dataset
df = pd.read_csv("context/goodreads_library_export.csv")

# Initialize embeddings model
embeddings = OllamaEmbeddings(model="mxbai-embed-large")
db_location = "./chroma_langchain_db"

# Check if we need to add documents
add_documents = not os.path.exists(db_location)

# Create the vector store instance
vector_store = Chroma(
    collection_name="goodreads",
    persist_directory=db_location,
    embedding_function=embeddings,
)

# Add documents if needed
if add_documents:
    documents = []
    ids = []
    
    # First, handle any missing columns by filling NaN values
    df = df.fillna("")
    
    for i, row in df.iterrows():
        # Create a richer text representation for embedding
        page_content = (
            f"Title: {row['Title']} | "
            f"Author: {row['Author']} | "
            f"Published: {row['Year Published']} | "
            f"My Rating: {row['My Rating']}/5"
        )
        
        # Include all columns as metadata
        metadata = {}
        for column in df.columns:
            # Convert to string to ensure compatibility
            metadata[column] = str(row[column])
        
        # Create document
        doc = Document(
            page_content=page_content,
            metadata=metadata
        )
        
        ids.append(str(i))
        documents.append(doc)
    
    print(f"Adding {len(documents)} documents to vector store...")
    # Add documents to the vector store
    vector_store.add_documents(documents=documents, ids=ids)
    print("Documents added successfully!")

# Create a retriever from the vector store
retriever = vector_store.as_retriever(
    search_kwargs={"k": 5}
)

# Function to help with displaying retrieved data
def get_book_details(retrieved_docs):
    """Format retrieved documents into detailed book information"""
    details = []
    
    for doc in retrieved_docs:
        metadata = doc.metadata
        detail = (
            f"Title: {metadata['Title']}\n"
            f"Author: {metadata['Author']}\n"
            f"My Rating: {metadata['My Rating']}/5\n"
            f"Average Rating: {metadata['Average Rating']}/5\n"
            f"Published: {metadata['Year Published']}\n"
            f"Pages: {metadata['Number of Pages']}\n"
            f"Date Read: {metadata['Date Read']}\n"
            f"Bookshelves: {metadata['Bookshelves']}\n"
            f"Exclusive Shelf: {metadata['Exclusive Shelf']}\n"
            f"My Review: {metadata['My Review']}\n"
            f"----------------------"
        )
        details.append(detail)
    
    return "\n".join(details)

# If this file is run directly, test the retriever
if __name__ == "__main__":
    query = input("Enter a test query: ")
    results = retriever.invoke(query)
    formatted_results = get_book_details(results)
    print(f"\nFound {len(results)} relevant books:")
    print(formatted_results)