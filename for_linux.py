import os
import time
import psutil
from prettytable import PrettyTable
from prettytable import DOUBLE_BORDER

size = ['bytes', 'KB', 'MB', 'GB', 'TB']


def getSize(bytes):
    for unit in size:
        if bytes < 1024:
            return f"{bytes:.1f}{unit}"
        bytes /= 1024


def getProcessNetworkUsage():
    processes = list(psutil.process_iter())

    networkUsage = {}

    for process in processes:
        try:
            connections = process.connections()
            for conn in connections:
                process_name = process.name()
                if process_name not in networkUsage:
                    networkUsage[process_name] = psutil.net_io_counters(pernic=False)
        except psutil.AccessDenied:
            pass

    return networkUsage


def printData(networkUsage):

    card = PrettyTable()
    card.set_style(DOUBLE_BORDER)
    card.field_names = ["Process", "Received", "Receiving", "Sent", 'Sending']

    sorted_processes = sorted(networkUsage.items(), key=lambda x: sum([x[1].bytes_sent, x[1].bytes_recv]), reverse=True)

    for process_name, data in sorted_processes[:5]:
        received = getSize(data.bytes_recv)
        sent = getSize(data.bytes_sent)

        netStats2 = psutil.net_io_counters()

        card.add_row([process_name, received, getSize(downloadStat) + "/s", sent, getSize(uploadStat) + "/s"])

    print(card)

netStats1 = psutil.net_io_counters()

dataSent = netStats1.bytes_sent
dataRecv = netStats1.bytes_recv

while True:
    time.sleep(1)

    os.system('clear')

    netStats2 = psutil.net_io_counters()

    uploadStat = netStats2.bytes_sent - dataSent
    downloadStat = netStats2.bytes_recv - dataRecv

    networkUsage = getProcessNetworkUsage()

    printData(networkUsage)
#Unfortunately, psutil has the ability only to track the total network usage or network usage per network interface. To be able to monitor usage per process, we have to use yet another library and that is Scapy.