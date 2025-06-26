#!/usr/bin/env python3
import os
import re
import sys
import argparse
from datetime import datetime
import fitz  # PyMuPDF
import xml.etree.ElementTree as ET
from lxml import etree

def extract_from_docx_alternative(file_path):
    """Extract text from a .docx file using direct ZIP extraction."""
    import zipfile
    from xml.dom import minidom
    
    text = []
    with zipfile.ZipFile(file_path) as document:
        # Find all word/document.xml files (handles both .docx and .doc)
        xml_content = None
        for f in document.namelist():
            if f == "word/document.xml":
                xml_content = document.read(f)
                break
        
        if xml_content:
            try:
                dom = minidom.parseString(xml_content)
                text_elements = dom.getElementsByTagName('w:t')
                paragraphs = []
                current_para = ""
                
                for element in text_elements:
                    # Check if there's a paragraph break
                    if element.parentNode.parentNode.parentNode.tagName == 'w:p':
                        # If we're at a new paragraph and have text from previous, add it
                        if element.parentNode.parentNode.parentNode != element.parentNode.parentNode.parentNode.previousSibling and current_para:
                            paragraphs.append(current_para)
                            current_para = ""
                    
                    # Add the text
                    if element.firstChild:
                        current_para += element.firstChild.nodeValue
                
                # Add the last paragraph
                if current_para:
                    paragraphs.append(current_para)
                
                text = "\n".join(paragraphs)
            except Exception as e:
                print(f"Error parsing .docx: {e}")
                text = ""
    
    return text

def extract_from_pdf(file_path):
    """Extract text from a .pdf file."""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_from_odt(file_path):
    """Extract text from an .odt file."""
    try:
        import zipfile
        
        text = []
        with zipfile.ZipFile(file_path) as document:
            # Find the content.xml file
            content = document.read('content.xml')
            
            # Parse the XML
            root = etree.fromstring(content)
            
            # Extract all text nodes
            # ODT uses a namespace, so we need to use the XPath functions
            ns = {'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'}
            paragraphs = root.xpath('//text:p', namespaces=ns)
            
            for p in paragraphs:
                # Get all text content from this paragraph
                paragraph_text = ''.join(p.xpath('.//text()', namespaces=ns))
                if paragraph_text.strip():
                    text.append(paragraph_text)
            
        return '\n'.join(text)
    except Exception as e:
        print(f"Error extracting from ODT: {e}")
        return ""

def extract_from_txt(file_path):
    """Extract text from a .txt file."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return file.read()

def extract_text(file_path):
    """Extract text from different file formats."""
    extension = os.path.splitext(file_path)[1].lower()
    
    if extension in ['.docx', '.doc']:
        return extract_from_docx_alternative(file_path)
    elif extension == '.pdf':
        return extract_from_pdf(file_path)
    elif extension == '.odt':
        return extract_from_odt(file_path)
    elif extension == '.txt':
        return extract_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {extension}")

def split_text(text, delimiter='---'):
    """Split text using the specified delimiter pattern."""
    # Escape special regex characters in the delimiter
    escaped_delimiter = re.escape(delimiter)
    
    # Create pattern based on the delimiter
    if delimiter.strip() == '---':
        # For the dash case, allow for 3 or more dashes
        pattern = r'(-{3,})'
    else:
        # For other delimiters, use exact match
        pattern = f'({escaped_delimiter})'
    
    # Split by pattern
    parts = re.split(pattern, text)
    
    # Filter out the delimiters and empty strings
    sections = []
    for part in parts:
        if part and (
            (delimiter.strip() == '---' and not re.match(r'^-{3,}$', part)) or 
            (delimiter.strip() != '---' and part != delimiter)
        ):
            sections.append(part.strip())
    
    return sections

def save_sections(sections, output_dir, include_date=True, append_line1="", append_line2=""):
    """Save each section to a separate file with optional appended text."""
    os.makedirs(output_dir, exist_ok=True)
    current_date = datetime.now().strftime("%Y%m%d")
    
    for i, section in enumerate(sections, 1):
        if not section.strip():
            continue
            
        file_name = f"text_{i:03d}"
        if include_date:
            file_name += f"_{current_date}"
        
        file_path = os.path.join(output_dir, f"{file_name}.txt")
        
        # Prepare content with appended lines if provided
        content = section
        if append_line1 or append_line2:
            content += "\n\n"  # Add an empty line before appended content
            if append_line1:
                content += f"{append_line1}\n"
            if append_line2:
                content += f"{append_line2}\n"
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
            
        print(f"Created file: {file_path}")

def main():
    parser = argparse.ArgumentParser(description='Extract text sections from documents and save as separate files.')
    parser.add_argument('--input_dir', default="G:/Mijn Drive/Creatief/Creatief poezie/process", 
                        help='Directory containing input files (default: G:/Mijn Drive/Creatief/Creatief poezie/process)')
    parser.add_argument('--output_dir', default="G:/Mijn Drive/Creatief/Creatief poezie/output", 
                        help='Directory for output files (default: G:/Mijn Drive/Creatief/Creatief poezie/output)')
    parser.add_argument('--no_date', action='store_true', help='Exclude date from filenames')
    parser.add_argument('--delimiter', default='---', help='Text delimiter pattern (default: "---")')
    parser.add_argument('--append_line1', default='', help='First line of text to append to each extracted section')
    parser.add_argument('--append_line2', default='', help='Second line of text to append to each extracted section')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_dir):
        print(f"Input directory not found: {args.input_dir}")
        return
    
    processed_any = False
    for filename in os.listdir(args.input_dir):
        file_path = os.path.join(args.input_dir, filename)
        
        if not os.path.isfile(file_path):
            continue
            
        extension = os.path.splitext(filename)[1].lower()
        if extension not in ['.docx', '.doc', '.pdf', '.odt', '.txt']:
            continue
            
        try:
            print(f"Processing {filename}...")
            full_text = extract_text(file_path)
            sections = split_text(full_text, args.delimiter)
            
            if sections:
                save_sections(
                    sections, 
                    args.output_dir, 
                    not args.no_date,
                    args.append_line1,
                    args.append_line2
                )
                processed_any = True
                print(f"Extracted {len(sections)} text sections from {filename}")
            else:
                print(f"No text sections found in {filename}")
                
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
    
    if not processed_any:
        print("No supported files found for processing.")

if __name__ == "__main__":
    main()