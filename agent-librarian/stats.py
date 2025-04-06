# stats.py
import pandas as pd
from collections import Counter

def get_author_stats(csv_path="context/goodreads_library_export.csv", limit=10):
    """
    Analyze the Goodreads library to find author statistics
    
    Parameters:
    csv_path (str): Path to the Goodreads CSV file
    limit (int): Number of top authors to return
    
    Returns:
    str: Formatted author statistics
    """
    df = pd.read_csv(csv_path)
    
    # Count books by author
    author_counts = Counter(df['Author'])
    
    # Get top authors by book count
    top_authors = author_counts.most_common(limit)
    
    # Format the results
    result = "Author Statistics:\n"
    result += "==================\n\n"
    result += f"Top {limit} authors by number of books:\n"
    
    for author, count in top_authors:
        result += f"- {author}: {count} books\n"
        
        # Get the books by this author
        author_books = df[df['Author'] == author]
        avg_rating = author_books['My Rating'].replace('', '0').astype(float).mean()
        
        # List the books
        result += "  Books:\n"
        for _, book in author_books.iterrows():
            title = book['Title']
            rating = book['My Rating'] if book['My Rating'] else 'Unrated'
            result += f"  - {title} (My Rating: {rating})\n"
        
        result += f"  Average rating: {avg_rating:.1f}/5\n\n"
    
    return result

def get_top_authors_simple(csv_path="context/goodreads_library_export.csv", limit=3):
    """
    Returns just the names of the top authors without details
    
    Parameters:
    csv_path (str): Path to the Goodreads CSV file
    limit (int): Number of top authors to return
    
    Returns:
    str: Formatted list of top authors
    """
    df = pd.read_csv(csv_path)
    
    # Count books by author
    author_counts = Counter(df['Author'])
    
    # Get top authors by book count
    top_authors = author_counts.most_common(limit)
    
    # Format the results
    result = f"Top {limit} most read authors:\n\n"
    
    for i, (author, count) in enumerate(top_authors, 1):
        result += f"{i}. {author} ({count} books)\n"
    
    return result

def get_reading_stats(csv_path="context/goodreads_library_export.csv"):
    """
    Get overall reading statistics from the Goodreads library
    """
    df = pd.read_csv(csv_path)
    
    # Total books
    total_books = len(df)
    
    # Books with dates
    df['Date Read'] = pd.to_datetime(df['Date Read'], errors='coerce')
    read_books = df.dropna(subset=['Date Read'])
    
    # Books per year
    if not read_books.empty:
        read_books['Year Read'] = read_books['Date Read'].dt.year
        books_per_year = read_books.groupby('Year Read').size().to_dict()
        
        # Sort by year
        books_per_year = {k: books_per_year[k] for k in sorted(books_per_year.keys())}
    else:
        books_per_year = {}
    
    # Format results
    result = "Reading Statistics:\n"
    result += "==================\n\n"
    result += f"Total books in library: {total_books}\n"
    result += f"Books with 'read' dates: {len(read_books)}\n\n"
    
    if books_per_year:
        result += "Books read per year:\n"
        for year, count in books_per_year.items():
            result += f"- {int(year)}: {count} books\n"
    
    return result

def get_genre_stats(csv_path="context/goodreads_library_export.csv"):
    """
    Analyze bookshelves/genres in the Goodreads library
    """
    df = pd.read_csv(csv_path)
    
    # Get all bookshelves
    all_shelves = []
    for shelves in df['Bookshelves'].fillna(''):
        if shelves:
            all_shelves.extend([shelf.strip() for shelf in shelves.split(',')])
    
    # Count shelves
    shelf_counts = Counter(filter(None, all_shelves))
    top_shelves = shelf_counts.most_common(10)
    
    # Format results
    result = "Genre/Bookshelf Statistics:\n"
    result += "=========================\n\n"
    result += "Top bookshelves:\n"
    
    for shelf, count in top_shelves:
        result += f"- {shelf}: {count} books\n"
    
    return result