import os
import time
import psutil
from prettytable import PrettyTable
from prettytable import DOUBLE_BORDER
from main import getSize, getProcessNetworkUsage

def test_getSize():
    assert getSize(1023) == '1023.0bytes'
    assert getSize(1024) == '1.0KB'
    assert getSize(1048576) == '1.0MB'
    assert getSize(1073741824) == '1.0GB'
    assert getSize(1099511627776) == '1.0TB'

def test_getProcessNetworkUsage():
    networkUsage = getProcessNetworkUsage()
    assert isinstance(networkUsage, dict)
    for key, value in networkUsage.items():
        assert isinstance(key, str)
        assert isinstance(value, psutil._common.snetio)

def test_whole_program():
    test_getSize()
    test_getProcessNetworkUsage()
