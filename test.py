import datetime

delta = datetime.timedelta(days=3)
current_data = datetime.datetime.now().date()
start_data = current_data
end_data = current_data + delta

print(f"start {start_data} end {end_data}")