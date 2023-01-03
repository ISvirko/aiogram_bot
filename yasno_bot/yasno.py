import logging
import json, req #test
import asyncio
import time
from datetime import datetime, timedelta
import get_png 

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

    if str(message.from_id) in user_list:        
        text = '''Hey, it's you again :)\nWhat you want me to do?'''      
        
        await bot.send_message(message.chat.id, text, reply_markup= get_start_keyboard(str(message.from_id)))

    else :
        text = '''Hey, you new here? Want to register new device?'''
        user_list[str(message.from_id)] = {"Devices":{},"AutoUpdate": 0}
        markup = types.ReplyKeyboardRemove()
        



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
   
    date_str =  dev[f"{dev['status']}_from"]
    date_object = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

    date_last_time =  dev[f"last_time_{ dev['last_status']}"]
    date_last_time_object = datetime.strptime(date_last_time, '%Y-%m-%d %H:%M:%S')
                                
    elapsed_time = date_last_time_object - date_object

    text = dev["Name"] + " is " + dev["status"] + " for " + str(elapsed_time).split(".")[0]
    await bot.edit_message_text(text, id, callback_query["message"]["message_id"],  reply_markup=get_start_keyboard(id))
                    


@dp.callback_query_handler(callback_args.filter(txt = "stat"))
async def stat_callback_handler(callback_query: types.CallbackQuery, callback_data : dict)  :
    id = str(callback_query["from"]["id"])
    dev_id = str(callback_data["device_id"])
    path = f"{dev_id}_stat.png"


    markup = types.InlineKeyboardMarkup()    
    markup.add( types.InlineKeyboardButton("Day", callback_data = callback_args.new(txt = "statD", device_id = dev_id)),
                types.InlineKeyboardButton("Week", callback_data = callback_args.new(txt = "statW", device_id = dev_id)),
                types.InlineKeyboardButton("Month", callback_data = callback_args.new(txt = "statM", device_id = dev_id))
            )
    markup.add(types.InlineKeyboardButton("<< Return", callback_data = "return"))

    await bot.edit_message_text("Choose time period", id, callback_query["message"]["message_id"],  reply_markup=markup)
    
    # get_png.plot_smth (get_png.get_stat(dev_id),path)
    
    # with open(path, 'rb') as photo:
    #     await bot.send_photo(id, photo)
    # await bot.send_photo( id, callback_query["message"]["message_id"],  reply_markup=get_start_keyboard(id))

@dp.callback_query_handler(callback_args.filter(txt = "statD"))#,callback_args.filter(txt = "statW"),callback_args.filter(txt = "statM"))
@dp.callback_query_handler(callback_args.filter(txt = "statM"))#
@dp.callback_query_handler(callback_args.filter(txt = "statW"))#
async def statP_callback_handler(callback_query: types.CallbackQuery, callback_data : dict)  :
    id = str(callback_query["from"]["id"])
    dev_id = str(callback_data["device_id"])
    path = f"{dev_id}_stat.png"

    if callback_data["txt"] == "statD":
        get_png.plot_smth (get_png.get_stat(dev_id, 24),path)
    elif callback_data["txt"] == "statW":
        get_png.plot_smth (get_png.get_stat(dev_id, 24*7),path)
    else :
        get_png.plot_smth (get_png.get_stat(dev_id, 24*31),path)
        
    with open(path, 'rb') as photo:
        await bot.send_photo(id, photo)


@dp.callback_query_handler(callback_args.filter(txt = "delete"))
async def delete_callback_handler(callback_query: types.CallbackQuery, callback_data : dict)  :
    # print ("delete_callback_handler")

    id = str(callback_query["from"]["id"])
    dev = user_list[id]["Devices"] #for device_id, device_data in
    
    dev.pop(callback_data["device_id"])
    # print (dev)

    updateDB()
    await some_callback_handler(callback_query)



@dp.callback_query_handler(Text(equals='return', ignore_case=True),state=Form.reg_device)
@dp.callback_query_handler(Text(equals='return', ignore_case=True))
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
    #print ("HERE process_name")

    key = str(message.text)
    #print (key)
    payload = {
        "Get_status": 1,
        "Devices": [key]
        }
    status = req.get_device_status (payload)
    #print (status)
    update = status["result"]
    #print (update)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("<< Return", callback_data = "Return"))

  
    if None in update.values() :
        #print ("None in update.values()")
        return await message.answer("There's no registered device with such MAC\nOr you tiped it wrong\nTry again", reply_markup=markup)
    
    else   :
        #print ("ELSE")
        vin = str(message.chat.id) 
        devices = user_list[vin]["Devices"]
        devices.update(update)
        devices[key]["last_status"] = devices[key]["status"]
        
        updateDB()
        
    text = '''New device successfully added'''    
        
    await bot.send_message(message.chat.id, text, reply_markup= get_start_keyboard(str(message.from_id)))

    await state.finish()







def get_start_keyboard(id):
    keyboard = types.InlineKeyboardMarkup()
    
    
    for  device_id, device_data in user_list[id]["Devices"].items():
        keyboard.add(   types.InlineKeyboardButton(device_data['Name'], callback_data = callback_args.new(txt = "status", device_id = device_id)),
                        types.InlineKeyboardButton("stat", callback_data = callback_args.new(txt = "stat", device_id = device_id)),                        
                        types.InlineKeyboardButton("delete", callback_data = callback_args.new(txt = "delete", device_id = device_id))
                    
                    )
        # keyboard.add(types.InlineKeyboardButton("delete", callback_data = callback_args.new(txt = "delete", device_id = device_id)))
    
    button1 = types.InlineKeyboardButton("ADD Device", callback_data="add_device")
   
    if user_list[id]["AutoUpdate"]:
        button3 = types.InlineKeyboardButton("AutoUpdate On", callback_data="AutoUpdate")
    else:
        button3 = types.InlineKeyboardButton("AutoUpdate Off", callback_data="AutoUpdate")

    keyboard.add(button1, button3)
    return (keyboard)





async def cmd_with_timeout(sleep_for):
    while True:
        await asyncio.sleep(sleep_for)
        #print("cmd_with_timeout(sleep_for)")
        devices_lst =[]

        for user, data in user_list.items():
            devices = data.get("Devices")
            devices_lst += (list(devices.keys())  )

        payload = {
            "Get_status": 1,
            "Devices": devices_lst
            }

        response = req.get_device_status(payload = payload)
        # print(response)
        for user, data in user_list.items():
            devices = data.get("Devices")
            if devices:
                for device_id, device_data in devices.items():
                    update = response["result"].get(device_id)
                    # print (update)
                    if update:
                        device_data.update(update)
                        updateDB() 
                        # print(update['status'], device_data['last_status'])
                        if update['status'] == device_data['last_status']:
                            # print( "update['status'] == device_data['last_status']" )
                            pass
                        else:
                            # print( "ELSE update" )
                            device_data.update(update)

                            date_str =  device_data[f"{ device_data['last_status']}_from"]
                            date_object = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                            
                            date_last_time =  device_data[f"last_time_{ device_data['last_status']}"]
                            date_last_time_object = datetime.strptime(date_last_time, '%Y-%m-%d %H:%M:%S')
                                                        
                            elapsed_time = date_last_time_object - date_object

                            await bot.send_message(user, device_data["Name"]+" was " + device_data['last_status'] + " for " + str(elapsed_time).split(".")[0] +"\nNow it's " + update['status'])
                        
                            device_data['last_status'] = update['status']
                            




def updateDB():
    # print ("in update db")
    with open("db.json", "w") as data_file:
        json.dump(user_list, data_file, indent=2)
    return    

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(cmd_with_timeout(65))

    executor.start_polling(dp, skip_updates=True)