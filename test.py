k = int(input("Введи К: "))
p = int(input("Введи Р: "))
t = int(input("Введи t: "))

for i in range(k, p + 1):
    if i % 10 == t:
        print(i, end=" ")