import requests
import time
import threading
import multiprocessing

def download_content(url):
    response = requests.get(url)
    print(f"Содержимое {url} имеет размер {len(response.text)} символов")


print("1. ПОСЛЕДОВАТЕЛЬНАЯ ПРОГРАММА:")
urls =["https://python.org",
     "https://docs.python.org",
     "https://peps.python.org"
     ]

start = time.time()
for url in urls:
    download_content(url)
print(f"Время: {time.time() - start:.2f} сек\n")


print("2. МНОГОПОТОЧНАЯ ПРОГРАММА:")
start = time.time()
threads = []
for url in urls:
    t = threading.Thread(target=download_content, args=(url,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
print(f"Время: {time.time() - start:.2f} сек\n")


print("3. МНОГОПРОЦЕССНАЯ ПРОГРАММА:")
start = time.time()
processes = []
for url in urls:
    p = multiprocessing.Process(target=download_content, args=(url,))
    processes.append(p)
    p.start()

for p in processes:
    p.join()
print(f"Время: {time.time() - start:.2f} сек")