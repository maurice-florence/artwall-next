import PyPDF2
import pandas as pd
import os

# Script: Extract and Convert PDF
# By: Johannes Renders (j.a.m.renders@minfin.nl)
# Creation Date: 2024-08-28

# This script automates the process of extracting and converting data from a PDF file to an Excel file.
# It performs the following steps:
# 1. Locates the PDF file relative to the script's location.
# 2. Extracts the text content from the PDF file.
# 3. Parses the extracted text row by row.
# 4. Converts the structured data into a Pandas DataFrame with row numbers.
# 5. Saves the DataFrame as an Excel file in the same directory as the script.

# Get the directory where the .py script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define file paths relative to the script's location
pdf_path = os.path.join(script_dir, "Maandrapportage december 2023.pdf")
output_file = os.path.join(script_dir, "Maandrapportage december 2023.xlsx")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

# Function to parse the extracted text and structure it row by row into a dataset
def parse_data(text):
    rows = text.splitlines()  # Split the text into rows based on line breaks
    data = [{"Row Number": i + 1, "Content": row.strip()} for i, row in enumerate(rows) if row.strip()]
    return data

# Function to save the parsed data into a DataFrame and export to Excel
def save_to_excel(data, output_file):
    df = pd.DataFrame(data)
    df.to_excel(output_file, index=False)

# Main execution

# Step 1: Extract text from PDF
text = extract_text_from_pdf(pdf_path)

# Step 2: Parse the extracted text row by row
data = parse_data(text)

# Step 3: Save parsed data to an Excel file
save_to_excel(data, output_file)

print(f"Data has been successfully extracted and saved to {output_file}")
