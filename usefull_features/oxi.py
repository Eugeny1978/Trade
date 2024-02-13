# import pandas as pd
# import datetime
#
# stamp_date = pd.Timestamp('2014-01-23 00:00:00', tz=None)
# date = stamp_date.to_pydatetime()
# date2 = datetime.date(2014, 1, 23)
# date3 = pd.Timestamp(datetime.date(2014, 1, 23))
#
# print(stamp_date)
# print(date)
# print(date2)
# print(date3)

import datetime
dt = datetime.datetime(2011, 12, 13, 10, 23)
print(dt)
import time
stamp = time.mktime(dt.timetuple())
print(stamp)


