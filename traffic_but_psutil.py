import psutil
import time
import os


def get_net_io():
    net1 = psutil.net_io_counters(pernic=True)
    time.sleep(1)
    net2 = psutil.net_io_counters(pernic=True)
    net_stat = {}
    for nic in net1.keys():
        bytes_sent = net2[nic].bytes_sent - net1[nic].bytes_sent
        bytes_recv = net2[nic].bytes_recv - net1[nic].bytes_recv
        net_stat[nic] = {"bytes_sent": bytes_sent, "bytes_recv": bytes_recv}
    return net_stat


try:
    prev_output = ""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        net_stat = get_net_io()
        total_sent = sum(data["bytes_sent"] for data in net_stat.values())
        total_recv = sum(data["bytes_recv"] for data in net_stat.values())

        output = ""
        for nic, data in net_stat.items():
            line = f"{nic}: Отправлено (B/sec): {data['bytes_sent']}, Получено (B/sec): {data['bytes_recv']}\n"
            output += line

        output += f"\nОбщее потребление: Отправлено (B/sec): {total_sent}, Получено (B/sec): {total_recv}"

        if output != prev_output:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(output)
            prev_output = output

        time.sleep(5)
except KeyboardInterrupt:
    print("Программа остановлена пользователем")