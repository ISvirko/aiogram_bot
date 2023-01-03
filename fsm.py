import random
from datetime import datetime, timedelta

# Set the start and end dates for the week
start_date = datetime(2022, 12, 23)
end_date = start_date + timedelta(days=7)

# Initialize an empty dictionary to store the data
data = {}

# Set the initial previous status to "offline"
prev_status = 'offline'

# Iterate over the days in the week
date = start_date
while date < end_date:
    day_str = date.strftime('%Y-%m-%d')
    data[day_str] = {}
    
    # Generate data for two devices for each day
    for i in range(1, 3):
        device_id = str(i)
        # Determine the current status based on the previous status
        if prev_status == 'offline':
            status = 'online'
        else:
            status = 'offline'
        # Generate random values for the timestamp and last_packet fields
        # Generate a random datetime object
        dt = datetime(date.year, date.month, date.day, random.randint(0, 23), random.randint(0, 59), random.randint(0, 59))

        # Convert the datetime object to a timestamp
        timestamp = dt.timestamp()
        last_packet = timestamp + timedelta(hours=random.randint(1, 6))
        data[day_str][device_id] = {
            'status': status,
            'timestamp': timestamp,
            'last_packet': last_packet
        }
        # Update the previous status
        prev_status = status
        
    # Move to the next day
    date += timedelta(days=1)

# Print the generated data
print(data)
