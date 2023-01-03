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
    
    print (message.from_id, message.from_user)

    if str(message.from_id) in user_list:        
        text = '''Hey, it's you again :)\nWhat you want me to do?'''
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("AutoUpdate", "GetStatus")
        markup.add("Add new device")
        markup.add("Cancel")
    else :
        text = '''Hey, you new here? Want to register new device?'''
        user_list[str(message.from_id)] = {"Devices":{},"AutoUpdate": 0}
        markup = types.ReplyKeyboardRemove()
        await Form.reg_device.set()

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
    status = HTMLparser.get_device_status({message.text:""})
    print (status)

    if "Invalid type" in status.values() :
        return await message.reply("MAC adress must be in HEX values only\nTry again")

    elif "NotFound" not in status.values() :
        # for key in status:
        #     print(key + ':', status[key])
        #     user_list[str(message.from_id)]["Devices"].update(status)
        # ##################################
        for key, value in status.items():
            vin = str(message.chat.id)            
            devices = user_list[vin]["Devices"]
            devices[key] = value
            devices[key]["last_status"] = devices[key]["status"]
            devices[key]["counter"] = time.time()
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
async def add_device(message: types.Message):
    await Form.reg_device.set()
    await message.reply('Enter new device id')


@dp.message_handler(Text(equals='GetStatus', ignore_case=True))
async def GetStatus(message: types.Message):
    
    await bot.delete_message(message.chat.id, message.message_id)

    for device_id, device_data in user_list[str(message.from_id)]["Devices"].items():
        elapsed_time = time.time() - device_data['counter']
        cnt_in_status = timedelta(seconds=elapsed_time)
                   
        await bot.send_message(message.from_id, device_data["name"] + " is " + device_data["status"] + " for " + str(cnt_in_status)[:8])


@dp.message_handler(Text(equals='AutoUpdate', ignore_case=True))
async def AutoUpdate(message: types.Message):
    # await bot.delete_message(message.chat.id, message.message_id)

    if user_list[str(message.chat.id)]["AutoUpdate"]:
        await bot.send_message(message.chat.id, "Now you wont get AutoUpdates...")
        user_list[str(message.chat.id)]["AutoUpdate"] = 0
    else :
        await bot.send_message(message.chat.id,"Now you will get AutoUpdates")
        user_list[str(message.chat.id)]["AutoUpdate"] = 1

    updateDB() 


async def cmd_with_timeout(sleep_for):
    # await asyncio.sleep(20)
    while True:
        await asyncio.sleep(sleep_for)

        devices ={}

        for key in user_list:
            devices.update (user_list[key]["Devices"])

        print (devices)
        response = HTMLparser.get_device_status(devices)
        print (response)
        
        for user, data in user_list.items():
            devices = data.get("Devices")
            if devices:
                for device_id, device_data in devices.items():
                    update = response.get(device_id)
                    print (update)
                    if update:
                        if update['status'] == device_data['last_status']:
                            # device_data['counter'] += 5
                            print(device_id, '  +++  ', update)
                        else:
                            device_data.update(update)
                            elapsed_time = time.time() - device_data['counter']
                            cnt_in_status = timedelta(seconds=elapsed_time)
                            await bot.send_message(user, device_data["name"]+" was " + device_data['last_status'] + " for " + str(cnt_in_status)[:8] +"\nNow it's " + update['status'],disable_notification=True)
                   
                            device_data['last_status'] = update['status']
                            device_data['counter'] = time.time()
                            print(device_id, '  ---   ', update)
                            updateDB() 

        # for user, data in user_list.items():
        #     if data ["AutoUpdate"]:
        #         for devices, device_data in data["Devices"].items():
        #             await bot.send_message(user, device_data["name"] + " " + device_data["status"] + " for " + str(device_data["counter"]) + " minutes",disable_notification=True)
                   
#         for vin, data in user_list.items():
#             devices = data.get("Devices", {})
#             for device_id, device_data in devices.items():
#                 update = response.get(device_id, {})
#                 if update:
#                     device_data.update(update)

#         updateDB()
#    #####################
#         for vin, data in user_list.items():
#             if user_list[vin]["AutoUpdate"]:
#                 devices = data.get("Devices", {})
#                 for device_id, device_data in devices.items():
#                     await bot.send_message(vin, device_data["name"] + " " + device_data["status"] + " for " + str(device_data["counter"]) + " minutes")
                    
        # for key in user_list:
        #     if user_list[key]["AutoUpdate"]:
        #         await bot.send_message(key, "This is a scheduled message.", disable_notification=True)


def updateDB():
    print ("in update db")
    with open("db.json", "w") as data_file:
        json.dump(user_list, data_file, indent=2)
    return

if __name__ == '__main__':
    # dp.loop.create_task(cmd_with_timeout(15))
    loop = asyncio.get_event_loop()
    loop.create_task(cmd_with_timeout(5*60))

    executor.start_polling(dp, skip_updates=True)

