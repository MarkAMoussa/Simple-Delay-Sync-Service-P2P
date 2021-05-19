from datetime import timezone
import datetime


# Getting the current date
# and time

utc_time = datetime.datetime.utcnow()
print(utc_time)
utc_timestamp = utc_time.timestamp()
print(type(utc_timestamp))
print(utc_timestamp)
