import gatt
import struct
import datetime
import os
import argparse
import sys
sys.path.append("..")
from atomfast_ble_driver import AtomFast

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--mac', default = None)

args = parser.parse_args(sys.argv[1:])

def OnUpdate(info):
    print(info['dose_power'])

manager = gatt.DeviceManager(adapter_name='hci0')

if args != None:
    device = AtomFast(mac_address = args.name, manager = manager)
    device.SetUpdateCallback(OnUpdate)
    device.connect()
    manager.run()
else:
    print("Need arg --mac for bt mac")