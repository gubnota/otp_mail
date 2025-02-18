# from fastapi import FastAPI
import telebot
from threading import Thread
from dotenv import load_dotenv
import os
from aiosmtpd.controller import Controller
from email.parser import BytesParser
import time
from email.message import Message

from extract_eml import decode_encoded_string, extract_text_and_metadata_from_eml
from test_email import send_eml_email, send_text_email

# Load environment variables
load_dotenv()

# Initialize FastAPI app and Telegram bot
# app = FastAPI()
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Load from .env file
AUTH_KEY = os.getenv("AUTH_KEY")
DOMAIN = os.getenv("DOMAIN")
TEST_ID = os.getenv("TEST_ID")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in .env file")

bot = telebot.TeleBot(BOT_TOKEN)


class EmailHandler:

    def extract_plain_text(self, msg: Message) -> str:
        """Extracts plain text content from email with proper decoding"""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset("utf-8")
                    return self._safe_decode(payload, charset)
        else:
            payload = msg.get_payload(decode=True)
            charset = msg.get_content_charset("utf-8")
            return self._safe_decode(payload, charset)

        return ""

    def _safe_decode(self, payload: bytes, charset: str) -> str:
        """Safe byte-to-string decoding with error handling"""
        try:
            return payload.decode(charset, errors="replace")
        except LookupError:
            return payload.decode("utf-8", errors="replace")

    async def handle_DATA(self, server, session, envelope):
        try:
            msg = BytesParser().parsebytes(envelope.content)
            from_addr = envelope.mail_from
            to_addr = envelope.rcpt_tos[0]
            subject = msg.get("Subject", "No Subject")
            user_id = to_addr.split("@")[0]

            # Extract and format message content
            # plain_text = self._extract_plain_text(msg)
            text_content = self.extract_plain_text(msg)[:4095]
            if text_content == "":
                text_content = extract_text_and_metadata_from_eml(msg)
            text_content = (
                "From: "
                + from_addr
                + "\n"
                + "Subject: "
                + decode_encoded_string(subject)
                + "\n"
                + text_content
            )
            text_content = text_content[:4095]
            # formatted_msg = self._format_for_telegram(
            #     from_addr=from_addr, subject=subject, body=plain_text, max_length=4096
            # )
            # print(text_content[:400], msg)
            try:
                bot.send_message(chat_id=user_id, text=text_content)
                print(f"Email sent to {user_id}")
            except Exception as e:
                print(f"Telegram send error to {user_id}: {str(e)}")

            return "250 OK"
        except Exception as e:
            print(f"Email handling error: {str(e)}")
            return "550 Error processing message"


# Telegram message handler
@bot.message_handler(func=lambda message: True)
def echo_id(message):
    bot.reply_to(message, f"Your loopback email is: {message.from_user.id}@{DOMAIN}")


def run_bot():
    bot.infinity_polling()


def run_smtp_server():
    handler = EmailHandler()
    controller = Controller(handler, hostname="0.0.0.0", port=25)
    controller.start()


if __name__ == "__main__":
    print("Starting bot and SMTP server...")
    # Start Telegram bot in a separate thread
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # Start SMTP server in a separate thread
    smtp_thread = Thread(target=run_smtp_server)
    smtp_thread.daemon = True
    smtp_thread.start()

    # Send test email
    time.sleep(1)
    # send_text_email()
    # send_eml_email()

    try:
        # Keep main thread alive until keyboard interrupt
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nReceived shutdown signal. Exiting gracefully...")
