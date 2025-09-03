from math import pi
from datetime import datetime as dt
import timeit

from netaddr.core import num_bits

# a, b , c , d = "ABCD"
# print(a, b, c, d)
#
# a, *b = "ABCD"
# print(a, b)

# d1 = {"x" :1, "y": 2}
# d2 = {"z": 3, **d1}
# print(d2)

# a = 5
# b = 6
# print(a, b)
#
# a, b = b, a
#
# print(a, b)

# name = "Максим"
# age = 24
# print("Меня зовут %s, мне %d лет", age, name)


# value  = 5.1234567
# print("число пи: %.3f" %value)

# print("Hello, my name is {}, I am a {}".format("Maksim", "programmer"))
# print("Steve plays{0} and {1}".format("trumpet", "drums"))
# print("{something} is {adjective}!".format(something="Python", adjective="awesome"))

# str = "Меня зовут {name} мне {age} года"
# print(str.format(name="Maksim", age=24))



# name = "maksim"
# age = 24
# print(f"My name is {name}, I am {age} years old")

# print(f"value pi:{pi:.2f}")

# x = 10
# y = 5
# print(f"{x} x {y} / 2 = {x * y / 2}")
#

# planets = ["Меркурий","Venera", "zemlya", "mars"]
# print(f"mi zivem {planets[2]}")

# name = "Maksim"
# score = 98.456
#
# old_person = timeit.timeit('"Пользователь %s набрал %.1f баллов" % (name, score)', globals=globals())
#
#
# format_method = timeit.timeit('"Пользователь {} набрал {:.1f} баллов".format(name, score)', globals=globals())
#
# f_method = timeit.timeit('"Пользователь {name} набрал {score:.1f} баллов"', globals=globals())
#
# print(f"old_person: {old_person}")
# print(f"format_method {format_method}")
# print(f"f_method: {f_method}")


# a = 5
# b = 10
# #Тернарный оператор
# result = a if a > b else b
# print(result)

# print(a == b)
# print(a != b)
# print(a < b)
# print(a >= b)
# print(a in [1, 5, 10])


# how_old = int(input("Введите ваш возраст: "))
# if 18 <= how_old <= 65:
#     print("Доступ разрешен")
# elif how_old < 18:
#     print("Доступ запрещен")
# else:
#     print("Пора на пенсию")


# for i in range(1,6):
#     print(i)


# amount = 100
# count = 0
# while amount > 0:
#     amount -= 20
#     count += 1
#     print(amount)
# print(f"всего циклов : {count}")
#


# files = ['report1.csv', 'report2.csv', 'report3.csv']
# for file in files:
#     print('processing:', file)


# for i in range(1, 6):
#     print(i, end=" ")
#


# users = {
#     'Alice': 25,
#     'Bob': 30,
#     'Charline':22
# }
#
# for name, age in users.items():
#     print(f"user: {name}   |  age: {age}")


# for i in range(5):
#     if i == 2 or i == 3:
#         continue
#     print(i, end=" ")


# for i in range(5):
#      if i == 2:
#          break
#      print(i, end=" ")
