import mysql.connector as d_base
from mysql.connector import Error
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib import dates as mpl_dates
import numpy as np

def plot_smth(data, save_path):
    plt.style.use('seaborn')
    plt.ylim(0, 2)
    date_format = mpl_dates.DateFormatter('%Y-%m-%d %H:%M:%S')


    dates = data['x']
    y_data = np.array(data['y'])

    plt.plot(dates, y_data)
    plt.yticks(ticks=[0, 1], labels=["Offline", "Online"], rotation=45)
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()

    for i, (x, y) in enumerate(zip(dates, y_data)):
        if i%2 == 0:
            plt.text(x,y, str(x), rotation=90)
    try:
        plt.savefig(save_path)
        plt.clf()
    except Exception as e:
        print(e)


def get_stat(DeviceID, hrs_ago):
    current_time = datetime.now()
    current_time -= timedelta(microseconds=current_time.microsecond)
    # print("Now: ", current_time)
    # print("24 hours ago: ", current_time - timedelta(hours=24))
    day_ago = current_time - timedelta(hours=hrs_ago)
    stat_list = {"x":[], "y":[]}
    # print(stat_list["x"])
    try:
        connection = d_base.connect(host='localhost',
                               database='MacData',
                               user='admin',
                               password="ANkd3Qte"
                              )
        cursor = connection.cursor(prepared=True)
        # print("Connected table class")
        if connection.is_connected():
            sql_search_query = f"select * from {DeviceID} WHERE ( Timestamp BETWEEN '{day_ago}' AND '{current_time}') ORDER BY Id"
            # print(sql_search_query)
            cursor = connection.cursor(prepared=True)
            cursor.execute(sql_search_query)  # need cast list of devices to tuple
            rows = cursor.fetchall()
            # print(rows)
            if rows:
                for row in rows:
                    if row[5]=="online":
                        stat_list["x"].extend([row[2],row[3]])
                        stat_list['y'].extend([1,1])
                    else:
                        stat_list["x"].extend([row[2],row[3]])
                        stat_list['y'].extend([0, 0])
                    # print(row[2], row[3], row[5])
        else:
            print("Connection error")
    except d_base.Error as error:
        connection.rollback()
        print("Failed inserting data into MySQL table {}".format(error))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            return stat_list


# row_data = get_stat()

# plot_smth(row_data,)
