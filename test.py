tList = [
    {'table_number': 1, 'time_reservation': '12:00'},
    {'table_number': 2, 'time_reservation': '12:00'}
]

key = "table_number"
val = 3

d = next(filter(lambda d: d.get(key) == val, tList), None)
if d == None: print(d)
else: print(d['time_reservation'])

