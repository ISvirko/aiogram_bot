"""
This is a echo bot.
It echoes any incoming text messages.
#my new line
"""

import logging
import HTMLparser
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = '989604812:AAE1NWU3CwhDfo41ucg80nE2aboimTmlDtQ'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")



@dp.message_handler(commands=['shuffle'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    
    await message.reply(HTMLparser.shuffle())


# You can use state '*' if you need to handle all states
@dp.message_handler(commands='cancel')
async def cancel_handler(message: types.Message):
    """
    Allow user to cancel any action
    """
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())





@dp.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)

    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)