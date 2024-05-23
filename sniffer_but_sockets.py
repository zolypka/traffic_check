import socket
import psutil
from collections import defaultdict
import os
from threading import Thread
import pandas as pd
import time
from datetime import datetime

ifaces = {
    "eth0": {"mac": "02:50:59:53:15:49"}
    #need mac addres here
}

all_macs = {iface['mac'] for iface in ifaces.values()}
connection2pid = {}
pid2traffic = defaultdict(lambda: [0, 0])
global_df = None
is_program_running = True


def get_size(bytes):
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}B"
        bytes /= 1024


def process_packet(data, addr):
    global pid2traffic
    packet_connection = (addr[1], data[0])
    packet_pid = connection2pid.get(packet_connection)
    if packet_pid:
        if data[1] in all_macs:
            pid2traffic[packet_pid][0] += len(data)
        else:
            pid2traffic[packet_pid][1] += len(data)


def get_connections():
    global connection2pid
    while is_program_running:
        for c in psutil.net_connections():
            if c.laddr and c.raddr and c.pid:
                connection2pid[(c.laddr.port, c.raddr.port)] = c.pid
                connection2pid[(c.raddr.port, c.laddr.port)] = c.pid
        time.sleep(1)


def print_pid2traffic():
    global global_df
    processes = []
    for pid, traffic in pid2traffic.items():
        try:
            p = psutil.Process(pid)
        except psutil.NoSuchProcess:
            continue
        name = p.name()
        try:
            create_time = datetime.fromtimestamp(p.create_time())
        except OSError:
            create_time = datetime.fromtimestamp(psutil.boot_time())
        process = {
            "pid": pid, "name": name, "create_time": create_time, "Upload": traffic[0],
            "Download": traffic[1],
        }
        try:
            process["Upload Speed"] = traffic[0] - global_df.at[pid, "Upload"]
            process["Download Speed"] = traffic[1] - global_df.at[pid, "Download"]
        except (KeyError, AttributeError):
            process["Upload Speed"] = traffic[0]
            process["Download Speed"] = traffic[1]
        processes.append(process)
    df = pd.DataFrame(processes)
    try:
        df = df.set_index("pid")
        df.sort_values("Download", inplace=True, ascending=False)
    except KeyError as e:
        pass
    printing_df = df.copy()
    try:
        printing_df["Download"] = printing_df["Download"].apply(get_size)
        printing_df["Upload"] = printing_df["Upload"].apply(get_size)
        printing_df["Download Speed"] = printing_df["Download Speed"].apply(get_size).apply(lambda s: f"{s}/s")
        printing_df["Upload Speed"] = printing_df["Upload Speed"].apply(get_size).apply(lambda s: f"{s}/s")
    except KeyError as e:
        pass
    os.system("cls") if "nt" in os.name else os.system("clear")
    print(printing_df.to_string())
    global_df = df


def print_stats():
    while is_program_running:
        time.sleep(1)
        print_pid2traffic()


if __name__ == "__main__":
    printing_thread = Thread(target=print_stats)
    printing_thread.start()
    connections_thread = Thread(target=get_connections)
    connections_thread.start()

    print("traffic check started")
    with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP) as s:
        s.bind((#need ports here, goddamn))
        while is_program_running:
            data, addr = s.recvfrom(65565)
            process_packet(data, addr)