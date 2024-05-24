import socket
import psutil
from collections import defaultdict
import os
from threading import Thread
import pandas as pd
import time
from datetime import datetime
import netifaces


def get_interface_ip(interface_name):
    iface_info = netifaces.ifaddresses(interface_name)
    if netifaces.AF_INET in iface_info:
        return iface_info[netifaces.AF_INET][0]['addr']
    return None


ifaces = netifaces.interfaces()
all_macs = set()
for iface_name in ifaces:
    iface_info = netifaces.ifaddresses(iface_name)
    if netifaces.AF_LINK in iface_info:
        mac_address = iface_info[netifaces.AF_LINK][0]['addr']
        all_macs.add(mac_address)

connection2pid = {}
pid2traffic = defaultdict(lambda: [0, 0])
global_df = None
is_program_running = True
HOST = socket.gethostname()
port = 12345

interface_name = '{D042288F-92D6-4DA1-974A-142FA3510CEC}'
# need interface name
interface_ip = get_interface_ip(interface_name)

if interface_ip:
    def get_connections():
        global connection2pid
        while is_program_running:
            with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP) as s:
                s.bind(("0.0.0.0", port))
                # need hostname and port for this thing to work
                s.listen(5)
                s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                data, addr = s.recvfrom(65565)

                src_port = int.from_bytes(data[34:36], byteorder='big')
                dst_port = int.from_bytes(data[36:38], byteorder='big')
                src_ip = '.'.join(map(str, data[26:30]))
                dst_ip = '.'.join(map(str, data[30:34]))

                for pid, conn in connection2pid.items():
                    if conn['laddr'] == (src_ip, src_port) and conn['raddr'] == (dst_ip, dst_port):
                        connection2pid[pid] = conn
                        break
                else:
                    connection2pid[pid] = {'laddr': (src_ip, src_port), 'raddr': (dst_ip, dst_port)}

                time.sleep(1)
else:
    print("Interface IP not found for interface:", interface_name)


def get_size(bytes):
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}B"
        bytes /= 1024


def process_packet(data):
    global pid2traffic
    try:
        packet_connection = (data['sport'], data['dport'])
    except (KeyError, IndexError):
        pass
    else:
        packet_pid = connection2pid.get(packet_connection)
        if packet_pid:
            if data['src'] in all_macs:
                pid2traffic[packet_pid][0] += len(data['data'])
            else:
                pid2traffic[packet_pid][1] += len(data['data'])


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

    print("Traffic check started")
