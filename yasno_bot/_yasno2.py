import logging
import json, HTMLparser #test
import asyncio
import time
from datetime import datetime, timedelta

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor

from aiogram.utils.callback_data import CallbackData
from aiogram.contrib.middlewares.logging import LoggingMiddleware

API_TOKEN = '989604812:AAE1NWU3CwhDfo41ucg80nE2aboimTmlDtQ'

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
# dp.middleware.setup(LoggingMiddleware())
callback_args = CallbackData('dev_data','txt', 'device_id') 



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
    
    # print (message.from_id)
       

    if str(message.from_id) in user_list:        
        text = '''Hey, it's you again :)\nWhat you want me to do?'''      
        
        await bot.send_message(message.chat.id, text, reply_markup= get_start_keyboard(str(message.from_id)))

    else :
        text = '''Hey, you new here? Want to register new device?'''
        user_list[str(message.from_id)] = {"Devices":{},"AutoUpdate": 0}
        markup = types.ReplyKeyboardRemove()
        

    # await message.reply(text, reply_markup=markup) #


# @dp.callback_query_handler(Text(equals='devices_list', ignore_case=True))
# async def echo(message: types.Message):
#     markup = types.InlineKeyboardMarkup()
#     text = '''Here's list of registered devices'''
#     for  device_id, device_data in user_list[str(message.message.chat.id)]["Devices"].items():
#         markup.add(types.InlineKeyboardButton(device_data['name'], callback_data = device_id))
    
#     markup.add(types.InlineKeyboardButton("<< Return", callback_data = "start"))

#     await bot.edit_message_text(text, message.message.chat.id, message.message.message_id,  reply_markup=markup)


@dp.callback_query_handler(Text(equals='start', ignore_case=True))
async def some_callback_handler(callback_query: types.CallbackQuery)  :
    # print (callback_query.from_user.id)
    # print ("HERE start")
    text = '''What you want me to do?'''  
    await bot.edit_message_text(text, callback_query["from"]["id"], callback_query["message"]["message_id"],  reply_markup=get_start_keyboard(str(callback_query.from_user.id)))


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('You tried...')
    



@dp.callback_query_handler(Text(equals='AutoUpdate', ignore_case=True))
async def AutoUpdate(callback_query: types.CallbackQuery):
    id = str(callback_query["from"]["id"] )
    m_id = str(callback_query["message"]["message_id"])

    user_list[id]["AutoUpdate"] = 0 if user_list[id]["AutoUpdate"] else 1

    await bot.edit_message_reply_markup(id, m_id, reply_markup= get_start_keyboard(id))
   
    updateDB() 



@dp.callback_query_handler(callback_args.filter(txt = "status"))
async def some2_callback_handler(callback_query: types.CallbackQuery, callback_data : dict)  :
   
    id = str(callback_query["from"]["id"])

    dev = user_list[id]["Devices"][callback_data["device_id"]] #for device_id, device_data in
        
    elapsed_time = time.time() - dev['counter']
    cnt_in_status = timedelta(seconds=elapsed_time)
    text = dev["name"] + " is " + dev["status"] + " for " + str(cnt_in_status)[:8]
    await bot.edit_message_text(text, id, callback_query["message"]["message_id"],  reply_markup=get_start_keyboard(id))




@dp.callback_query_handler(Text(equals='return', ignore_case=True),state=Form.reg_device)
async def cancel_query_handler(callback_query: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        # print ("HERE CANCEL do")
        await some_callback_handler(callback_query)
        return

    # Cancel state and inform user about it
    await state.finish()
    # print ("HERE CANCEL")
    await some_callback_handler(callback_query)


@dp.callback_query_handler(Text(equals='add_device', ignore_case=True))
async def add_device(callback_query: types.CallbackQuery):
    await Form.reg_device.set()
    id = str(callback_query["from"]["id"])
    text = 'Enter new device id'
    await bot.send_message(id, text)

@dp.message_handler(state=Form.reg_device)
async def process_name(message: types.Message, state: FSMContext):
    # print ("HERE process_name")
    status = HTMLparser.get_device_status({message.text:""})
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("<< Return", callback_data = "Return"))

    if "Invalid type" in status.values() :
        return await message.answer("MAC adress must be in HEX values only\nTry again", reply_markup=markup)

    elif "NotFound" in status.values() :
        
        return await message.answer("There's no registered device with such MAC\nTry another", reply_markup=markup)
    
    else   :
        for key, value in status.items():
            vin = str(message.chat.id)            
            devices = user_list[vin]["Devices"]
            devices[key] = value
            devices[key]["last_status"] = devices[key]["status"]
            devices[key]["counter"] = time.time()
        updateDB()
        

    await state.finish()















def get_start_keyboard(id):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("ADD Device", callback_data="add_device")
    button2 = types.InlineKeyboardButton("GetStatus", callback_data="GetStatus")
    
    if user_list[id]["AutoUpdate"]:
        button3 = types.InlineKeyboardButton("AutoUpdate On", callback_data="AutoUpdate")
    else:
        button3 = types.InlineKeyboardButton("AutoUpdate Off", callback_data="AutoUpdate")

    keyboard.add(button1, button3)
    # keyboard.add(button2)
    for  device_id, device_data in user_list[id]["Devices"].items():
        keyboard.add(types.InlineKeyboardButton(device_data['name'], callback_data = callback_args.new(txt = "status", device_id = device_id)))

    return (keyboard)












async def cmd_with_timeout(sleep_for):
    # await asyncio.sleep(20)
    while True:
        await asyncio.sleep(sleep_for)

        devices ={}

        for key in user_list:
            devices.update (user_list[key]["Devices"])

        # print (devices)
        response = HTMLparser.get_device_status(devices)
        # print (response)
        
        for user, data in user_list.items():
            devices = data.get("Devices")
            if devices:
                for device_id, device_data in devices.items():
                    update = response.get(device_id)
                    # print (update)
                    if update:
                        if update['status'] == device_data['last_status']:
                            # device_data['counter'] += 5
                            # print(device_id, '  +++  ', update)
                            pass
                        else:
                            device_data.update(update)
                            elapsed_time = time.time() - device_data['counter']
                            cnt_in_status = timedelta(seconds=elapsed_time)
                            await bot.send_message(user, device_data["name"]+" was " + device_data['last_status'] + " for " + str(cnt_in_status)[:8] +"\nNow it's " + update['status'],disable_notification=True)
                   
                            device_data['last_status'] = update['status']
                            device_data['counter'] = time.time()
                            # print(device_id, '  ---   ', update)
                            updateDB() 


def updateDB():
    # print ("in update db")
    with open("db.json", "w") as data_file:
        json.dump(user_list, data_file, indent=2)
    return    

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(cmd_with_timeout(5*60))

    executor.start_polling(dp, skip_updates=True)