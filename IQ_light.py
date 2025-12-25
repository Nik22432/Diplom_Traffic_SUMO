import traci
import os
import sys
import time

# --- НАСТРОЙКИ ---
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)

sumoBinary = os.path.join(os.environ['SUMO_HOME'], 'bin', 'sumo-gui.exe')
config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "simulation.sumocfg")

# ВАЖНО: Пишем статистику в result_smart.xml
sumoCmd = [sumoBinary, "-c", config_file, "--start", "--tripinfo-output", "result_smart.xml"]


def run():
    traci.start(sumoCmd)
    tls_id = "C"
    step = 0

    print("Запуск УМНОГО (Адаптивного) сценария.")

    while step < 10800:  # 3 часа
        traci.simulationStep()

        # --- 1. СБОР ДАННЫХ (Глаза) ---
        # Складываем пробки на главной (Север + Юг)
        q_main = traci.edge.getLastStepHaltingNumber("n_to_c") + traci.edge.getLastStepHaltingNumber("s_to_c")
        # Складываем пробки на боковой (Запад + Восток)
        q_side = traci.edge.getLastStepHaltingNumber("w_to_c") + traci.edge.getLastStepHaltingNumber("e_to_c")

        # --- 2. ЛОГИКА УПРАВЛЕНИЯ (Мозги) ---
        phase = traci.trafficlight.getPhase(tls_id)

        # Если горит Зеленый ГЛАВНОЙ (Фаза 0)
        if phase == 0:
            # Если боковая дорога пустая
            if q_side == 0:
                # Продлеваем зеленый главной (не даем переключиться)
                traci.trafficlight.setPhaseDuration(tls_id, 2.0)

        # Если горит Зеленый БОКОВОЙ (Фаза 2)
        if phase == 2:
            # Если на боковой ЕСТЬ машины, а на главной пока свободно (или меньше 20 машин)
            # Мы даем боковым проехать, продлевая их фазу
            if q_side > 0 and q_main < 20:
                traci.trafficlight.setPhaseDuration(tls_id, 2.0)
            # Иначе (если q_side стало 0) -> продление прекратится, включится желтый, потом главная.

        # Пауза для визуализации (чтобы было плавно)
        #time.sleep(0.05)

        step += 1

    traci.close()


if __name__ == "__main__":
    run()