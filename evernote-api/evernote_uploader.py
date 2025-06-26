import os
import sys
import argparse
import time
import uuid
import hashlib
import requests
import json
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime

def create_evernote_note(auth_token, title, content, notebook_name=None, tags=None):
    """Create a new note in Evernote using the REST API."""
    try:
        # Evernote API endpoint
        url = "https://www.evernote.com/shard/s1/notestore"
        
        # Format content in ENML (Evernote Markup Language)
        note_content = '<?xml version="1.0" encoding="UTF-8"?>'
        note_content += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
        note_content += '<en-note>'
        
        # Add content paragraphs with proper formatting
        paragraphs = content.split('\n')
        for para in paragraphs:
            if para.strip():
                note_content += f'<div>{para}</div>'
        
        note_content += '</en-note>'
        
        # First, get the notebook GUID if needed
        notebook_guid = None
        if notebook_name:
            notebook_guid = get_notebook_guid(auth_token, notebook_name)
        
        # Create the note using curl command
        curl_command = [
            'curl', '-X', 'POST', 
            f"{url}/createNote",
            '-H', f'Authorization: Bearer {auth_token}',
            '-H', 'Content-Type: application/json',
            '-d', json.dumps({
                'title': title,
                'content': note_content,
                'notebookGuid': notebook_guid,
                'tagNames': tags if tags else []
            })
        ]
        
        # Execute the curl command
        result = subprocess.run(curl_command, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error creating note: {result.stderr}")
            return None
        
        # Parse the response
        response = json.loads(result.stdout)
        if 'guid' in response:
            return response['guid']
        else:
            print(f"Failed to create note: {response.get('error', 'Unknown error')}")
            return None
    
    except Exception as e:
        print(f"Error creating note: {e}")
        return None

def get_notebook_guid(auth_token, notebook_name):
    """Get the GUID of a notebook by name using the REST API."""
    try:
        # Evernote API endpoint
        url = "https://www.evernote.com/shard/s1/notestore"
        
        # List notebooks using curl
        curl_command = [
            'curl', '-X', 'GET', 
            f"{url}/listNotebooks",
            '-H', f'Authorization: Bearer {auth_token}'
        ]
        
        # Execute the curl command
        result = subprocess.run(curl_command, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error listing notebooks: {result.stderr}")
            return None
        
        # Parse the response
        notebooks = json.loads(result.stdout)
        
        for notebook in notebooks:
            if notebook.get('name') == notebook_name:
                return notebook.get('guid')
        
        print(f"Notebook '{notebook_name}' not found. Available notebooks:")
        for notebook in notebooks:
            print(f"  - {notebook.get('name')}")
        
        return None
    
    except Exception as e:
        print(f"Error getting notebook GUID: {e}")
        return None

def create_note_with_direct_curl(config, title, content, notebook_name=None, tags=None):
    """Create a note using a direct curl command with OAuth parameters."""
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
        
        # Generate timestamp and nonce for OAuth
        timestamp = str(int(time.time()))
        nonce = uuid.uuid4().hex
        
        # Evernote API endpoints (try both production and sandbox)
        endpoints = [
            "https://www.evernote.com/shard/s1/notestore",  # Production API
            "https://sandbox.evernote.com/shard/s1/notestore",  # Sandbox API
            "https://www.evernote.com/shard/s1/nl/1/note",   # Alternative endpoint
        ]
        
        for endpoint in endpoints:
            print(f"\nTrying endpoint: {endpoint}")
            
            # Build the curl command with verbose output for debugging
            curl_cmd = ["curl", "-v", "-X", "POST", f"{endpoint}"]
            
            # Add OAuth headers instead of form data (may work better)
            oauth_header = f'OAuth oauth_consumer_key="{config["oauth_consumer_key"]}", '
            oauth_header += f'oauth_signature="{config["oauth_signature"]}", '
            oauth_header += f'oauth_signature_method="{config["oauth_signature_method"]}", '
            oauth_header += f'oauth_timestamp="{timestamp}", '
            oauth_header += f'oauth_nonce="{nonce}", '
            oauth_header += f'oauth_callback="{config["oauth_callback"]}"'
            
            curl_cmd.extend(["-H", f"Authorization: {oauth_header}"])
            curl_cmd.extend(["-H", "Content-Type: application/x-www-form-urlencoded"])
            
            # Add note parameters
            form_data = f"title={title}&content={note_content}"
            
            # Add notebook if specified
            if notebook_name:
                form_data += f"&notebook={notebook_name}"
            
            # Add tags if specified
            if tags and len(tags) > 0:
                form_data += f"&tags={','.join(tags)}"
            
            curl_cmd.extend(["-d", form_data])
            
            # Execute the curl command
            print(f"Creating note: {title}")
            result = subprocess.run(curl_cmd, capture_output=True, text=True)
            
            # Print full response for debugging
            print("Response status code:", result.returncode)
            print("Response headers and info:", result.stderr)
            print("Response body:", result.stdout)
            
            if result.returncode == 0 and ("success" in result.stdout.lower() or "guid" in result.stdout.lower()):
                print("Note created successfully")
                return True
            else:
                print(f"Attempt failed with endpoint {endpoint}")
        
        print("All endpoint attempts failed.")
        return False
        
    except Exception as e:
        print(f"Error creating note with curl: {e}")
        return False

def process_files(input_dir, config, notebook_name=None, tags=None):
    """Process text files and create Evernote notes."""
    if not os.path.exists(input_dir):
        print(f"Input directory not found: {input_dir}")
        return
    
    # Convert tags string to list if provided
    tag_list = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(',')]
    
    # Process each text file
    success_count = 0
    total_count = 0
    
    for filename in sorted(os.listdir(input_dir)):
        if not filename.endswith('.txt'):
            continue
        
        file_path = os.path.join(input_dir, filename)
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
            
            # Try to create the note using OAuth configuration
            success = create_note_with_direct_curl(config, title, content, notebook_name, tag_list)
            
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

def load_evernote_config(config_file):
    """Load Evernote API configuration from a JSON file."""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Validate required fields
        required_fields = ['oauth_consumer_key', 'oauth_signature_method', 
                          'oauth_signature', 'oauth_callback']
        for field in required_fields:
            if field not in config:
                print(f"Error: Missing required field '{field}' in config file")
                return None
        
        return config
    except FileNotFoundError:
        print(f"Error: Config file '{config_file}' not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: Config file '{config_file}' is not valid JSON")
        return None
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Create Evernote notes from text files.')
    parser.add_argument('--input_dir', default="G:/Mijn Drive/Creatief/Creatief poezie/output", 
                        help='Directory containing text files (default: G:/Mijn Drive/Creatief/Creatief poezie/output)')
    parser.add_argument('--notebook', help='Evernote notebook name (optional)')
    parser.add_argument('--tags', help='Comma-separated list of tags to apply (optional)')
    parser.add_argument('--config', default='evernote_config.json', 
                        help='Path to Evernote API configuration file (default: evernote_config.json)')
    
    args = parser.parse_args()
    
    # Load Evernote configuration
    config = load_evernote_config(args.config)
    if not config:
        print("Failed to load Evernote configuration. Please check your config file.")
        return
    
    # Process files
    process_files(args.input_dir, config, args.notebook, args.tags)

if __name__ == "__main__":
    main()