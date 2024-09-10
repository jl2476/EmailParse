import imaplib
import email
import re
from email.policy import default
import os
from dotenv import load_dotenv



def get_raw_emails(username=None, password=None, imap_server='imap.gmail.com', folder='inbox', uid=None):
    # Check if credentials are missing
    if not username or not password:
        raise ValueError("Username or password not provided.")
    
    try:
        # Connect to the IMAP server
        mail = imaplib.IMAP4_SSL(imap_server)
        
        # Log in to your email account
        mail.login(username, password)
        
        # Select the mailbox folder (e.g., inbox)
        mail.select(folder)
        
        # Search for the email by UID if provided, otherwise fetch all emails
        if uid:
            # Search for a specific email by its UID
            status, messages = mail.uid('SEARCH', None, f'UID {uid}')
        else:
            # Search for all emails in the folder
            status, messages = mail.search(None, 'ALL')

        # Get the list of email IDs
        email_ids = messages[0].split()

        raw_emails = []
        
        # Fetch each email by its ID
        for email_id in email_ids:
            # Fetch the raw email by ID
            if uid:
                status, msg_data = mail.uid('FETCH', email_id, '(RFC822)')
            else:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
            
            # Extract the raw email content (the RFC822 message)
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    raw_email = response_part[1].decode('utf-8')
                    
                    # Parse the email if you want
                    msg = email.message_from_string(raw_email, policy=default)
                    
                    # Add the raw email to the list
                    raw_emails.append(raw_email)

        # Close the connection to the IMAP server
        mail.logout()
        
        return raw_emails

    except imaplib.IMAP4.error as e:
        print(f"Error logging in or fetching emails: {e}")
        return []


def extract_email_details(raw_email):
    # Parse the raw email
    msg = email.message_from_string(raw_email)
    
    # Extract headers
    sender = msg.get('From')
    recipient = msg.get('To')
    subject = msg.get('Subject')
    
    # Extract email body
    body = ""

    # Check if the email message is multipart (e.g., text and HTML)
    if msg.is_multipart():
        for part in msg.walk():
            # We're only interested in the plain text part (text/plain)
            if part.get_content_type() == 'text/plain':
                body += part.get_payload(decode=True).decode('utf-8')
    else:
        # If the email is not multipart, extract the payload directly
        body = msg.get_payload(decode=True).decode('utf-8')
    
    # Return the extracted details
    return {
        'sender': sender,
        'recipient': recipient,
        'subject': subject,
        'body': body
    }

def extract_links_from_email(raw_email):
    # Parse the raw email
    msg = email.message_from_string(raw_email)
    
    # Initialize an empty string to store email body
    email_body = ""

    # Check if the email message is multipart (with different parts like plain text, HTML, etc.)
    if msg.is_multipart():
        for part in msg.walk():
            # Extract plain text email body
            if part.get_content_type() == "text/plain":
                email_body += part.get_payload(decode=True).decode('utf-8')
    else:
        # If not multipart, extract the payload directly
        email_body = msg.get_payload(decode=True).decode('utf-8')

    # Use regex to find all URLs
    url_pattern = r'(https?://\S+)'
    links = re.findall(url_pattern, email_body)

    return links

def main():
    load_dotenv()
    # Get email credentials from environment variables if not passed directly
    username = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASS')
    
    print(f'Username: {username} \n Password: {password}')
    
    emails = get_raw_emails(username=username, password=password)
    
    links = extract_links_from_email(raw_email=emails)
    
    print(links)

if __name__ == "__main__":
    main()



