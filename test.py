from datetime import datetime, timezone

msg = '13 10'
try:
    if len(msg) == 5:
        if " " in msg:
            msg = msg.replace(" ", ":")
        elif "." in msg:
            msg = msg.replace(".", ":")
        elif "-" in msg:
            msg = msg.replace("-", ":")

        msg = msg + ":00"

        time = datetime.strptime(msg, '%H:%M:%S').time()
        if time < datetime.now().time():
            raise Exception('time error')
        print(time)
    # else:
    #     raise ValueError('input error')

except Exception as _ex:
    print("Я вас, к сожалению, не понимаю. Введите время в формате ЧЧ.ММ, ЧЧ:ММ, ЧЧ-ММ или ЧЧ ММ")
    print(_ex)
else:
    print('Vse OK')
