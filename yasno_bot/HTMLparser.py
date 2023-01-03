import mysql.connector as d_base
from mysql.connector import Error


def get_device_status(device_ids: dict) -> dict:  # input dict with key->str: value->str
    ''' Added column Name row[3] as display name'''
    devices = list(list(device_ids.keys()))  # convert dict to list of keys
    for int_check in devices:  # check if key is string in hex representation
        try:
            int(int_check, 16)
        except Exception as e:
            # print("except: ", e)
            return {"Exception": "Invalid type"}  # if invalid type, return dict like "exception":"<exception type>"
    placeholders = ", ".join(["%s"]*len(devices))  # placeholders <%s> for sql query - count of %s equal to len of list of devices
    try:
        connection = d_base.connect(host='localhost',
                               database='MacData',
                               user='admin',
                               password="ANkd3Qte"
                              )
        cursor = connection.cursor(prepared=True)
        print("Connected table class")
        if connection.is_connected():
            sql_search_query = "select * from DevID WHERE Device_id IN ({})".format(placeholders)  # select * from DevID WHERE Device_id IN (%s %s %s) count of %s depends of list len -> len(devices)
            cursor = connection.cursor(prepared=True)
            cursor.execute(sql_search_query, tuple(devices))  # need cast list of devices to tuple
            rows = cursor.fetchall()
            # print(rows)
            if rows:
                for row in rows:
                    if row[0] in device_ids:
                        device_ids[row[0]] = {"status":row[4], "name" :row[3]}  # row[4] - status [0] - device_id  [1] - random mac(unused) [2] -datetime [3] - name(unused)
            else:
                for device in devices:
                    device_ids[device] = "NotFound"

        else:
            print("Connection error")
    except d_base.Error as error:
        connection.rollback()
        print("Failed inserting data into MySQL table {}".format(error))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            return device_ids  # return: {'112233445566': 'ofline', '5ccf7f0a0013': 'ofline'}
