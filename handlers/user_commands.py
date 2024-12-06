import random

from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandObject, CommandStart


router = Router()

@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Helloooooooo")


@router.message(Command(commands=["rn", "random-number"])) # /rn 1-100
async def get_random_number(message: Message, command: CommandObject):
    a, b = [int(n) for n in command.args.split("-")]
    rnum = random.randint(a, b)

    await message.reply(f"Random number: {rnum}")


@router.message(Command("test"))
async def test(message: Message, bot: Bot):
    await bot.send_message(message.chat.id, "test")