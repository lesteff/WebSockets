import time
import threading
import multiprocessing
import math


def my_func(n):
    start_time = time.time()
    result = 0
    for i in range(n):
        for j in range(1000):
            result += math.sqrt(i * j)
    end_time = time.time()
    result_time = end_time - start_time
    print(f"Время выполнения: {round(result_time, 3)} секунд. Результат: {round(result, 3)}")
    return result


if __name__ == '__main__':
    n = 100000
    print("Обычное выполнение")
    my_func(n)

    print("Выполнение в потоке")
    thread = threading.Thread(target=my_func, args=(n,))
    thread.start()
    thread.join()
    print("Поток завершен")

    print("МУЛЬТИПРОЦЕССОРНОЕ ВЫПОЛНЕНИЕ")

    num_cores = multiprocessing.cpu_count()
    print(f"Количество ядер: {num_cores}")

    print(f"\nЗапускаем в {num_cores} процессах...")
    processes = []


    chunk_size = n // num_cores

    start_time = time.time()

    for i in range(num_cores):
        p = multiprocessing.Process(target=my_func, args=(chunk_size,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    end_time = time.time()
    print(f"Общее время выполнения в {num_cores} процессах: {round(end_time - start_time, 3)} секунд")
    print("Все процессы завершены")