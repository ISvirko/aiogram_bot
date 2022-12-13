import logging
import json, test

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor

API_TOKEN = '989604812:AAE1NWU3CwhDfo41ucg80nE2aboimTmlDtQ'

# Configure logging
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)

# Initialize bot and dispatcher
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

user_list = {}

try:
    with open("db.json", 'r') as read_file:
        user_list = json.load(read_file)
except Exception as E:
    print (E)

# States
class Form(StatesGroup):
    reg_device = State()  # Will be represented in storage as 'Form:name'
    reg_dev_name = State()  # Will be represented in storage as 'Form:age'


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await Form.reg_device.set()
    print (message.from_id, message.from_user)

    if user_list[message.from_id]:        
        text = '''Hey, you new here? Want to register new device?'''
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("AutoUpdate", "GetStatus")
        markup.add("Add new device")
        markup.add("Cancel")
    else :
        text = '''Hey, you new here? Want to register new device?'''
        user_list[message.from_id] = {}
        markup = types.ReplyKeyboardRemove()

    await message.reply(text, reply_markup=markup) #

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Form.reg_device)
async def process_name(message: types.Message, state: FSMContext):
    print (message.text)
    status = test.get_device_status({message.text:""})
    print (status)
    if "NotFound" not in status.values() :
        for key in status:
            print(key + ':', status[key])
            user_list[message.from_id][key] = status[key]
        updateDB()
    else   :
        return await message.reply("There's no registered device with such MAC\nTry another")

    await state.finish()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("AutoUpdate", "GetStatus")
    markup.add("Add new device")
    markup.add("Cancel")

    await message.reply("Now what?", reply_markup=markup)





@dp.message_handler(Text(equals='Add new device', ignore_case=True))
async def cancel_handler(message: types.Message):
    await Form.reg_device.set()
    await message.reply('Enter new device id')


@dp.message_handler(Text(equals='GetStatus', ignore_case=True))
async def cancel_handler(message: types.Message):
    
    status = test.get_device_status(user_list[str(message.from_id)])

    print (status)
    for key in status:
        await message.answer ('id '+ key + ' is '+ status[key])

    updateDB()





def updateDB():
    print ("in update db")
    with open("db.json", "w") as data_file:
        json.dump(user_list, data_file, indent=2)
    return

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)