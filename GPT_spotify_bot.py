import asyncio
from random import choice
from aiogram import Dispatcher, types, Bot

# Initialize the dispatcher and define the command for sending the message
bot=Bot(token="989604812:AAE1NWU3CwhDfo41ucg80nE2aboimTmlDtQ")
dispatcher = Dispatcher(bot)
send_message_command = "/send_random_message"

# Define the coroutine that sends the random message
async def send_random_message():
    while True:
        # Choose a random message from a list of messages
        messages = ["Hello, world!", "How are you?", "Goodbye!"]
        message = choice(messages)

        # # Send the random message to all users who have previously sent the command
        # users = await bot.get_chat_members_count(chat_id=send_message_command)
        # for user in users:
        await dispatcher.bot.send_message(chat_id=383621032, text=message)

        # Sleep for 24 hours before sending the next message
        await asyncio.sleep(25)

# Handle the /send_random_message command
@dispatcher.message_handler(commands=[send_message_command])
async def send_random_message_command(message: types.Message):
    # When the /send_random_message command is received, add the user to the chat
    # where the coroutine is running (which is the send_message_command chat)
    print ("AAAAAAAAAAAAAAAAAA")
    await dispatcher.bot.add_chat_members(chat_id=send_message_command,
                                          user_id=message.from_user.id)

# Use asyncio.run to schedule the coroutine to run concurrently

@dispatcher.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)

    await message.answer(message.text)


asyncio.run(send_random_message())

# Start the bot
dispatcher.start_polling()
