import traci
import os
import sys
import time

# --- НАСТРОЙКИ ---
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Ошибка: нужно объявить переменную среды 'SUMO_HOME'")

sumoBinary = os.path.join(os.environ['SUMO_HOME'], 'bin', 'sumo.exe')  # Используем быструю версию без GUI
config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "simulation.sumocfg")
sumoCmd = [sumoBinary, "-c", config_file, "--start", "--quit-on-end"]


def run():
    traci.start(sumoCmd)

    # Открываем файл для записи логов датчиков
    # Формат: 1 строка = 1 секунда. Значение: 1 (есть машина сбоку) или 0 (пусто)
    with open("sensor_data.txt", "w") as f:
        print("Начинаю симуляцию и запись данных...")

        step = 0
        while step < 1000:  # Запишем 1000 секунд
            traci.simulationStep()

            # Считываем датчики (Второстепенная дорога)
            halt_WE = traci.edge.getLastStepHaltingNumber("w_to_c") + traci.edge.getLastStepHaltingNumber("e_to_c")

            # Логика для ПЛИС простая:
            # 1 - если есть пробка на второстепенной
            # 0 - если второстепенная пуста
            sensor_signal = "1" if halt_WE > 0 else "0"

            # Записываем в файл
            f.write(sensor_signal + "\n")

            step += 1

    traci.close()
    print("Готово! Файл 'sensor_data.txt' создан.")


if __name__ == "__main__":
    run()