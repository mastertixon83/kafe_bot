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

date = datetime.now().strftime('%d.%m.%Y').split('.')
text = f"<b>Шаг [1/5]</b>\n\n Введите дату в формате ДД.ММ.ГГГГ, сегодня {date[0]} {MONTHS[int(date[1]) - 1]} {date[2]} год"
t = "12:00"

print(text)