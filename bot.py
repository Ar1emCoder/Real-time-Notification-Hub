import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
from sqlalchemy import select

from app.database import async_session_maker
from app.models import User
from app.services.notification_sender import send_pending_notifications

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: Message):
    chat_id = str(message.chat.id)

    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.telegram_chat_id == chat_id))
        user = result.scalar_one_or_none()

        if not user:
            user = User(telegram_chat_id=chat_id, timezone="UTC")
            session.add(user)
            await session.commit()
            await message.answer("Привет! Я успешно тебя зарегистрировал.")
        else:
            await message.answer("С возвращением! Ты уже в базе.")


@dp.message(Command("send"))
async def send_handler(message: Message):
    await message.answer("Начинаю отправку уведомлений...")

    async with async_session_maker() as session:
        await send_pending_notifications(bot, session)
    await message.answer("Отправка завершена!")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
