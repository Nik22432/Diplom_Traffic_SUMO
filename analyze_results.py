import xml.etree.ElementTree as ET


def get_stats(xml_file):
    try:
        tree = ET.parse(xml_file)
    except FileNotFoundError:
        return None

    root = tree.getroot()

    total_time_loss = 0
    total_waiting_time = 0
    total_cars = 0

    for trip in root.findall('tripinfo'):
        # ИСПРАВЛЕНИЕ: используем 'waitingTime' вместо 'waitSteps'
        # А также берем 'timeLoss' - это более показательная метрика
        wait = float(trip.get('waitingTime', 0))
        loss = float(trip.get('timeLoss', 0))

        total_waiting_time += wait
        total_time_loss += loss
        total_cars += 1

    if total_cars == 0:
        return 0, 0, 0

    return total_waiting_time, total_time_loss, total_cars


print("--- АНАЛИЗ РЕЗУЛЬТАТОВ ---")

# Читаем оба файла
stats_basic = get_stats("result_basic.xml")
stats_smart = get_stats("result_smart.xml")

if stats_basic is None:
    print("Ошибка: Нет файла result_basic.xml")
elif stats_smart is None:
    print("Ошибка: Нет файла result_smart.xml")
else:
    # Распаковываем данные
    wait_b, loss_b, cars_b = stats_basic
    wait_s, loss_s, cars_s = stats_smart

    # 1. БАЗОВЫЙ
    avg_loss_b = loss_b / cars_b
    print(f"БАЗОВЫЙ сценарий:")
    print(f"  Машин: {cars_b}")
    print(f"  Средняя потеря времени: {avg_loss_b:.2f} сек")
    print(f"  (Средний чистый простой: {wait_b / cars_b:.2f} сек)")

    print("-" * 30)

    # 2. УМНЫЙ
    avg_loss_s = loss_s / cars_s
    print(f"УМНЫЙ сценарий:")
    print(f"  Машин: {cars_s}")
    print(f"  Средняя потеря времени: {avg_loss_s:.2f} сек")
    print(f"  (Средний чистый простой: {wait_s / cars_s:.2f} сек)")

    print("-" * 30)

    # СРАВНЕНИЕ
    if avg_loss_b > 0:
        diff = avg_loss_b - avg_loss_s
        percent = (diff / avg_loss_b) * 100

        if diff > 0:
            print(f"ИТОГ: Твой алгоритм сэкономил {diff:.2f} сек каждой машине!")
            print(f"ЭФФЕКТИВНОСТЬ: +{percent:.2f}%")
        else:
            print(f"ИТОГ: Алгоритм сработал хуже на {abs(percent):.2f}%. Нужно настраивать.")