from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("TOKEN_BOT").strip()  # Удаление лишних пробелов и символов

if not BOT_TOKEN:
    raise ValueError("Токен не загружен. Проверьте .env файл или переменные окружения.")
if not isinstance(BOT_TOKEN, str):
    raise ValueError("BOT_TOKEN должен быть строкой!")

print(f"Загруженный токен: {repr(BOT_TOKEN)}")  # Отладочный вывод токена

async def main():
    bot = Bot(BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()

    await bot.delete_webhook(drop_pending_updates=True)

    try:
        print("Бот запущен. Нажмите Ctrl+C для остановки.")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("Остановка работы бота...")
    finally:
        await bot.session.close()
        print("Сессия бота закрыта.")

if __name__ == "__main__":
    try:
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Программа завершена через Ctrl+C.")
