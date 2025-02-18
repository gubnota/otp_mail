from fastapi import FastAPI
from aiogram import Bot, Dispatcher, types
import asyncio
from aiosmtpd.controller import Controller
from email.parser import BytesParser
import os
import traceback
from contextlib import asynccontextmanager
from extract_eml import extract_text_and_metadata_from_eml
from test_email import send_eml_email, send_text_email


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    task = asyncio.create_task(run_smtp())
    yield
    # Shutdown
    task.cancel()


app = FastAPI(lifespan=lifespan)
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot)


class AsyncEmailHandler:
    async def handle_DATA(self, server, session, envelope):
        try:
            msg = BytesParser().parsebytes(envelope.content)
            text_content = extract_text_and_metadata_from_eml(msg)
            user_id = envelope.rcpt_tos[0].split("@")[0]
            print(f"Received 🧧 from {envelope.mail_from} to {user_id}")

            # Validate Telegram ID
            try:
                chat = await bot.get_chat(user_id)
            except (types.ChatNotFound, ValueError):
                print(f"Invalid Telegram ID: {user_id}")
                return "550 Invalid Telegram ID"

            # Format message
            body = self._extract_content(msg)
            await bot.send_message(
                chat_id=user_id,
                text=f"🧧 from {envelope.mail_from}:\n{text_content}",  # body[:3000]
            )
            return "250 OK"

        except Exception as e:
            traceback.print_exc()
            return f"550 Error: {str(e)}"

    def _extract_content(self, msg):
        if msg.is_multipart():
            return "\n".join(
                part.get_payload(decode=True).decode()
                for part in msg.walk()
                if part.get_content_type() == "text/plain"
            )
        return msg.get_payload(decode=True).decode()


async def run_smtp():
    controller = Controller(AsyncEmailHandler(), hostname="0.0.0.0", port=25)
    controller.start()
    await asyncio.sleep(10)
    send_text_email()
    send_eml_email()
    while True:
        await asyncio.sleep(3600)


@app.on_event("startup")
async def startup():
    asyncio.create_task(run_smtp())
