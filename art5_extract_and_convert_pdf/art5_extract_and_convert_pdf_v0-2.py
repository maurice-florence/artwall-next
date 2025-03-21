import os
import re
import fitz  # PyMuPDF
from pdfminer.high_level import extract_text, extract_pages
from pdfminer.layout import LTTextContainer
import pandas as pd
import camelot

# Script: Extract and Process PDF Text and Tables
# By: Johannes Renders (j.a.m.renders@minfin.nl)
# Creation Date: 2024-08-28

# This script automates the extraction of text and tables from a PDF file.
# It performs the following steps:
# 1. Extracts text content from the PDF using pdfminer and saves it into a CSV and a TXT file.
# 2. Extracts tables from the PDF using camelot-py (stream mode) and saves each table to a CSV file.

# Get the directory where the .py script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define file paths relative to the script's location
pdf_path = os.path.join(script_dir, "Maandrapportage december 2023.pdf")
text_output_csv = os.path.join(script_dir, "extracted_text.csv")
text_output_txt = os.path.join(script_dir, "extracted_text.txt")
table_output_dir = os.path.join(script_dir, "extracted_tables3")

# Create the directory for tables if it doesn't exist
os.makedirs(table_output_dir, exist_ok=True)

# Function to remove footers from text
def remove_footer(text):
    footer_pattern = r'Page \d+ of \d+.*?© Atradius.*?$'
    cleaned_text = re.sub(footer_pattern, '', text, flags=re.MULTILINE)
    return cleaned_text.strip()

# Function to extract and clean text using pdfminer and save it to a CSV and TXT file
def extract_and_save_text(pdf_path, csv_output_file, txt_output_file):
    data = []
    all_text = ""
    
    for i, page_layout in enumerate(extract_pages(pdf_path)):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                text = element.get_text()
                cleaned_text = clean_text(remove_footer(text))
                cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Remove extra spaces
                all_text += cleaned_text + "\n"
                for line_num, line in enumerate(cleaned_text.splitlines(), start=1):
                    data.append([line_num, i + 1, line])
    
    # Save to CSV
    df = pd.DataFrame(data, columns=["row", "page", "content"])
    df.to_csv(csv_output_file, index=False)
    print(f"Text extracted and saved to {csv_output_file}")
    
    # Save to TXT
    with open(txt_output_file, 'w', encoding='utf-8') as f:
        f.write(all_text)
    print(f"Text extracted and saved to {txt_output_file}")

# Function to clean the text by removing unnecessary characters
def clean_text(text):
    # Replace unwanted characters and clean up the text
    text = re.sub(r'[^\x09\x0A\x0D\x20-\x7E]', '', text)
    return text

# Function to extract tables using camelot-py (stream mode) and save them to CSV files
def extract_tables_from_pdf(pdf_path):
    try:
        tables = camelot.read_pdf(pdf_path, pages="all", flavor='stream')
        
        # Ensure that `tables` is a TableList and not empty
        if isinstance(tables, camelot.core.TableList) and len(tables) > 0:
            for idx, table in enumerate(tables):
                if isinstance(table.df, pd.DataFrame) and not table.df.empty:
                    # Use the page number and table index for the filename
                    page_num = table.page
                    table_filename = os.path.join(table_output_dir, f"tbl_p{page_num}_table_{idx + 1}.csv")
                    table.to_csv(table_filename, index=False)
                    print(f"Table from page {page_num} extracted and saved to {table_filename}")
                else:
                    print(f"No tables found on page {table.page}")
        else:
            print("No valid tables found or Camelot did not return a TableList object.")
    except Exception as e:
        print(f"Error extracting tables: {e}")

# Main execution

# Step 1: Extract and save all text from the PDF to a CSV and a TXT file
extract_and_save_text(pdf_path, text_output_csv, text_output_txt)

# Step 2: Extract tables from the PDF using camelot-py (stream mode) and save them as CSV files
extract_tables_from_pdf(pdf_path)

print("PDF content extraction completed.")
