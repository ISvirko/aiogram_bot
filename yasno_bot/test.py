import json, req

import time
from datetime import datetime, timedelta





user_list = {}

try:
    with open("db.json", 'r') as read_file:
        user_list = json.load(read_file)        
except Exception as E:
    print (E)


id = "383621032"
dev = user_list[id]["Devices"]
dev.pop("5ccf7f0a0018")

print (dev)