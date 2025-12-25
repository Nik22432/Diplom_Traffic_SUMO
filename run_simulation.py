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

# ВАЖНО: Пишем статистику в result_basic.xml
sumoCmd = [sumoBinary, "-c", config_file, "--start", "--tripinfo-output", "result_basic.xml"]


def run():
    traci.start(sumoCmd)
    tls_id = "C"
    step = 0

    # Переменная, чтобы помнить, какая фаза была на прошлом шаге
    last_phase = -1

    print("Запуск БАЗОВОГО (Глупого) сценария. Цикл: 90 сек Главная / 30 сек Боковая.")

    while step < 10800:  # 3 часа
        traci.simulationStep()

        # --- ЛОГИКА ЖЕСТКОГО ТАЙМЕРА (30/90) ---
        current_phase = traci.trafficlight.getPhase(tls_id)

        # Если фаза только что сменилась (начало новой фазы)
        if current_phase != last_phase:

            # Фаза 0: Зеленый ГЛАВНАЯ (Север-Юг) -> Ставим 90 секунд
            if current_phase == 0:
                traci.trafficlight.setPhaseDuration(tls_id, 90)

            # Фаза 2: Зеленый БОКОВАЯ (Запад-Восток) -> Ставим 30 секунд
            elif current_phase == 2:
                traci.trafficlight.setPhaseDuration(tls_id, 30)

            # Фазы 1 и 3 (Желтые) не трогаем, они останутся стандартными (по 4 сек)

            last_phase = current_phase
        # ---------------------------------------

        # Можешь закомментировать sleep, если хочешь, чтобы пролетело быстро
        # time.sleep(0.01)

        step += 1

    traci.close()


if __name__ == "__main__":
    run()