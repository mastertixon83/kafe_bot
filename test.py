from datetime import datetime

MONTHS = [
    'Январь',
    'Февраль',
    'Март',
    'Апрель',
    'Май',
    'Июнь',
    'Июль',
    'Август',
    'Сентябрь',
    'Октябрь',
    'Ноябрь',
    'Декабрь',
]

# date = datetime.now().strftime('%d.%m.%Y').split('.')
# print(date)
# text = f"<b>ШАГ [1/4]</b> Выберите дату\n\nСегодня {date[0]} {MONTHS[int(date[1])-1]} {date[2]} года"
print(datetime.now().date())
date = '01.02.2023'
print(datetime.strptime(date, "%d.%m.%Y").date())
try:
    # date = datetime.strptime('12.12.2003', "%d.%m.%Y").date()
    date = '01.02.2023'

    if len(date.split('.')) == 3:
        if (len(date.split('.')[0]) == 2) and (len(date.split('.')[1]) == 2) and (len(date.split('.')[2]) == 4):
            # if date < datetime.now().strftime('%d.%m.%Y'):
            if datetime.strptime(date, "%d.%m.%Y") < datetime.now():
                raise Exception('data error')
        else:
            raise Exception("input error")

except Exception as _ex:
    print(str(_ex))