import gatt
import struct
import datetime
import os
import smbus
import time

class AtomFast(gatt.Device):

    def __init__(self):
        self.connect_callback = None
        self.update_callback = None
    
    def SetConnectCallback(self, connect_callback):
        self.connect_callback = connect_callback

    def SetDisconnectCallback(self, disconnect_callback):
        self.disconnect_callback = disconnect_callback

    def SetUpdateCallback(self, update_callback):
        self.update_callback = update_callback
    
    def SetErrorCallback(self, error_callback):
        self.error_callback = error_callback

    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))
        if self.connect_callback != None:
            self.connect_callback()

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))
        super().connect()
        if self.error_callback != None:
            self.error_callback()

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))
        super().connect()
        if self.disconnect_callback != None:
            self.disconnect_callback()

    def services_resolved(self):
        super().services_resolved()

        device_information_service = next(
            s for s in self.services
            if s.uuid == '63462a4a-c28c-4ffd-87a4-2d23a1c72581')

        firmware_version_characteristic = next(
            c for c in device_information_service.characteristics
            if c.uuid == '70bc767e-7a1a-4304-81ed-14b9af54f7bd')

        firmware_version_characteristic.enable_notifications()

    def characteristic_value_updated(self, characteristic, value):
        flags_b_value = bytes(value)[0:1]
        dose_accumulated_b_value = bytes(value)[1:5]
        dose_power_b_value = bytes(value)[5:9]
        impulses_b_value = bytes(value)[9:11]
        charge_b_value = bytes(value)[11:12]
        temperature_b_value = bytes(value)[12:13]

        flags = struct.unpack('b', flags_b_value)[0]
        dose_accumulated = struct.unpack('f',dose_accumulated_b_value)[0]
        dose_power = struct.unpack('f', dose_power_b_value)[0]
        impulses = struct.unpack('H', impulses_b_value)[0]
        charge = struct.unpack('b', charge_b_value)[0]
        temperature = struct.unpack('B', temperature_b_value)[0]

        dose_exceed_flag = flags >> 0 & 1
        dose_power_exceed_flag = flags >> 1 & 1
        count_speed_inc_flag = flags >> 2 & 1
        current_exceed_flag = flags >> 4 & 1
        detector_overload_flag = flags >> 5 & 1
        charger_connected_flag = flags >> 6 & 1
        emergency_shutdown_flag = flags >> 7 & 1

        date_now = datetime.datetime.now().timestamp()

        info = {'timestamp': date_now,
                'dose_accumulated': dose_accumulated,
                'dose_power': dose_power,
                'impulses': impulses,
                'charge': charge,
                'temperature': temperature,
                'flags': {
                        'dose_exceed': dose_exceed_flag,
                        'dose_power_exceed': dose_power_exceed_flag,
                        'count_speed_inc': count_speed_inc_flag,
                        'current_exceed': current_exceed_flag,
                        'detector_overload': detector_overload_flag,
                        'charger_connected': charger_connected_flag,
                        'emergency_shutdown': emergency_shutdown_flag
                    }
                }

        if self.update_callback != None:
            self.update_callback(info)