import datetime

now = datetime.datetime.now().time()
a = datetime.time.fromisoformat('12:30')

print(now < a)