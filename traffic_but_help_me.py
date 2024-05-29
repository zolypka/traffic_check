import os
import time
import psutil
from prettytable import PrettyTable
from prettytable import DOUBLE_BORDER


def create_table(process_list, limit) -> str:
    x = PrettyTable()
    x.field_names = ["Process ID", "Process Name", "Sent", "Received", "Sent/s", "Recv/s"]

    for process in process_list[:limit]:
        sent = convert_bytes(process["sent"])
        received = convert_bytes(process["recv"])
        sent_per_s = convert_bytes(process["sent_per_s"]) + "/sec"
        received_per_s = convert_bytes(process["recv_per_s"]) + "/sec"
        x.add_row([process["pid"], process["name"], sent, received, sent_per_s, received_per_s])

    x.set_style(DOUBLE_BORDER)
    return x.get_string()


def get_process_stats() -> list:
    connections = psutil.net_connections(kind='inet')
    process_stats = {}
    for conn in connections:
        if conn.raddr and hasattr(conn.raddr, 'pid'):
            pid = conn.raddr.pid
        elif conn.laddr and hasattr(conn.laddr, 'pid'):
            pid = conn.laddr.pid
        else:
            continue

        process_stats[pid] = {
            'sent': process_stats.get(pid, {}).get('sent', 0) + conn.sent,
            'recv': process_stats.get(pid, {}).get('recv', 0) + conn.recv,
        }

    process_stats_list = [
        {"pid": pid, "name": psutil.Process(pid).name(), "sent": sent, "recv": recv}
        for pid, (sent, recv) in process_stats.items()
    ]

    return process_stats_list

# Main program
def main():
    print("Network Traffic Monitor: ")
    print("-------------------------------------------------")
    try:
        while True:
            time.sleep(1)
            os.system('cls')
            process_stats = get_process_stats()
            table = create_table(process_stats, 5)  
            print(table)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nProgram terminated.")

if __name__ == '__main__':
    main()
