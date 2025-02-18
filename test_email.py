import smtplib
from email.mime.text import MIMEText
import os
import email
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from extract_eml import extract_text_and_metadata_from_eml


def send_text_email():
    # Email content
    DOMAIN = os.getenv("DOMAIN")
    TEST_ID = os.getenv("TEST_ID")
    subject = "Test Email"
    body = "This is a test email sent using Python."
    sender = f"{TEST_ID}@{DOMAIN}"
    recipient = f"{TEST_ID}@{DOMAIN}"

    # Create the email message
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg["Date"] = email.utils.formatdate(localtime=True)
    # Connect to the SMTP server and send the email
    try:
        with smtplib.SMTP("localhost", 25) as server:
            server.sendmail(sender, [recipient], msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email to {recipient}: {e}", sender, recipient)


def load_email_from_eml(eml_path):
    """Load an email message from an .eml file."""
    with open(eml_path, "rb") as f:
        return email.message_from_binary_file(f)


def send_eml_email():
    """Test loading and parsing an email from an .eml file."""
    # Email content
    DOMAIN = os.getenv("DOMAIN")
    TEST_ID = os.getenv("TEST_ID")
    recipient = f"{TEST_ID}@{DOMAIN}"
    # Example usage
    eml_path = Path("./email.eml")
    if eml_path.exists():
        msg = load_email_from_eml(eml_path)
        print(f"From: {msg['from']}")
        print(f"Subject: {msg['subject']}")
        print(f"To: {msg['to']}")
    # Connect to the SMTP server and send the email
    try:
        with smtplib.SMTP("localhost", 25) as server:
            server.sendmail(msg["from"], [recipient], msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email to {recipient}: {e}", msg["from"], recipient)


if __name__ == "__main__":
    # send_text_email()
    send_eml_email()
