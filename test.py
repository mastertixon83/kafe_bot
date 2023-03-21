import datetime
from datetime import timedelta

current_data = datetime.datetime.now()
delta_t = timedelta(days=1)

run_dt = (current_data + delta_t).year, (current_data + delta_t).month, (current_data + delta_t).day, 10, 30

print(*run_dt)
print(datetime.datetime(*run_dt))
