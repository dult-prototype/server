import dbus
import command_result
import helper

import threading
import multiprocessing
from playsound import playsound

from advertisement import Advertisement
from service import Application, Service, Characteristic, Descriptor

GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"

# Sound player process and a mutex lock for the same
mutex = threading.Lock()
sound_player = multiprocessing.Process(target=playsound, args=("sound.wav",))

# converts bytes to array of dbus bytes
def encode(data):
    data = [dbus.Byte(c) for c in data]
    return data

class NonOwnerAdvertisement(Advertisement):
    def __init__(self, index):
        Advertisement.__init__(self, index, "peripheral")
        self.add_local_name("Rakshith GATT Server")
        self.include_tx_power = True

class NonOwnerService(Service):
    NON_OWNER_SERVICE_UUID = "00000090-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, index):

        Service.__init__(self, index, self.NON_OWNER_SERVICE_UUID, True)
        self.add_characteristic(NonOwnerControlPoint(self))

class NonOwnerControlPoint(Characteristic):
    NON_OWNER_CONTROL_POINT_CHARACTERISTIC_UUID = "00000090-0100-0000-0000-000000000000"

    GET_PRODUCT_DATA = 0x306
    GET_PRODUCT_DATA_RESPONSE = 0x311

    GET_MANUFACTURER_NAME = 0x307
    GET_MANUFACTURER_NAME_RESPONSE = 0x312

    GET_MODEL_NAME = 0x308
    GET_MODEL_NAME_RESPONSE = 0x313

    GET_ACCESSORY_CATEGORY = 0x309
    GET_ACCESSORY_CATEGORY_RESPONSE = 0x314

    GET_ACCESSORY_CAPABILITIES = 0x30a
    GET_ACCESSORY_CAPABILITIES_RESPONSE = 0x315

    GET_SERIAL_NUMBER = 0x404
    GET_SERIAL_NUMBER_RESPONSE = 0x405

    SOUND_START = 0x300
    SOUND_STOP = 0x301
    COMMAND_RESPONSE = 0X302
    SOUND_COMPLETED = 0x303

    OPCODE_SIZE = 16

    def __init__(self, service):
        self.notifying = False
        self.product_data = "0xdfeceff1e1ff54db"
        self.manufacturer_name = "Tile"
        self.model_name = "Tile Slim 2020"
        self.accessory_category = "1"
        self.accessory_capabilities = "9"
        self.serial_number = "83A8JFDK48WJSAK"

        Characteristic.__init__(
                self, self.NON_OWNER_CONTROL_POINT_CHARACTERISTIC_UUID,
                ["read", "write", "indicate"], service)
        self.add_descriptor(NonOwnerControlPointDescriptor(self))

    def StartNotify(self):
        print('Subscribing to non owner control point')

    def StopNotify(self):
        print('Unsubscribing from non owner control point')
    
    def start_sound(self):
        global mutex, sound_player
        mutex.acquire()
        if not sound_player.is_alive():
            try:
                sound_player = multiprocessing.Process(target=playsound, args=("sound.wav",))
                print("Playing sound...")
                sound_player.start()
            except:
                print("Error while playing sound")
                mutex.release()
                return False
            mutex.release()
            return True
        mutex.release()
        return False

    def stop_sound(self):
        global mutex, sound_player
        mutex.acquire()
        if sound_player.is_alive():        
            try:
                sound_player.terminate()
            except Exception:
                return False
            mutex.release()
            return True
        mutex.release()
        return False

    def IndicateValue(self, opcode, value_in_bytes):
        opcode_in_bytes = opcode.to_bytes(2, 'little')
        self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': encode(opcode_in_bytes + value_in_bytes)}, [])

    def WriteValue(self, value, options):
        opcode = helper.bytes_to_int(value)
        if opcode == self.GET_PRODUCT_DATA:
            print("Get Product Data")
            self.IndicateValue(self.GET_PRODUCT_DATA_RESPONSE, self.product_data.encode())
        elif opcode == self.GET_MODEL_NAME:
            print("Get Model Name")
            self.IndicateValue(self.GET_MODEL_NAME_RESPONSE, self.model_name.encode())
        elif opcode == self.GET_MANUFACTURER_NAME:
            print("Get Manufacturer Name")
            self.IndicateValue(self.GET_MANUFACTURER_NAME_RESPONSE, self.manufacturer_name.encode())
        elif opcode == self.GET_ACCESSORY_CAPABILITIES:
            print("Get Accessory Capabilities")
            self.IndicateValue(self.GET_ACCESSORY_CAPABILITIES_RESPONSE, self.accessory_capabilities.encode())
        elif opcode == self.GET_ACCESSORY_CATEGORY:
            print("Get Accessory Category")
            self.IndicateValue(self.GET_ACCESSORY_CATEGORY_RESPONSE, self.accessory_category.encode())
        elif opcode == self.SOUND_START:
            print("Sound Start")
            is_successful = self.start_sound()
            if is_successful:
                print("Sound start successful")
                result = command_result.get_command_result(self.SOUND_START, command_result.SUCCESS)
                self.IndicateValue(self.COMMAND_RESPONSE, result)
            else:
                print("Error while starting sound, might be already playing")        
                result = command_result.get_command_result(self.SOUND_START, command_result.INVALID_STATE)
                self.IndicateValue(self.COMMAND_RESPONSE, result)
        elif opcode == self.SOUND_STOP:
            print("Sound Stop")
            is_successful = self.stop_sound()
            if is_successful:
                print("Sound stop successful")
                result = command_result.get_command_result(self.SOUND_STOP, command_result.SUCCESS)
                self.IndicateValue(self.COMMAND_RESPONSE, result)
            else:
                print("Error while starting sound, might be already playing")        
                result = command_result.get_command_result(self.SOUND_STOP, command_result.INVALID_STATE)
                self.IndicateValue(self.COMMAND_RESPONSE, result)
        elif opcode == self.GET_SERIAL_NUMBER:
            self.IndicateValue(self.GET_SERIAL_NUMBER_RESPONSE, self.serial_number.encode())

class NonOwnerControlPointDescriptor(Descriptor):
    NON_OWNER_CONTROL_POINT_DESCRIPTOR_UUID = "2901"
    NON_OWNER_CONTROL_POINT_DESCRIPTOR_VALUE = "Control point for DULT"

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, self.NON_OWNER_CONTROL_POINT_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        return encode(self.NON_OWNER_CONTROL_POINT_DESCRIPTOR_VALUE)
    
# Set up the application with the non owner service
app = Application()
app.add_service(NonOwnerService(0))
app.register()

# Register advertisement
adv = NonOwnerAdvertisement(0)
adv.register()

try:
    app.run()
except KeyboardInterrupt:
    app.quit()
    adv.Release()
