import traci
import os
import sys
import time

# --- НАСТРОЙКА ПУТЕЙ (как было) ---
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Ошибка: нужно объявить переменную среды 'SUMO_HOME'")

sumoBinary = os.path.join(os.environ['SUMO_HOME'], 'bin', 'sumo-gui.exe')
config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "simulation.sumocfg")
# Было: sumoCmd = [sumoBinary, "-c", config_file, "--start"]
# Стало:
sumoCmd = [sumoBinary, "-c", config_file, "--start", "--tripinfo-output", "result_smart.xml"]


def run():
    traci.start(sumoCmd)

    # ID нашего светофора (как в nodes.nod.xml)
    tls_id = "C"

    step = 0
    # Начинаем с зеленого для главной дороги (Фаза 0)
    traci.trafficlight.setPhase(tls_id, 0)

    print("Старт интеллектуального управления!")

    while step < 3600:  # Крутим час симуляции
        traci.simulationStep()

        # --- 1. СБОР ДАННЫХ (Глаза) ---
        # Считаем машины, которые СТОЯТ (скорость < 0.1 м/с) на подъездах
        # Главная дорога (Вертикаль)
        halt_NS = traci.edge.getLastStepHaltingNumber("n_to_c") + traci.edge.getLastStepHaltingNumber("s_to_c")
        # Второстепенная дорога (Горизонталь)
        halt_WE = traci.edge.getLastStepHaltingNumber("w_to_c") + traci.edge.getLastStepHaltingNumber("e_to_c")

        # --- 2. ЛОГИКА УПРАВЛЕНИЯ (Мозги) ---

        # Узнаем, какая сейчас фаза светофора
        current_phase = traci.trafficlight.getPhase(tls_id)

        # Выводим инфу в консоль (чтобы видеть, что происходит)
        # print(f"Шаг {step}: Главная пробке={halt_NS}, Второстеп. пробка={halt_WE}, Фаза={current_phase}")

        # ЛОГИКА:
        # Если сейчас горит Зеленый Главной (Фаза 0)
        if current_phase == 0:
            # Если на второстепенной дороге скопились машины (больше 0)
            if halt_WE > 0:
                print(f"Обнаружена машина на второстепенной! Переключаем светофор...")
                traci.trafficlight.setPhase(tls_id, 1)  # Включаем желтый (Фаза 1)

        # Если горит Желтый после Главной (Фаза 1)
        elif current_phase == 1:
            # Ждем 4 секунды (условно 4 шага, если 1 шаг = 1 сек) и включаем зеленый боковым
            # В SUMO фаза имеет длительность. Здесь мы упростим:
            # Просто проверим, сколько времени мы уже в этой фазе.
            # Но для простоты: пусть SUMO сам переключит с желтого на след. фазу по таймеру,
            # А мы будем просто ждать.
            pass  # SUMO сам переключит на 2 (Зеленый боковой) когда выйдет время желтого

        # Если горит Зеленый Второстепенной (Фаза 2)
        elif current_phase == 2:
            # Держим зеленый, пока пробка на второстепенной не рассосется
            # ИЛИ пока не пройдет слишком много времени (защита от дурака)

            # Если боковая дорога опустела (halt_WE == 0) - пора переключать обратно
            if halt_WE == 0:
                print("Второстепенная пуста. Возвращаем приоритет главной.")
                traci.trafficlight.setPhase(tls_id, 3)  # Желтый (Фаза 3)

        # Если горит Желтый после Второстепенной (Фаза 3)
        elif current_phase == 3:
            pass  # Ждем, пока само переключится на 0 (Главная Зеленый)

        # Задержка для визуализации (чтобы ты успевал следить)
        time.sleep(0.01)
        step += 1

    traci.close()


if __name__ == "__main__":
    run()