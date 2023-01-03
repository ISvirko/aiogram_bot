import requests,json

# url = "http://116.203.132.117:14632/WifiMacCollector"
url = "http://127.0.0.1:14632/WifiMacCollector"
# payload = {
#   "Get_status": 1,
#   "Devices": ["5ccf7f0a0013"]
# }

headers = {
  "Content-Type": "application/json"
}

def get_device_status (payload):
    # print (payload)
    response = requests.post(url, json=payload, headers=headers)
    # print (response.json())
    return (response.json())

