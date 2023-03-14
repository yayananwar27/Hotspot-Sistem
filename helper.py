import time
from datetime import datetime

class get_datetime():
    def __init__(self):
        self.now = datetime.now()
    
    def __str__(self):
        dt_string = self.now.strftime("%Y-%m-%d %H:%M:%S")
        return dt_string
    def unix(self):
        unix_time = int(time.mktime(self.now.timetuple()))
        return unix_time
    
    def unix_to_datetime(self, unix: int):
        self.unixnya = unix
        dt_obj = datetime.fromtimestamp(self.unixnya)
        dt_string = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
        return dt_string
    def datetime_to_unix(self, datetiming):
        self.datetimenya = datetiming
        dt_obj = datetime.strptime(self.datetimenya, "%Y-%m-%d %H:%M:%S")
        unix_time = int(time.mktime(dt_obj.timetuple()))
        return unix_time
        