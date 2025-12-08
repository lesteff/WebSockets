import threading
import time
import random
from queue import Queue
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


class OrderStatus(Enum):
    PENDING = "ожидает обработки"
    PROCESSING = "в обработке"
    COMPLETED = "выполнен"
    FAILED = "не выполнен"


@dataclass
class Order:
    id: int
    required_resources: List[str]
    processing_time: float
    status: OrderStatus = OrderStatus.PENDING
    assigned_worker: Optional[str] = None

    def process(self, worker_name: str):
        self.status = OrderStatus.PROCESSING
        self.assigned_worker = worker_name
        time.sleep(self.processing_time)
        self.status = OrderStatus.COMPLETED
        return True


class Worker:
    def __init__(self, name: str):
        self.name = name
        self.is_busy = False
        self.completed_orders = 0

    def work_on_order(self, order: Order, order_lock: threading.Lock):
        try:
            print(f"Работник {self.name} начинает обработку заказа {order.id}")
            self.is_busy = True
            success = order.process(self.name)

            with order_lock:
                if success:
                    order.status = OrderStatus.COMPLETED
                    self.completed_orders += 1
                    print(f"✓ Работник {self.name} завершил заказ {order.id} "
                          f"(время: {order.processing_time}с, ресурсы: {order.required_resources})")
                else:
                    order.status = OrderStatus.FAILED
                    print(f"✗ Работник {self.name} не смог обработать заказ {order.id}")

        except Exception as e:
            print(f"Ошибка при обработке заказа {order.id}: {e}")
        finally:
            self.is_busy = False
        return success


class OrderProcessingSystem:
    """Система обработки заказов с ограниченными ресурсами"""

    def __init__(self, max_concurrent_workers: int):
        self.worker_semaphore = threading.Semaphore(max_concurrent_workers)
        self.order_queue = Queue()
        self.order_lock = threading.Lock()
        self.processed_orders = 0
        self.total_orders = 0
        self.statistics_lock = threading.Lock()

        self.workers = [
            Worker(f"Worker-{i}") for i in range(1, max_concurrent_workers + 2)
        ]


        self.shutdown_flag = False
        self.shutdown_lock = threading.Lock()

    def add_order(self, order: Order):
        with self.order_lock:
            self.order_queue.put(order)
            self.total_orders += 1
            print(f"Добавлен заказ {order.id}: ресурсы={order.required_resources}, "
                  f"время={order.processing_time}с")

    def worker_thread(self, worker: Worker):
        while True:

            with self.shutdown_lock:
                if self.shutdown_flag and self.order_queue.empty():
                    break


            if not self.worker_semaphore.acquire(timeout=1):
                continue

            try:
                try:
                    order = self.order_queue.get(timeout=1)
                except:
                    self.worker_semaphore.release()
                    continue

                worker.work_on_order(order, self.order_lock)

                with self.statistics_lock:
                    self.processed_orders += 1
                self.order_queue.task_done()

            except Exception as e:
                print(f"Ошибка в потоке работника {worker.name}: {e}")
            finally:
                self.worker_semaphore.release()

    def start_processing(self):
        """Запуск системы обработки заказов"""
        print(f"\n{'=' * 60}")
        print(f"Запуск системы обработки заказов")
        print(f"Максимально работников одновременно: {self.worker_semaphore._value}")
        print(f"Всего работников в системе: {len(self.workers)}")
        print(f"{'=' * 60}\n")

        threads = []
        for worker in self.workers:
            thread = threading.Thread(
                target=self.worker_thread,
                args=(worker,),
                name=f"Thread-{worker.name}",
                daemon=True
            )
            threads.append(thread)
            thread.start()

        return threads

    def stop_processing(self):
        """Остановка системы обработки"""
        with self.shutdown_lock:
            self.shutdown_flag = True

        print("\nЗавершение работы системы...")
        time.sleep(2)

    def print_statistics(self):
        """Вывод статистики"""
        print(f"\n{'=' * 60}")
        print("СТАТИСТИКА ОБРАБОТКИ ЗАКАЗОВ:")
        print(f"{'=' * 60}")
        print(f"Всего заказов в системе: {self.total_orders}")
        print(f"Обработано заказов: {self.processed_orders}")
        print(f"Заказов в очереди: {self.order_queue.qsize()}")
        print(f"\nРезультаты работы работников:")

        for worker in self.workers:
            print(f"  {worker.name}: {worker.completed_orders} заказов "
                  f"{'(занят)' if worker.is_busy else '(свободен)'}")

        print(f"{'=' * 60}")


def generate_sample_orders(num_orders: int) -> List[Order]:
    """Генерация тестовых заказов"""
    resources_options = [
        ["принтер", "сканер"],
        ["станок"],
        ["компьютер", "монитор"],
        ["склад"],
        ["грузовик", "погрузчик"]
    ]

    orders = []
    for i in range(1, num_orders + 1):
        resources = random.choice(resources_options)
        processing_time = random.uniform(0.5, 3.0)
        orders.append(Order(
            id=i,
            required_resources=resources,
            processing_time=processing_time
        ))
    return orders


def main():
    """Основная функция демонстрации"""
    system = OrderProcessingSystem(max_concurrent_workers=3)

    orders = generate_sample_orders(10)


    for order in orders:
        system.add_order(order)


    threads = system.start_processing()


    time.sleep(2)
    print("\n--- Добавление дополнительных заказов во время работы ---")

    additional_orders = generate_sample_orders(5)
    for order in additional_orders:
        order.id += 100
        system.add_order(order)
        time.sleep(random.uniform(0.1, 0.5))

    while not system.order_queue.empty():
        time.sleep(1)
        print(f"Ожидающих заказов: {system.order_queue.qsize()}")


    time.sleep(5)


    system.stop_processing()
    system.print_statistics()


    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ПРЕДОТВРАЩЕНИЯ ВЗАИМНОЙ БЛОКИРОВКИ")
    print("=" * 60)
    print("1. Семафор ограничивает одновременный доступ к ресурсам")
    print("2. Мьютекс защищает обновление статусов заказов")
    print("3. Очередь заказов обеспечивает FIFO обработку")
    print("4. Таймауты в acquire() предотвращают deadlock")
    print("=" * 60)


if __name__ == "__main__":
    main()