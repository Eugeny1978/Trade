import time
import datetime

# name = 'time'
# full_name = name + '.time()'
# print(full_name)
# xxx = exec(full_name)
# print(xxx)
n = datetime.datetime.now()
print(n)

name = 'now()'
full_name = 'datetime.datetime.' + name
print(full_name)
xxx = eval(full_name)
print(xxx)



