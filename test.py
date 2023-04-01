def is_prime(n):
   """Проверяет, является ли заданное число простым"""
   sq = int(n ** 0.5) + 1
   if n < 2:
      return False
   for i in range(2, int(n ** 0.5) + 1):
      z = n % i
      if n % i == 0:
         return False
   return True
#
# a = int(input("Введите число а: "))
# b = int(input("Введите число b: "))
a = 1
b = 20
primes = [num for num in range(a, b+1) if is_prime(num)]
print(f"Простые числа между {a} и {b}: ", end="")
print(*primes, sep=" ")
