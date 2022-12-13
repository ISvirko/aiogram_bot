import random

def get_device_status(device_ids: dict) -> dict:
    # print (device_ids)
    for key in device_ids:
        device_ids[key] = random.choice(["OnLine", "OffLine","NotFound"])
    # print (device_ids)
    return device_ids

# nums = {"1515155631": "", "5615615":""}
# print (get_device_status(nums))