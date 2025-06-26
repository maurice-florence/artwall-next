import os
import sys
import argparse
import json
import requests
from datetime import datetime
import base64
import time
import hashlib
import binascii

def create_note_with_api(token, title, content, notebook_name=None, tags=None):
    """Create a note using Evernote's official REST API."""
    try:
        # Format the content for Evernote
        note_content = '<?xml version="1.0" encoding="UTF-8"?>'
        note_content += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
        note_content += '<en-note>'
        
        # Add content paragraphs
        paragraphs = content.split('\n')
        for para in paragraphs:
            if para.strip():
                note_content += f'<div>{para}</div>'
        
        note_content += '</en-note>'
        
        # Set up the API request
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Prepare the note data
        note_data = {
            'title': title,
            'content': note_content,
            'contentLength': len(note_content)
        }
        
        # Add notebook if specified
        if notebook_name:
            note_data['notebookGuid'] = get_notebook_guid(token, notebook_name)
        
        # Add tags if specified
        if tags:
            note_data['tagNames'] = tags
        
        # Try with different endpoints
        endpoints = [
            "https://api.evernote.com/v1/note",  # Current API
            "https://www.evernote.com/shard/s1/nl/1/note"  # Older API path
        ]
        
        for endpoint in endpoints:
            print(f"Trying endpoint: {endpoint}")
            
            # Make the API request
            response = requests.post(
                endpoint,
                headers=headers,
                json=note_data
            )
            
            # Print response for debugging
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {response.headers}")
            
            try:
                print(f"Response content: {response.json()}")
            except:
                print(f"Response content: {response.text}")
            
            if response.status_code == 200:
                print("Note created successfully!")
                return True
            elif response.status_code == 401:
                print("Authentication error. Please check your token.")
                break
        
        # If we got here, all attempts failed
        print("Failed to create note after trying all endpoints.")
        return False
    
    except Exception as e:
        print(f"Error creating note: {e}")
        return False

def get_notebook_guid(token, notebook_name):
    """Get the GUID of a notebook by name."""
    try:
        # Set up the API request
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Make the API request to get all notebooks
        response = requests.get(
            "https://api.evernote.com/v1/notebooks",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"Failed to get notebooks: {response.text}")
            return None
        
        # Parse the response
        notebooks = response.json()
        
        # Find the notebook by name
        for notebook in notebooks:
            if notebook.get('name') == notebook_name:
                return notebook.get('guid')
        
        print(f"Notebook '{notebook_name}' not found")
        return None
    
    except Exception as e:
        print(f"Error getting notebook GUID: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Create Evernote notes from text files using direct API calls.')
    parser.add_argument('--input_dir', default="G:/Mijn Drive/Creatief/Creatief poezie/upload", 
                        help='Directory containing text files (default: G:/Mijn Drive/Creatief/Creatief poezie/upload)')
    parser.add_argument('--notebook', help='Evernote notebook name (optional)')
    parser.add_argument('--tags', help='Comma-separated list of tags to apply (optional)')
    parser.add_argument('--token', help='Your Evernote developer token')
    parser.add_argument('--token_file', default='evernote_token.txt', help='File containing your Evernote token')
    
    args = parser.parse_args()
    
    # Get the token
    token = args.token
    if not token and os.path.exists(args.token_file):
        with open(args.token_file, 'r') as f:
            token = f.read().strip()
    
    if not token:
        print("Please provide a token either via --token or in a token file")
        return
    
    # Process tags
    tag_list = None
    if args.tags:
        tag_list = [tag.strip() for tag in args.tags.split(',')]
    
    # Process each text file
    success_count = 0
    total_count = 0
    
    for filename in sorted(os.listdir(args.input_dir)):
        if not filename.endswith('.txt'):
            continue
        
        file_path = os.path.join(args.input_dir, filename)
        total_count += 1
        
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
            
            if not content:
                print(f"Skipping empty file: {filename}")
                continue
            
            # Generate a title (use first line or filename)
            title_line = content.split('\n')[0].strip()
            title = title_line if len(title_line) <= 50 else filename.replace('.txt', '')
            
            # Create the note
            success = create_note_with_api(token, title, content, args.notebook, tag_list)
            
            if success:
                print(f"Created note '{title}' from {filename}")
                success_count += 1
            else:
                print(f"Failed to create note from {filename}")
            
            # Delay to avoid rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
    
    print(f"\nSummary: Created {success_count} of {total_count} notes in Evernote")

if __name__ == "__main__":
    main()