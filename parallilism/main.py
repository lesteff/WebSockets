import threading
import time
import multiprocessing

import requests


# print ("Текущий поток: ", threading.current_thread().name)
#
#
# def print_numbers():
#     print("Запуск в потоке", threading.current_thread().name)
#     for i in range(5):
#         time.sleep(1)
#         print(i)
#
#
# def print_letters():
#     for letter in 'abcde':
#         time.sleep(1.5)
#         print(letter)
#
#
#
#
# thread = threading.Thread(target=print_numbers)
# thread_2 = threading.Thread(target=print_letters)
#
#
#
# thread.start()
# thread_2.start()
#
#
# thread.join()
# thread_2.join()
#
# print("Поток завершен")



# def download_content(url):
#     response = requests.get(url)
#     print(f"Содержимое {url} имеет размер {len(response.text)} символов")
#
# urls = [
#     "https://python.org",
#     "https://docs.python.org",
#     "https://peps.python.org",
# ]
#
#
# threads = []
# for url in urls:
#     t = threading.Thread(target=download_content, args=(url,))
#     threads.append(t)
#     t.start()
#
# # Start each thread
# for t in threads:
#     t.join()


def print_number():
    for i in range(5):
        print(i)


if __name__ == '__main__':
    process = multiprocessing.Process(target=print_number)
    process.start()
    process.join()
