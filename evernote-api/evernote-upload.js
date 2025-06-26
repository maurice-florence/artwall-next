// evernote-upload.js
const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const readdir = promisify(fs.readdir);
const readFile = promisify(fs.readFile);
const Evernote = require('evernote');

// Configuration
const INPUT_DIR = 'G:/Mijn Drive/Creatief/Creatief poezie/upload';
const TOKEN_FILE = 'evernote_token.txt';

async function main() {
  try {
    // Parse command line arguments
    const args = process.argv.slice(2);
    let notebook = null;
    let tags = [];
    
    for (let i = 0; i < args.length; i++) {
      if (args[i] === '--notebook' && i + 1 < args.length) {
        notebook = args[i + 1];
        i++;
      } else if (args[i] === '--tags' && i + 1 < args.length) {
        tags = args[i + 1].split(',').map(tag => tag.trim());
        i++;
      }
    }
    
    // Read the developer token
    let token;
    try {
      token = fs.readFileSync(TOKEN_FILE, 'utf8').trim();
    } catch (err) {
      console.error('Error reading token file. Please create a file named evernote_token.txt with your developer token.');
      process.exit(1);
    }
    
    // Initialize Evernote client
    const client = new Evernote.Client({
      token: token,
      sandbox: false // Set to true for sandbox environment
    });
    
    // Get the note store
    const noteStore = client.getNoteStore();
    
    // Get notebook GUID if specified
    let notebookGuid = null;
    if (notebook) {
      try {
        const notebooks = await noteStore.listNotebooks();
        const foundNotebook = notebooks.find(nb => nb.name === notebook);
        if (foundNotebook) {
          notebookGuid = foundNotebook.guid;
          console.log(`Found notebook "${notebook}" with GUID: ${notebookGuid}`);
        } else {
          console.log(`Notebook "${notebook}" not found. Available notebooks:`);
          notebooks.forEach(nb => console.log(` - ${nb.name}`));
        }
      } catch (err) {
        console.error('Error listing notebooks:', err);
      }
    }
    
    // Process text files
    try {
      const files = await readdir(INPUT_DIR);
      const textFiles = files.filter(file => file.endsWith('.txt'));
      
      console.log(`Found ${textFiles.length} text files to process`);
      
      let successCount = 0;
      
      for (const file of textFiles) {
        const filePath = path.join(INPUT_DIR, file);
        
        try {
          // Read file content
          const content = await readFile(filePath, 'utf8');
          
          if (!content.trim()) {
            console.log(`Skipping empty file: ${file}`);
            continue;
          }
          
          // Generate a title (use first line or filename)
          const titleLine = content.split('\n')[0].trim();
          const title = titleLine.length <= 50 ? titleLine : file.replace('.txt', '');
          
          // Create Evernote note object
          const note = new Evernote.Types.Note();
          note.title = title;
          
          // Format content in ENML
          let noteContent = '<?xml version="1.0" encoding="UTF-8"?>';
          noteContent += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">';
          noteContent += '<en-note>';
          
          // Add content paragraphs
          const paragraphs = content.split('\n');
          for (const para of paragraphs) {
            if (para.trim()) {
              noteContent += `<div>${para}</div>`;
            }
          }
          
          noteContent += '</en-note>';
          note.content = noteContent;
          
          // Set notebook if specified
          if (notebookGuid) {
            note.notebookGuid = notebookGuid;
          }
          
          // Set tags if specified
          if (tags.length > 0) {
            note.tagNames = tags;
          }
          
          // Create the note
          try {
            const createdNote = await noteStore.createNote(note);
            console.log(`Created note "${title}" with GUID: ${createdNote.guid}`);
            successCount++;
          } catch (err) {
            console.error(`Error creating note from ${file}:`, err);
          }
          
          // Add a small delay to avoid rate limits
          await new Promise(resolve => setTimeout(resolve, 1000));
          
        } catch (err) {
          console.error(`Error processing ${file}:`, err);
        }
      }
      
      console.log(`\nSummary: Created ${successCount} of ${textFiles.length} notes in Evernote`);
      
    } catch (err) {
      console.error('Error reading directory:', err);
    }
    
  } catch (err) {
    console.error('Unexpected error:', err);
  }
}

main();
