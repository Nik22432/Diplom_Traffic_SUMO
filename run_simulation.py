import traci
import os
import sys

# Настройка путей (стандартная)
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)

sumoBinary = os.path.join(os.environ['SUMO_HOME'], 'bin', 'sumo-gui.exe')
config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "simulation.sumocfg")

# ВАЖНО: Добавляем вывод статистики в файл result_basic.xml
sumoCmd = [sumoBinary, "-c", config_file, "--start", "--tripinfo-output", "result_basic.xml"]


def run_basic():
    traci.start(sumoCmd)
    print("Запуск БАЗОВОГО сценария (без управления)...")

    step = 0
    while step < 3600:  # 1 час симуляции
        traci.simulationStep()
        # МЫ НИЧЕГО НЕ ДЕЛАЕМ СО СВЕТОФОРОМ
        # Пусть работает как обычный таймер
        step += 1

    traci.close()
    print("Базовый сценарий завершен. Файл result_basic.xml создан.")


if __name__ == "__main__":
    run_basic()