import datetime

date_text = "2023.04.07 18:00:00"
try:
    datetime.date.fromisoformat(date_text)
except ValueError:
    raise ValueError("Incorrect data format, should be YYYY-MM-DD")
