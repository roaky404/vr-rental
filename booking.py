"""
Модуль проверки доступности VR-оборудования и создания бронирования.
Процедурная реализация алгоритма из раздела 6.4 отчёта по практике.
Автор: Бесчеревных Н.А., группа ИКБО-30-24
"""

from datetime import datetime, date
from typing import List, Dict, Optional, Tuple


# Имитация базы данных в виде словарей.
# В реальном проекте здесь будут SQL-запросы к PostgreSQL.

EQUIPMENT_DB: Dict[int, Dict] = {
    1: {
        "id": 1,
        "serial_number": "MQ3-001-A",
        "type": "headset",
        "model": "Meta Quest 3",
        "status": "available",
        "battery_level": 95,
    },
    2: {
        "id": 2,
        "serial_number": "MQ3-002-B",
        "type": "headset",
        "model": "Meta Quest 3",
        "status": "maintenance",
        "battery_level": 40,
    },
    3: {
        "id": 3,
        "serial_number": "HV-003-C",
        "type": "headset",
        "model": "HTC Vive",
        "status": "available",
        "battery_level": 80,
    },
}

DEFECT_ACTS_DB: List[Dict] = [
    {
        "id": 1,
        "equipment_id": 2,
        "description": "Трещина на правой линзе",
        "created_at": "2026-10-15",
        "is_resolved": False,
    },
    {
        "id": 2,
        "equipment_id": 1,
        "description": "Дрифт левого контроллера",
        "created_at": "2026-09-20",
        "is_resolved": True,
    },
]

BOOKING_ITEMS_DB: List[Dict] = [
    {
        "id": 1,
        "booking_id": 100,
        "equipment_id": 3,
        "start_date": "2026-11-10",
        "end_date": "2026-11-12",
    },
]

BOOKINGS_DB: List[Dict] = []
NEXT_BOOKING_ID = 1


def get_equipment(equipment_id: int) -> Optional[Dict]:
    """Получить данные оборудования по id."""
    return EQUIPMENT_DB.get(equipment_id)


def has_active_defects(equipment_id: int) -> bool:
    """Проверить наличие неразрешённых актов дефектовки."""
    for act in DEFECT_ACTS_DB:
        if act["equipment_id"] == equipment_id and not act["is_resolved"]:
            return True
    return False


def count_date_overlaps(
    equipment_id: int, start_date: date, end_date: date
) -> int:
    """
    Подсчитать количество пересечений дат для заданного оборудования.
    Пересечение есть, если start_date < existing_end И end_date > existing_start.
    """
    overlaps = 0
    for item in BOOKING_ITEMS_DB:
        if item["equipment_id"] != equipment_id:
            continue
        existing_start = datetime.strptime(item["start_date"], "%Y-%m-%d").date()
        existing_end = datetime.strptime(item["end_date"], "%Y-%m-%d").date()
        if start_date < existing_end and end_date > existing_start:
            overlaps += 1
    return overlaps


def create_booking(
    equipment_id: int, start_date: date, end_date: date
) -> Tuple[bool, str]:
    """
    Основная функция бронирования.
    Возвращает кортеж (успех, сообщение).
    """
    global NEXT_BOOKING_ID

    # Шаг 1. Получаем данные оборудования
    equipment = get_equipment(equipment_id)
    if equipment is None:
        return False, f"Оборудование с id={equipment_id} не найдено"

    # Шаг 2. Проверяем статус
    if equipment["status"] != "available":
        return False, (
            f"Оборудование {equipment['serial_number']} недоступно. "
            f"Текущий статус: {equipment['status']}"
        )

    # Шаг 3. Проверяем активные дефекты
    if has_active_defects(equipment_id):
        return False, (
            f"Оборудование {equipment['serial_number']} имеет "
            f"неустранённые дефекты"
        )

    # Шаг 4. Проверяем пересечения дат
    overlaps = count_date_overlaps(equipment_id, start_date, end_date)
    if overlaps > 0:
        return False, (
            f"Оборудование {equipment['serial_number']} уже занято "
            f"на выбранный период ({overlaps} пересечений)"
        )

    # Шаг 5. Создаём запись бронирования
    booking = {
        "id": NEXT_BOOKING_ID,
        "equipment_id": equipment_id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "status": "active",
    }
    BOOKINGS_DB.append(booking)

    booking_item = {
        "id": len(BOOKING_ITEMS_DB) + 1,
        "booking_id": NEXT_BOOKING_ID,
        "equipment_id": equipment_id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
    BOOKING_ITEMS_DB.append(booking_item)

    # Шаг 6. Меняем статус оборудования
    equipment["status"] = "booked"

    NEXT_BOOKING_ID += 1

    return True, (
        f"Бронирование #{booking['id']} создано. "
        f"Оборудование: {equipment['serial_number']}, "
        f"период: {start_date} — {end_date}"
    )


def run_tests() -> None:
    """Тестовые сценарии для проверки алгоритма."""
    print("ТЕСТ 1: Успешное бронирование доступного оборудования")
    ok, msg = create_booking(
        equipment_id=1,
        start_date=date(2026, 11, 20),
        end_date=date(2026, 11, 22),
    )
    print(f"Результат: {'УСПЕХ' if ok else 'ОШИБКА'}")
    print(f"Сообщение: {msg}")
    print()

    print("ТЕСТ 2: Попытка забронировать оборудование в ремонте")
    ok, msg = create_booking(
        equipment_id=2,
        start_date=date(2026, 11, 20),
        end_date=date(2026, 11, 22),
    )
    print(f"Результат: {'УСПЕХ' if ok else 'ОШИБКА'}")
    print(f"Сообщение: {msg}")
    print()

    print("ТЕСТ 3: Попытка забронировать уже занятое оборудование")
    ok, msg = create_booking(
        equipment_id=3,
        start_date=date(2026, 11, 11),
        end_date=date(2026, 11, 13),
    )
    print(f"Результат: {'УСПЕХ' if ok else 'ОШИБКА'}")
    print(f"Сообщение: {msg}")
    print()

    print("ТЕСТ 4: Несуществующее оборудование")
    ok, msg = create_booking(
        equipment_id=99,
        start_date=date(2026, 11, 20),
        end_date=date(2026, 11, 22),
    )
    print(f"Результат: {'УСПЕХ' if ok else 'ОШИБКА'}")
    print(f"Сообщение: {msg}")


if __name__ == "__main__":
    run_tests()