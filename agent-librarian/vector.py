# vector.py
from langchain_core.documents import Document
import os
import pandas as pd
import streamlit as st

# Function to create documents from dataframe
def create_documents_from_df(df):
    """Create document objects from dataframe rows"""
    documents = []
    
    # Handle any missing columns by filling NaN values
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
        
        documents.append(doc)
    
    return documents

# Function to get or create vector store
# Notice the leading underscore in _embeddings parameter to prevent hashing
@st.cache_resource
def get_vector_store(_embeddings, df):
    """Create or get vector store"""
    if _embeddings is None:
        return None
    
    try:
        from langchain_community.vectorstores import FAISS
        
        # Always create a fresh index in cloud environments
        documents = create_documents_from_df(df)
        
        if not documents:
            st.warning("No documents to create embeddings from.")
            return None
            
        st.info(f"Creating vector store with {len(documents)} documents...")
        vector_store = FAISS.from_documents(documents, _embeddings)
        st.success("Vector store created successfully!")
        
        return vector_store
    
    except Exception as e:
        st.error(f"Error creating vector store: {str(e)}")
        return None

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

# Global retriever variable - this will be initialized in app.py
retriever = None