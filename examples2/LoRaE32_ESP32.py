#######################################################################
# MicroPython class for EBYTE E32 Series LoRa modules which are based
# on SEMTECH SX1276/SX1278 chipsets and are available for 170, 433, 470,
# 868 and 915MHz frequencies in 100mW and 1W transmitting power versions.
# They all use a simple UART interface to control the device.
#
# Pin layout E32-868T20D (SX1276 868MHz 100mW DIP Wireless Module)
# ======================
# +---------------------------------------------+
# | 0 - M0  (set mode)        [*]               |
# | 0 - M1  (set mode)        [*]               |
# | 0 - RXD (TTL UART input)  [*]               |
# | 0 - TXD (TTL UART output) [*]               |
# | 0 - AUX (device status)   [*]               |
# | 0 - VCC (3.3-5.2V)                          +---+
# | 0 - GND (GND)                                SMA| Antenna
# +-------------------------------------------------+
#     [*] ALL COMMUNICATION PINS ARE 3.3V !!!
#
# Transmission modes :
# ==================
#   - Transparent : all modules have the same address and channel and
#        can send/receive messages to/from each other. No address and
#        channel is included in the message.
#
#   - Fixed : all modules can have different addresses and channels.
#        The transmission messages are prefixed with the destination address
#        and channel information. If these differ from the settings of the
#        transmitter, then the configuration of the module will be changed
#        before the transmission. After the transmission is complete,
#        the transmitter will revert to its prior configuration.
#
#        1. Fixed P2P : The transmitted message has the address and channel
#           information of the receiver. Only this module will receive the message.
#           This is a point to point transmission between 2 modules.
#
#        2. Fixed Broadcast : The transmitted message has address FFFF and a
#           channel. All modules with any address and the same channel of
#           the message will receive it.
#             
#        3. Fixed Monitor : The receiver has adress FFFF and a channel.
#           It will receive messages from all modules with any address and
#           the same channel as the receiver.
#
# Operating modes :
# ===============
#   - 0=Normal (M0=0,M1=0) : UART and LoRa radio are on.
#
#   - 1=wake up (M0=1,M1=0) : Same as normal but preamble code is added to
#             transmitted data to wake up the receiver.
#
#   - 2=power save (M0=0,M1=1) : UART is off, LoRa radio is on WOR(wake on radio) mode
#             which means the device will turn on when there is data to be received.
#             Transmission is not allowed.
#
#   - 3=sleep (M0=1,M1=1) : UART is on, LoRa radio is off. Is used to
#             get/set module parameters or to reset the module.
#
######################################################################
import time
from machine import Pin, UART

from LoRaE32 import ebyteE32

class ebyteE32_ESP32(ebyteE32):
    ''' class to interface an ESP32 via serial commands to the EBYTE E32 Series LoRa modules '''
    
    # UART ports
    PORT = { 'U0':0, 'U1':1, 'U2':2 }
    

    def __init__(self, PinM0, PinM1, PinAUX, Model='433T30D', Port='U2', Baudrate=9600, Parity='8N1', AirDataRate='2.4k', Address=0x0000, Channel=0x17, debug=False):
        ''' constructor for ebyte E32 LoRa module '''
        super().__init__(Model, Port, Baudrate, Parity, AirDataRate, Address, Channel, debug)
        # 
        self.PinM0 = PinM0                         # M0 pin number
        self.PinM1 = PinM1                         # M1 pin number
        self.PinAUX = PinAUX                       # AUX pin number
        self.M0 = None                             # instance for M0 Pin (set operation mode)
        self.M1 = None                             # instance for M1 Pin (set operation mode)
        self.AUX = None                            # instance for AUX Pin (device status : 0=busy - 1=idle)
        

    def start(self):
        ''' Start the ebyte E32 LoRa module '''
        super().start()
        
        # make UART instance
        self.serdev = UART(self.PORT.get(self.config['port']))
        par = self.PARBIT.get(str(self.config['parity'])[1])
        self.serdev.init(baudrate=self.config['baudrate'], bits=8, parity=par, stop=1) # , txbuf=512, rxbuf=512) # , timeout=100)

        # init UART
        if self.debug:
            print('self.serdev', self.serdev)
        # make operation mode & device status instances
        self.M0 = Pin(self.PinM0, Pin.OUT, 1)
        self.M1 = Pin(self.PinM1, Pin.OUT, 1)
        self.AUX = Pin(self.PinAUX, Pin.IN, Pin.PULL_UP)
        if self.debug:
            print('self.M0, self.M1, self.AUX', self.M0, self.M1, self.AUX)
        # set config to the ebyte E32 LoRa module
        # self.setConfig('setConfigPwrDwnSave')
        return 'OK start'
        
    def setM0(self, value):
        self.M0.value(value)
    
    
    def setM1(self, value):
        self.M1.value(value)
    
    
    def getAUX(self):
        return self.AUX.value()
    
    
    def in_waiting(self):
        return self.serdev.any()

    def flush(self):
        pass

    def read(self)->bytes:
        return self.serdev.read()

    def time_ms(self):
        return time.ticks_ms()

    def sleep_ms(self, ms):
        time.sleep_ms(ms)
