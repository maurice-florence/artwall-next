import os
import re
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
import pandas as pd

# Script: Aggregate Text and CSV from PDF
# By: Johannes Renders (j.a.m.renders@minfin.nl)
# Creation Date: 2024-08-28

# This script extracts text content from a PDF and saves it into an aggregate CSV and TXT file.
# The CSV file includes additional columns (position_1, position_2, etc.) based on content distribution.

# Get the directory where the .py script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define file paths relative to the script's location
pdf_path = os.path.join(script_dir, "Maandrapportage december 2023.pdf")
text_output_csv = os.path.join(script_dir, "extracted_text.csv")
text_output_txt = os.path.join(script_dir, "extracted_text.txt")

# Function to remove footers from text
def remove_footer(text):
    footer_pattern = r'Page \d+ of \d+.*?© Atradius.*?$'
    cleaned_text = re.sub(footer_pattern, '', text, flags=re.MULTILINE)
    return cleaned_text.strip()

# Function to clean the text by removing unnecessary characters
def clean_text(text):
    text = re.sub(r'[^\x09\x0A\x0D\x20-\x7E]', '', text)  # Remove non-printable characters
    return text

# Function to split text into multiple columns based on spaces
def split_into_positions(line):
    parts = re.split(r'\s{2,}', line)  # Split on 2 or more spaces
    return parts

# Function to extract and clean text from the PDF and save it into CSV and TXT
def extract_and_save_text(pdf_path, csv_output_file, txt_output_file):
    data = []
    all_text = ""
    
    for i, page_layout in enumerate(extract_pages(pdf_path)):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                text = element.get_text()
                cleaned_text = clean_text(remove_footer(text))
                lines = cleaned_text.splitlines()
                for line_num, line in enumerate(lines, start=1):
                    split_content = split_into_positions(line)
                    data.append([line_num, i + 1] + split_content)
                all_text += cleaned_text + "\n"
    
    # Save to CSV with dynamic column names
    max_columns = max(len(row) for row in data) - 2  # Adjusting for "row" and "page" columns
    column_names = ["row", "page"] + [f"position_{i+1}" for i in range(max_columns)]
    df = pd.DataFrame(data, columns=column_names)
    df.to_csv(csv_output_file, index=False)
    print(f"Text extracted and saved to {csv_output_file}")
    
    # Save to TXT
    with open(txt_output_file, 'w', encoding='utf-8') as f:
        f.write(all_text)
    print(f"Text extracted and saved to {txt_output_file}")

# Main execution
extract_and_save_text(pdf_path, text_output_csv, text_output_txt)

print("Aggregate text and CSV extraction completed.")
