import requests

# try:
#     x = int(input("введите число "))
# except ValueError:
#     print("error")
#
# print("finish")




# def flow_ok():
#     print("a: start")
#     try:
#         print("b: try-body")
#         x = 1/0
#         print("C: still in try")
#     except ZeroDivisionError as e:
#         print("d: except",type(e).__name__)
#     print("e: after try/except")
#
# flow_ok()

#
# def inner():
#     1/0
#
# def outer_wrong():
#     try:
#         inner()
#     except ValueError:
#         print("VE")
#
#
#
# def outer_right():
#     try:
#         inner()
#     except ZeroDivisionError:
#         print("ZDE")
#
#
#
# outer_right()



# try:
#     a  = int(input("Введите число: "))
#     x = 100 / a
# except ValueError:
#     print("ошибка ValueError")
# except ZeroDivisionError:
#     print("ошибка ZeroDivisionError")
# else:
#     print(f"результат {x}")
# finally:
#     print("Конец программы")
#
#





# try:
#     url = "https://jsonplaceholder.typicode.com/posts/1"
#     session = requests.Session()
#     response = session.get(url, timeout=5)
#
# except requests.exceptions.Timeout:
#     print("Не успел")
# except requests.exceptions.ConnectionError:
#     print("Не удалось подключится ")
# else:
#     print("Все хорошо")
#     print(response.json())
#     print(response.status_code)
# finally:
#     print("Finally")
#     session.close()


# try:
#     print("2" + 1)
# except:
#     raise


# def sqrt(x):
#     assert x>=0, "Меньше нуля"
#     return x ** 0.5
#
# print(sqrt(-5))


# def apply_discount(product_price, discount):
#     final_price = product_price * (1 - discount)
#     assert 0 <= final_price <= product_price, "Invalid final price"
#     return final_price
#
# print(apply_discount(100, 0.2))

# class MyException(Exception):
#     pass
#
# try:
#     number = int(input("Input value: "))
#     if number == 10:
#         raise MyException("10 не подходит")
#     result = 10 / number
#
# except ValueError:
#     print("Ошибка введено не число")
# except ZeroDivisionError:
#     print("Ошибка деление на ноль")
# except MyException as my:
#     print(my)
# else:
#     print(f"Успех! {result}")
# finally:
#     print("Завершено")
#


