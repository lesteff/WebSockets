import threading
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass


@dataclass
class MovieSchedule:
    movie_id: str
    movie_title: str
    start_time: datetime
    hall_capacity: int


class CinemaHall:
    def __init__(self, hall_id: str, capacity: int):
        self.hall_id = hall_id
        self.capacity = capacity
        self.available_seats = set(range(1, capacity + 1))
        self.lock = threading.Lock()
        self.condition = threading.Condition()
        self.reservation_log = []
        self.log_lock = threading.Lock()

class CinemaBookingSystem:
    def __init__(self):
        self.movies_schedule: Dict[str, MovieSchedule] = {}
        self.halls: Dict[str, CinemaHall] = {}
        self.booking_semaphore = threading.Semaphore(4)
        self.init_lock = threading.Lock()
        self.waiting_queue: List[Tuple[str, int, List[int]]] = []
        self.queue_lock = threading.Lock()
        self.initialized = False

        self._initialize_data()

    def _initialize_data(self):
        with self.init_lock:
            if not self.initialized:
                self.halls = {
                    "hall_a": CinemaHall("hall_a", 50),
                    "hall_b": CinemaHall("hall_b", 40),
                    "hall_c": CinemaHall("hall_c", 60),
                    "hall_d": CinemaHall("hall_d", 30),
                }

                now = datetime.now()
                self.movies_schedule = {
                    "m1": MovieSchedule("m1", "Интерстеллар", now + timedelta(hours=2), 50),
                    "m2": MovieSchedule("m2", "Начало", now + timedelta(hours=3), 40),
                    "m3": MovieSchedule("m3", "Матрица", now + timedelta(hours=1), 60),
                    "m4": MovieSchedule("m4", "Титаник", now + timedelta(hours=4), 30),
                    "m5": MovieSchedule("m5", "Аватар", now + timedelta(hours=5), 50),
                }

                self.movie_to_hall = {
                    "m1": "hall_a",
                    "m2": "hall_b",
                    "m3": "hall_c",
                    "m4": "hall_d",
                    "m5": "hall_a",
                }

                self.initialized = True

    def get_available_movies(self) -> List[Dict]:
        available = []
        current_time = datetime.now()

        for movie_id, schedule in self.movies_schedule.items():
            if schedule.start_time > current_time:
                hall_id = self.movie_to_hall[movie_id]
                hall = self.halls[hall_id]

                with hall.lock:
                    available_seats = len(hall.available_seats)

                available.append({
                    'id': movie_id,
                    'title': schedule.movie_title,
                    'time': schedule.start_time.strftime("%H:%M"),
                    'available_seats': available_seats,
                    'total_seats': schedule.hall_capacity
                })

        return available

    def check_seat_availability(self, movie_id: str, seat_numbers: List[int]) -> bool:
        if movie_id not in self.movie_to_hall:
            return False

        hall_id = self.movie_to_hall[movie_id]
        hall = self.halls[hall_id]

        with hall.lock:
            return all(seat in hall.available_seats for seat in seat_numbers)

    def book_seats(self, movie_id: str, user_id: int, seat_numbers: List[int],
                   max_wait_time: float = 2.0) -> Tuple[bool, str]:
        """
        Забронировать места на фильм

        Args:
            movie_id: ID фильма
            user_id: ID пользователя
            seat_numbers: список номеров мест
            max_wait_time: максимальное время ожидания (секунды)

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        start_time = time.time()

        if movie_id not in self.movies_schedule:
            return False, f"Фильм с ID {movie_id} не найден"

        movie = self.movies_schedule[movie_id]

        if datetime.now() >= movie.start_time:
            return False, f"Сеанс фильма '{movie.movie_title}' уже начался"

        hall_id = self.movie_to_hall.get(movie_id)
        if not hall_id or hall_id not in self.halls:
            return False, f"Зал для фильма '{movie.movie_title}' не найден"

        hall = self.halls[hall_id]

        if not self.booking_semaphore.acquire(timeout=max_wait_time):
            return False, f"Превышено время ожидания начала бронирования"

        try:
            with hall.condition:
                wait_start = time.time()

                while time.time() - wait_start < max_wait_time:
                    with hall.lock:
                        all_available = all(seat in hall.available_seats for seat in seat_numbers)
                        valid_seats = all(1 <= seat <= hall.capacity for seat in seat_numbers)

                        if not valid_seats:
                            return False, f"Неверные номера мест. В зале всего {hall.capacity} мест"

                        if all_available:

                            for seat in seat_numbers:
                                hall.available_seats.remove(seat)

                            with hall.log_lock:
                                hall.reservation_log.append({
                                    'user_id': user_id,
                                    'movie_id': movie_id,
                                    'movie_title': movie.movie_title,
                                    'seats': seat_numbers,
                                    'time': datetime.now(),
                                    'booking_time': time.time() - start_time
                                })
                            hall.condition.notify_all()

                            message = (f"Пользователь {user_id}: Успешно забронировал места {seat_numbers} "
                                       f"на фильм '{movie.movie_title}' в {movie.start_time.strftime('%H:%M')}. "
                                       f"Осталось мест: {len(hall.available_seats)}")
                            print(message)
                            return True, message

                    remaining_time = max_wait_time - (time.time() - wait_start)
                    if remaining_time > 0:
                        hall.condition.wait(timeout=min(1.0, remaining_time))

                return False, f"Не удалось забронировать места {seat_numbers} - они заняты"

        finally:
            self.booking_semaphore.release()

    def release_seats(self, movie_id: str, seat_numbers: List[int]) -> bool:
        if movie_id not in self.movie_to_hall:
            return False

        hall_id = self.movie_to_hall[movie_id]
        if hall_id not in self.halls:
            return False

        hall = self.halls[hall_id]

        with hall.lock:
            all_occupied = all(seat not in hall.available_seats for seat in seat_numbers)
            valid_seats = all(1 <= seat <= hall.capacity for seat in seat_numbers)

            if not all_occupied or not valid_seats:
                return False


            for seat in seat_numbers:
                hall.available_seats.add(seat)


            with hall.condition:
                hall.condition.notify_all()

            movie = self.movies_schedule[movie_id]
            print(f"Места {seat_numbers} освобождены на фильм '{movie.movie_title}'. "
                  f"Доступно мест: {len(hall.available_seats)}")

            return True

    def process_group_booking(self, movie_id: str, group_id: int,
                              seat_requests: List[List[int]]) -> Dict:
        """
        Обработка группового бронирования

        Args:
            movie_id: ID фильма
            group_id: ID группы
            seat_requests: список запросов на места для каждого члена группы

        Returns:
            Dict: результаты бронирования
        """
        results = {
            'group_id': group_id,
            'movie_id': movie_id,
            'successful': [],
            'failed': [],
            'total_time': 0
        }

        start_time = time.time()

        for i, seats in enumerate(seat_requests):
            user_id = group_id * 100 + i + 1
            success, message = self.book_seats(movie_id, user_id, seats)

            if success:
                results['successful'].append({
                    'user_id': user_id,
                    'seats': seats,
                    'message': message
                })
            else:
                results['failed'].append({
                    'user_id': user_id,
                    'seats': seats,
                    'message': message
                })

        results['total_time'] = time.time() - start_time
        return results

    def get_hall_statistics(self, hall_id: str) -> Dict:
        if hall_id not in self.halls:
            return {}

        hall = self.halls[hall_id]

        with hall.lock:
            available = len(hall.available_seats)

        with hall.log_lock:
            total_bookings = len(hall.reservation_log)

        return {
            'hall_id': hall_id,
            'capacity': hall.capacity,
            'available_seats': available,
            'occupied_seats': hall.capacity - available,
            'total_bookings': total_bookings
        }


def simulate_concurrent_bookings(system: CinemaBookingSystem, num_users: int):
    print(f"\n{'=' * 60}")
    print(f"Симуляция {num_users} конкурентных бронирований")
    print(f"{'=' * 60}")

    threads = []
    results = []
    results_lock = threading.Lock()

    def booking_task(user_id: int):
        movies = system.get_available_movies()
        if not movies:
            with results_lock:
                results.append(f"Пользователь {user_id}: Нет доступных фильмов")
            return


        movie = random.choice(movies)


        hall_id = system.movie_to_hall[movie['id']]
        hall = system.halls[hall_id]

        with hall.lock:
            max_seat = hall.capacity
        num_seats = random.randint(1, 3)
        seats = random.sample(range(1, max_seat + 1), min(num_seats, max_seat))


        success, message = system.book_seats(movie['id'], user_id, seats)

        with results_lock:
            results.append(message)


        if random.random() < 0.1 and success:
            time.sleep(random.uniform(0.5, 1.5))
            system.release_seats(movie['id'], seats)

    for i in range(1, num_users + 1):
        thread = threading.Thread(target=booking_task, args=(i,), name=f"User_{i}")
        threads.append(thread)
        thread.start()

        time.sleep(random.uniform(0.05, 0.2))

    for thread in threads:
        thread.join()

    print(f"\nРезультаты бронирования:")
    for result in results:
        print(f"  - {result}")


def simulate_group_booking(system: CinemaBookingSystem, num_groups: int):
    print(f"\n{'=' * 60}")
    print(f"Симуляция {num_groups} групповых бронирований")
    print(f"{'=' * 60}")

    movies = system.get_available_movies()
    if not movies:
        print("Нет доступных фильмов для бронирования")
        return

    for group_id in range(1, num_groups + 1):
        movie = random.choice(movies)
        hall_id = system.movie_to_hall[movie['id']]
        hall = system.halls[hall_id]


        group_size = random.randint(2, 4)
        seat_requests = []


        for _ in range(group_size):
            with hall.lock:
                max_seat = hall.capacity
            num_seats = random.randint(1, 2)
            seats = random.sample(range(1, max_seat + 1), min(num_seats, max_seat))
            seat_requests.append(seats)


        results = system.process_group_booking(movie['id'], group_id, seat_requests)

        print(f"\nГруппа {group_id} - Фильм: '{movie['title']}'")
        print(f"  Успешные бронирования: {len(results['successful'])}")
        print(f"  Неудачные бронирования: {len(results['failed'])}")
        print(f"  Общее время обработки: {results['total_time']:.2f} сек")


def stress_test(system: CinemaBookingSystem):

    print(f"\n{'=' * 60}")
    print("СТРЕСС-ТЕСТ: Попытка бронирования одинаковых мест")
    print(f"{'=' * 60}")

    movies = system.get_available_movies()
    if not movies:
        return

    movie = movies[0]
    target_seats = [1, 2, 3, 4, 5]

    def stress_task(thread_id: int):
        seats_to_book = random.sample(target_seats, random.randint(1, 3))
        success, message = system.book_seats(movie['id'], 1000 + thread_id, seats_to_book)

        if "успешно" in message.lower():
            time.sleep(random.uniform(0.3, 0.7))
            system.release_seats(movie['id'], seats_to_book)

    threads = []
    for i in range(10):
        thread = threading.Thread(target=stress_task, args=(i,), name=f"Stress_{i}")
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("Стресс-тест завершен!")


def main():
    """Основная функция"""
    print("=" * 60)
    print("СИСТЕМА БРОНИРОВАНИЯ БИЛЕТОВ В КИНОТЕАТР")
    print("=" * 60)

    print("\nИнициализация системы бронирования...")
    booking_system = CinemaBookingSystem()
    time.sleep(1)


    print("\nДОСТУПНЫЕ ФИЛЬМЫ:")
    movies = booking_system.get_available_movies()
    for movie in movies:
        print(f"  • {movie['title']} ({movie['time']}) - "
              f"свободно мест: {movie['available_seats']}/{movie['total_seats']}")

    print("\nСТАТИСТИКА ПО ЗАЛАМ:")
    for hall_id in booking_system.halls:
        stats = booking_system.get_hall_statistics(hall_id)
        print(f"  Зал {hall_id}: {stats['available_seats']}/{stats['capacity']} "
              f"мест свободно (бронирований: {stats['total_bookings']})")
    simulate_concurrent_bookings(booking_system, 8)


    simulate_group_booking(booking_system, 3)


    stress_test(booking_system)


    print(f"\n{'=' * 60}")
    print("ИТОГОВАЯ СТАТИСТИКА")
    print(f"{'=' * 60}")

    total_bookings = 0
    for hall_id in booking_system.halls:
        stats = booking_system.get_hall_statistics(hall_id)
        total_bookings += stats['total_bookings']
        print(f"Зал {hall_id}: {stats['available_seats']}/{stats['capacity']} "
              f"мест свободно, всего бронирований: {stats['total_bookings']}")

    print(f"\nВсего выполнено бронирований: {total_bookings}")
    print("=" * 60)


if __name__ == "__main__":
    main()