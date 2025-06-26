# 📚 Goodreads Library Assistant

A personal AI assistant for analyzing and exploring your Goodreads library data using Retrieval-Augmented Generation (RAG) and statistical analysis.

## Features

- **Interactive Analysis**: Ask questions about your reading habits, get book recommendations, and explore patterns in your library
- **Smart Classification**: Automatically determines whether to use statistical analysis or RAG based on your question
- **Customizable Outputs**: Specify how many results you want to see (e.g., "Show me my top 3 authors")
- **Visual Interface**: Clean Streamlit UI with your library data, question input, and answer history
- **Comprehensive Stats**: Get insights on your most-read authors, reading frequency, and favorite genres

## Installation

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running on your system

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/goodreads-library-assistant.git
   cd goodreads-library-assistant
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Download required models with Ollama:
   ```bash
   ollama pull llama3:8b
   ollama pull mxbai-embed-large
   ```

4. Place your Goodreads library export CSV in the `context` folder:
   ```bash
   mkdir -p context
   # Copy your exported "goodreads_library_export.csv" to this folder
   ```

## Usage

1. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. The app will open in your browser at `http://localhost:8501`

3. Ask questions about your library such as:
   - "Which author do I read the most?"
   - "Show only the names of my top 5 most read authors"
   - "What genres do I read most often?"
   - "How many books do I read per year?"
   - "Recommend a book similar to [book title]"
   - "What patterns do you see in my reading habits?"

## How It Works

The system uses a hybrid approach combining:

1. **Vector Database Retrieval**: For questions about specific books or recommendations
   - Creates embeddings from your book data using Ollama embeddings
   - Stores them in a local Chroma vector database
   - Retrieves relevant books based on semantic similarity

2. **Statistical Analysis**: For questions about patterns and trends
   - Analyzes your entire library directly from the CSV
   - Provides author statistics, reading frequency data, and genre analysis
   - Customizable to show only the information you request

3. **Smart Question Classification**: 
   - Uses pattern matching and keyword detection to determine the best approach
   - Extracts numbers and display preferences from your queries

## Project Structure

- `app.py`: Main Streamlit application
- `vector.py`: Vector store and retrieval functions
- `stats.py`: Statistical analysis functions
- `requirements.txt`: Required Python packages
- `context/`: Folder containing your Goodreads CSV data
- `chroma_langchain_db/`: Auto-generated vector database

## Exporting Your Goodreads Data

1. Log in to your Goodreads account
2. Go to "My Books" (your library)
3. Click on "Import and export" link at the bottom
4. Select "Export Library"
5. Place the downloaded CSV in the `context` folder

## Customization

- Edit the `model_name` and `temperature` variables in `app.py` to use different LLMs
- Modify the stats functions in `stats.py` to add new analysis types
- Adjust the retriever's `k` value to change how many books are retrieved for each query

## Logging

All interactions are logged in `goodreads_assistant.log` for future reference.

## License

MIT

---

Built with [LangChain](https://www.langchain.com/), [Ollama](https://ollama.ai/), and [Streamlit](https://streamlit.io/).