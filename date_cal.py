
from datetime import datetime

todayDate = datetime.today()
toDate = todayDate.strftime("%Y-%m-%d")
fromDate = str(todayDate.year-1) + "-" + str(todayDate.month).zfill(2) + "-" +str(todayDate.day).zfill(2)
print(toDate, fromDate)