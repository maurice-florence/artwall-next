#!/usr/bin/env python3
"""
Signal Chat Exporter Script - FIXED LIST VERSION
===============================================

INSTRUCTIONS:
1. Install: pip install signal-export pandas
2. Close Signal Desktop before running
3. Run: python signal_export.py --list  (now shows ONLY chat names!)

COMMANDS:
- List chats:          python signal_export.py --list
- Export all:          python signal_export.py --all  
- Export group:        python signal_export.py --group "Group Name"
- Parse all:           python signal_export.py --parse-all
- Parse one:           python signal_export.py --parse "Group Name"

Chats → ./signal-export/chats/ | CSVs → ./signal-export/chats-parsed/
"""

import subprocess
import sys
import os
import argparse
import pandas as pd
import re
from pathlib import Path
import io
import logging

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

log_path = Path(__file__).resolve().parent / "signal_export.log"
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_path, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

import tempfile

BASE_DIR = Path(r"G:\Mijn Drive\Backup\Signal\converted")
CHATS_DIR = BASE_DIR / 'chats'
PARSED_DIR = BASE_DIR / 'chats-parsed'

temp_workspace = Path(tempfile.gettempdir()) / "signal_export_workspace"
TEMP_CHATS_DIR = temp_workspace / 'chats'

def run_sigexport_quiet(args):
    """Run sigexport and capture ONLY chat names (no messages)"""
    cmd = ['sigexport', '--list-chats']
    
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUTF8'] = '1'
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8', env=env)
        # Filter to chat names only (skip message content lines)
        output = result.stdout
        lines = output.strip().split('\n')
        
        chats = []
        for line in lines:
            line = line.strip()
            # Skip empty lines, headers, and message content
            if line and not line.startswith(('[', 'Available', 'Exporting')):
                # Extract just the chat name (before first ":")
                if ':' in line:
                    chat_name = line.split(':', 1)[0].strip()
                    if chat_name and chat_name not in chats:
                        chats.append(chat_name)
                else:
                    chats.append(line)
        
        return chats
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ sigexport --list-chats failed: {e.stderr}")
        sys.exit(1)

def list_chats_clean():
    """List ONLY chat names, numbered for easy selection"""
    logger.info("\n📋 Your Signal Groups/Chats:")
    logger.info("=" * 60)
    
    chats = run_sigexport_quiet([])
    if not chats:
        logger.error("❌ No chats found. Check Signal Desktop is closed.")
        return []
    
    for i, chat in enumerate(chats, 1):
        logger.info(f"{i:2d}. {chat}")
    
    logger.info(f"\nTotal: {len(chats)} chats")
    return chats

def ensure_dirs():
    TEMP_CHATS_DIR.parent.mkdir(parents=True, exist_ok=True)
    PARSED_DIR.mkdir(parents=True, exist_ok=True)
    CHATS_DIR.mkdir(parents=True, exist_ok=True)

def export_chats(group_name=None):
    if temp_workspace.exists():
        try:
            import shutil
            shutil.rmtree(temp_workspace, ignore_errors=True)
        except:
            pass
            
    ensure_dirs()
    
    export_args = ['--paginate=0']
    if group_name:
        export_args.extend(['--chats', group_name])
        logger.info(f"📤 Exporting: {group_name}")
    else:
        logger.info("📤 Exporting ALL chats")
    
    cmd = ['sigexport'] + export_args + [str(TEMP_CHATS_DIR)]
    logger.debug(f"Running command: {' '.join(cmd)}")
    
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUTF8'] = '1'
    
    try:
        subprocess.run(cmd, check=True, env=env)
        logger.info("✓ Export complete! Moving files to G: Drive...")
        import shutil
        shutil.copytree(TEMP_CHATS_DIR, CHATS_DIR, dirs_exist_ok=True)
        logger.info("✓ Files moved successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ Export failed. Check Signal Desktop is closed. Details: {e}")
        return False

def parse_chat_md(chat_file):
    try:
        with open(chat_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse Signal format: [date] Name: message
        pattern = r'\[(\d{4}-\d{2}-\d{2}[^\]]*)\]\s*([^:]+?):\s*(.*?)(?=\n\[|\Z)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        if matches:
            df = pd.DataFrame(matches, columns=['Timestamp', 'Sender', 'Message'])
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='mixed', errors='coerce')
            df = df.dropna(subset=['Timestamp'])
            
            # Clean markdown from messages
            df['Message'] = df['Message'].str.replace(r'!\[[^\]]+\]\([^)]+\)', '', regex=True)
            df['Message'] = df['Message'].str.replace(r'\[[^\]]+\]\([^)]+\)', '', regex=True)
            
            chat_name = Path(chat_file).parent.name
            if chat_name == "chats":  # Fallback for old behavior
                chat_name = Path(chat_file).stem
            safe_name = chat_name.replace('/', '_').replace('\\', '_')
            csv_path = PARSED_DIR / f"{safe_name}.csv"
            df.to_csv(csv_path, index=False)
            logger.info(f"✓ Parsed → {csv_path} ({len(df)} messages)")
        else:
            logger.warning(f"⚠️ No messages in {chat_file}")
            
    except Exception as e:
        logger.error(f"✗ Parse error {chat_file}: {e}")

def parse_all_chats():
    md_files = list(CHATS_DIR.rglob('*.md'))
    
    if not md_files:
        logger.error(f"❌ No .md files in '{CHATS_DIR}/'. Export first.")
        return
    
    logger.info(f"🔄 Parsing {len(md_files)} chats...")
    for md_file in md_files:
        parse_chat_md(md_file)
    logger.info("✓ All parsing complete!")

def main():
    parser = argparse.ArgumentParser(description="Signal Chat Exporter", 
                                   formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument('--list', action='store_true', help="List chat names only")
    parser.add_argument('--all', action='store_true', help="Export all chats")
    parser.add_argument('--group', type=str, help="Export specific group")
    parser.add_argument('--parse-all', action='store_true', help="Parse all exported")
    parser.add_argument('--parse', type=str, help="Parse single group MD")
    
    args = parser.parse_args()
    
    if args.list:
        list_chats_clean()
        
    elif args.group:
        export_chats(args.group)
        
    elif args.all:
        export_chats()
        
    elif args.parse_all:
        parse_all_chats()
        
    elif args.parse:
        chat_md = CHATS_DIR / args.parse / "chat.md"
        if not chat_md.exists():
             chat_md = CHATS_DIR / f"{args.parse}.md"
             
        if chat_md.exists():
            parse_chat_md(chat_md)
        else:
            logger.error(f"❌ '{args.parse}' not found. Export first.")
            
    else:
        logger.info("ℹ️ USE:\n  python signal_export.py --list\n  python signal_export.py --group \"My Group\"\n  python signal_export.py --all")

if __name__ == "__main__":
    main()
