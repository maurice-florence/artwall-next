import imaplib
import email
from email.header import decode_header
import os
import logging
import uuid
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

USERNAME = r"johannesrenders@yahoo.ca"
PASSWORD = r"wPX2E^vY&BjSr1t#2x71"

# Debug: Print loaded variables
print("Debug: YAHOO_USERNAME =", USERNAME)
print("Debug: YAHOO_PASSWORD =", PASSWORD)

IMAP_SERVER = "imap.mail.yahoo.com"

# Directory to save attachments
ATTACHMENT_DIR = r"C:\Users\friem\Downloads\attachments"
os.makedirs(ATTACHMENT_DIR, exist_ok=True)

def clean_filename(filename):
    """Ensure filenames are safe and unique."""
    safe_name = "_".join(filename.split()) if filename else "unnamed"
    return f"{safe_name}_{uuid.uuid4().hex}"

def fetch_attachments(mailbox):
    """Fetch attachments from the specified mailbox."""
    logging.info(f"Accessing mailbox: {mailbox}")
    status, _ = mail.select(mailbox)
    if status != "OK":
        logging.error(f"Failed to access mailbox: {mailbox}")
        return

    # Search for all emails
    status, messages = mail.search(None, "ALL")
    if status != "OK":
        logging.error(f"Failed to fetch emails from {mailbox}")
        return

    email_ids = messages[0].split()
    logging.info(f"Found {len(email_ids)} emails in {mailbox}")

    for email_id in email_ids:
        try:
            # Fetch the email by ID
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            if status != "OK":
                logging.warning(f"Failed to fetch email ID {email_id}")
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # Parse the email content
                    msg = email.message_from_bytes(response_part[1])

                    for part in msg.walk():
                        content_disposition = part.get("Content-Disposition")
                        if content_disposition:
                            filename = part.get_filename()
                            if filename:
                                decoded_filename = decode_header(filename)[0][0]
                                if isinstance(decoded_filename, bytes):
                                    decoded_filename = decoded_filename.decode(errors="ignore")
                                safe_filename = clean_filename(decoded_filename)
                                filepath = os.path.join(ATTACHMENT_DIR, safe_filename)
                                with open(filepath, "wb") as f:
                                    f.write(part.get_payload(decode=True))
                                logging.info(f"Downloaded: {safe_filename}")
                            else:
                                logging.warning("Attachment found with no filename; skipping.")
        except Exception as e:
            logging.error(f"Error processing email ID {email_id}: {e}")

def main():
    global mail
    try:
        # Check if credentials are loaded
        if not USERNAME or not PASSWORD:
            logging.error("Environment variables for Yahoo credentials not loaded. Check .env file.")
            return

        # Connect to the Yahoo IMAP server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        try:
            mail.login(USERNAME, PASSWORD)
        except imaplib.IMAP4.error as e:
            logging.error(f"Login failed: {e}")
            return

        # List all mailboxes
        status, mailboxes = mail.list()
        if status != "OK":
            logging.error("Failed to list mailboxes")
            return

        # Iterate through all mailboxes
        mailboxes_list = []
        for box in mailboxes:
            parts = box.split()
            if len(parts) > 0:
                mailbox = parts[-1]
                if isinstance(mailbox, bytes):
                    try:
                        decoded_mailbox = mailbox.decode("utf-8")
                        mailboxes_list.append(decoded_mailbox)
                    except Exception as e:
                        logging.warning(f"Failed to decode mailbox name: {mailbox}, error: {e}")

        for mailbox in mailboxes_list:
            fetch_attachments(mailbox)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        if 'mail' in locals() and mail.state == 'SELECTED':
            try:
                mail.close()
            except Exception as e:
                logging.warning(f"Error closing mail connection: {e}")
        if 'mail' in locals():
            try:
                mail.logout()
            except Exception as e:
                logging.warning(f"Error logging out: {e}")

if __name__ == "__main__":
    main()
