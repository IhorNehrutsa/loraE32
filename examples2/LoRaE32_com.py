# M0 - RTS - фиолетовый
# M1 - DTR - синий
# AUX - DSR - оранжевый

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
import serial

from LoRaE32 import ebyteE32

class ebyteE32_win(ebyteE32):
    ''' class to interface an ESP32 via serial commands to the EBYTE E32 Series LoRa modules '''
    

    def __init__(self, Model='433T30D', Port='COM1', Baudrate=9600, Parity='8N1', AirDataRate='2.4k', Address=0x0000, Channel=0x17, debug=False):
        ''' constructor for ebyte E32 LoRa module '''
        super().__init__(Model, Port, Baudrate, Parity, AirDataRate, Address, Channel, debug)
        

    def start(self):
        ''' Start the ebyte E32 LoRa module '''
        try:
            super().start()
            
            # make UART instance
            self.serdev = serial.Serial(self.config['port'], baudrate=self.config['baudrate'], timeout=None, write_timeout=None)
            if not self.serdev.isOpen():
                self.serdev.open()
            
            if self.debug:
                print('self.serdev', self.serdev)
            # set config to the ebyte E32 LoRa module
            # self.setConfig('setConfigPwrDwnSave')
            return 'OK start'
        
        except Exception as E:
            if self.debug:
                print('error on start UART', E)
            return 'NOK start'
        
    
    def setM0(self, value):
        self.serdev.rts = (value == 0)
    
    
    def setM1(self, value):
        self.serdev.dtr = (value == 0)
    
    
    def getAUX(self):
        return 1
    
    
    def is_any(self):
        return self.serdev.in_waiting

    def read(self)->bytes:
        #return self.serdev.read()
        return self.serdev.read_all()
        #return self.serdev.read(self.serdev.in_waiting)
    
        n = self.serdev.in_waiting
        if n:
            #return self.serdev.read(n)
            #return self.serdev.read_all()
            return self.serdev.read(self.serdev.in_waiting)
        else:
            return None
        
    def flush(self):
        self.serdev.flush()
  
#     def sendMessage(self, to_address, to_channel, payload, useChecksum=False):
#         ''' Send the payload to ebyte E32 LoRa modules in transparent or fixed mode. The payload is a data dictionary to
#             accomodate key value pairs commonly used to store sensor data and is converted to a JSON string before sending.
#             The payload can be appended with a 2's complement checksum to validate correct transmission.
#             - transparent mode : all modules with the same address and channel of the transmitter will receive the payload
#             - fixed mode : only the module with this address and channel will receive the payload;
#                            if the address is 0xFFFF all modules with the same channel will receive the payload'''
#         try:
#             # type of transmission
#             if (to_address == self.config['address']) and (to_channel == self.config['channel']):
#                 # transparent transmission mode
#                 # all modules with the same address and channel will receive the payload
#                 self.setTransmissionMode(0)
#             else:
#                 # fixed transmission mode
#                 # only the module with the target address and channel will receive the payload
#                 self.setTransmissionMode(1)
#             # put into wakeup mode (includes preamble signals to wake up device in powersave or sleep mode)
#             self.setOperationMode('wakeup')
# #            self.setOperationMode('normal')
#             # check payload
#             if (type(payload) != dict) and (type(payload) != str):
#                 print('payload is not a dictionary or str', payload)
#                 return 'NOK sendMessage'
#             # encode message
#             msg = []
# #             if self.config['transmode'] == 1:     # only for fixed transmission mode
# #                 msg.append(to_address//256)          # high address byte
# #                 msg.append(to_address%256)           # low address byte
# #                 msg.append(to_channel)               # channel
#             if type(payload) == dict:
#                 js_payload = ujson.dumps(payload)     # convert payload to JSON string
#             else:
#                 js_payload = payload
#             for i in range(len(js_payload)):      # message
#                 msg.append(ord(js_payload[i]))    # ascii code of character
#             if useChecksum:                       # attach 2's complement checksum
#                 msg.append(int(self.calcChecksum(js_payload), 16))
#             # debug
#             if self.debug:
#                 print('msg', msg)
#             # wait for idle module
#             self.waitForDeviceIdle()
#             # send the message
#             self.serdev.write(bytes(msg))
# #            print(js_payload, msg)
#             return 'OK sendMessage'
#         
#         except Exception as E:
#             if self.debug:
#                 print('Error on sendMessage: ',E)
#             return 'NOK sendMessage'
#         
#         
#     def recvMessage(self, from_address, from_channel, useChecksum=False):
#         ''' Receive payload messages from ebyte E32 LoRa modules in transparent or fixed mode. The payload is a JSON string
#             of a data dictionary to accomodate key value pairs commonly used to store sensor data. If checksumming is used, the
#             checksum of the received payload including the checksum byte should result in 0 for a correct transmission.
#             - transparent mode : payload will be received if the module has the same address and channel of the transmitter
#             - fixed mode : only payloads from transmitters with this address and channel will be received;
#                            if the address is 0xFFFF, payloads from all transmitters with this channel will be received'''
#         try:
#             # type of transmission
#             if (from_address == self.config['address']) and (from_channel == self.config['channel']):
#                 # transparent transmission mode
#                 # all modules with the same address and channel will receive the message
#                 self.setTransmissionMode(0)
#             else:
#                 # fixed transmission mode
#                 # only the module with the target address and channel will receive the message
#                 self.setTransmissionMode(1)
#             # put into normal mode
#             self.setOperationMode('normal')
#             # receive message
#             js_payload = None
#             if self.serdev.any():
#                 js_payload = self.serdev.read()
#             # debug
# #             if self.debug:
# #                 print('js_payload', js_payload)
#             # did we receive anything ?
#             if js_payload == None:
#                 # nothing
#                 return None
#             else :
#                 # decode message
#                 msg = ''
#                 for i in range(len(js_payload)):
#                     msg += chr(js_payload[i])
#                 if self.debug:
#                     print('msg', msg)
#                 # checksum check
#                 if useChecksum:
#                     cs = int(self.calcChecksum(msg),16)
#                     if cs != 0:
#                         # corrupt
#                         return 'corrupt message >' + msg + ' <, checksum ' + str(cs) 
#                     else:
#                         # message ok, remove checksum
#                         msg = msg[:-1]
#                 try:
#                     # JSON to dictionary
#                     return ujson.loads(msg)
#                 except:
#                     return msg
#         
#         except Exception as E:
#             if self.debug:
#                 print('Error on recvMessage: ',E)
#             return 'NOK recvMessage'
# 
#     
#     def calcChecksum(self, payload):
#         ''' Calculates checksum for sending/receiving payloads. Sums the ASCII character values mod256 and returns
#             the lower byte of the two's complement of that value in hex notation. '''
#         return '%2X' % (-(sum(ord(c) for c in payload) % 256) & 0xFF)
# 
# 
#     def reset(self):
#         ''' Reset the ebyte E32 Lora module '''
#         try:
#             # send the command
#             res = self.sendCommand('reset')
#             # discard result
#             return 'OK reset'
#           
#         except Exception as E:
#             if self.debug:
#                 print('error on reset', E)
#             return 'NOK reset'
# 
# 
#     def stop(self):
#         ''' Stop the ebyte E32 LoRa module '''
#         try:
#             if self.serdev != None:
#                 self.serdev.deinit()
#                 del self.serdev
#             return 'OK stop'
#             
#         except Exception as E:
#             if self.debug:
#                 print('error on stop UART', E)
#             return 'NOK stop'
#         
#     
#     def sendCommand(self, command):
#         ''' Send a command to the ebyte E32 LoRa module.
#             The module has to be in sleep mode '''
#         try:
#             # put into sleep mode
#             self.setOperationMode('sleep')
#             # send command
#             HexCmd = ebyteE32.CMDS.get(command)
#             if self.debug:
#                 print('HexCmd', HexCmd)
#             if HexCmd in [0xC0, 0xC2]:        # set config to device
#                 header = HexCmd
#                 HexCmd = self.encodeConfig()
#                 HexCmd[0] = header
#             else:                             # get config, get version, reset
#                 HexCmd = [HexCmd]*3
#             if self.debug:
#                 print('HexCmd', HexCmd)
#             n = self.serdev.write(bytes(HexCmd))
#             if n != len(HexCmd):
#                 print('Error on serdev.write()', n)
#                 return 'NOK sendCommand'    
#             # wait for result
#             utime.sleep_ms(50)
#             # read result
#             if command == 'reset':
#                 result = ''
#             else:
#                 result = self.serdev.read()
#                 # wait for result
#                 utime.sleep_ms(50)
#                 # debug
#                 if self.debug:
#                     print('result', result)
#             return result
#         
#         except Exception as E:
#             if self.debug:
#                 print('Error on sendCommand: ',E)
#             return 'NOK sendCommand'
#         
#         
#     
#     def getVersion(self):
#         ''' Get the version info from the ebyte E32 LoRa module '''
#         try:
#             # send the command
#             result = self.sendCommand('getVersion')
#             # check result
#             if len(result) != 4:
#                 return 'NOK getVersion'
#             # decode result
#             freq = ebyteE32.FREQV.get(hex(result[1]),'unknown')
#             # show version
#             if result[0] == 0xc3:
#                 print('================= E32 MODULE ===================')
#                 print('model       \t%dMhz'%(freq))
#                 print('version     \t%d'%(result[2]))
#                 print('features    \t%d'%(result[3]))
#                 print('================================================')
#             return 'OK getVersion'
#         
#         except Exception as E:
#             if self.debug:
#                 print('Error on getVersion: ',E)
#             return 'NOK getVersion'
#         
#     
#     def getConfig(self):
#         ''' Get config parameters from the ebyte E32 LoRa module '''
#         try:
#             # send the command
#             result = self.sendCommand('getConfig')
#             # check result
#             if len(result) != 6:
#                 return 'NOK getConfig'
#             # decode result
#             self.decodeConfig(result)
#             # show config
#             self.showConfig()
#             return 'OK getConfig'
# 
#         except Exception as E:
#             if self.debug:
#                 print('Error on getConfig: ',E)
#             return 'NOK getConfig'  
#     
# 
#     def decodeConfig(self, message):
#         ''' decode the config message from the ebyte E32 LoRa module to update the config dictionary '''
#         # message byte 0 = header
#         header = int(message[0])
#         # message byte 1 & 2 = address
#         self.config['address'] = int(message[1])*256 + int(message[2])
#         # message byte 3 = speed (parity, baudrate, datarate)
#         bits = '{0:08b}'.format(message[3])
#         self.config['parity'] = ebyteE32.PARINV.get(bits[0:2])
#         self.config['baudrate'] = ebyteE32.BAUDRINV.get(bits[2:5])
#         self.config['datarate'] = ebyteE32.DATARINV.get(bits[5:])
#         # message byte 4 = channel
#         self.config['channel'] = int(message[4])
#         # message byte 5 = option (transmode, iomode, wutime, fec, txpower)
#         bits = '{0:08b}'.format(message[5])
#         self.config['transmode'] = int(bits[0:1])
#         self.config['iomode'] = int(bits[1:2])
#         self.config['wutime'] = int(bits[2:5])
#         self.config['fec'] = int(bits[5:6])
#         self.config['txpower'] = int(bits[6:])
#         
#     
#     def encodeConfig(self):
#         ''' encode the config dictionary to create the config message of the ebyte E32 LoRa module '''
#         # Initialize config message
#         message = []
#         # message byte 0 = header
#         message.append(0xC0)
#         # message byte 1 = high address
#         message.append(self.config['address']//256)
#         # message byte 2 = low address
#         message.append(self.config['address']%256)
#         # message byte 3 = speed (parity, baudrate, datarate)
#         bits = '0b'
#         bits += ebyteE32.PARSTR.get(self.config['parity'])
#         bits += ebyteE32.BAUDRATE.get(self.config['baudrate'])
#         bits += ebyteE32.DATARATE.get(self.config['datarate'])
#         message.append(int(bits))
#         # message byte 4 = channel
#         message.append(self.config['channel'])
#         # message byte 5 = option (transmode, iomode, wutime, fec, txpower)
#         bits = '0b'
#         bits += str(self.config['transmode'])
#         bits += str(self.config['iomode'])
#         bits += '{0:03b}'.format(self.config['wutime'])
#         bits += str(self.config['fec'])
#         bits += '{0:02b}'.format(self.config['txpower'])
#         message.append(int(bits))
#         return message
#     
# 
#     def showConfig(self):
#         ''' Show the config parameters of the ebyte E32 LoRa module on the shell '''
#         print('=================== CONFIG =====================')
#         print('model       \tE32-%s'%(self.config['model']))
#         print('frequency   \t%dMhz'%(self.config['frequency']))
#         print('address     \t0x%04x'%(self.config['address']))
#         print('channel     \t0x%02x'%(self.config['channel']))
#         print('datarate    \t%sbps'%(self.config['datarate']))                
#         print('port        \t%s'%(self.config['port']))
#         print('baudrate    \t%dbps'%(self.config['baudrate']))
#         print('parity      \t%s'%(self.config['parity']))
#         print('transmission\t%s'%(ebyteE32.TRANSMODE.get(self.config['transmode'])))
#         print('IO mode     \t%s'%(ebyteE32.IOMODE.get(self.config['iomode'])))
#         print('wakeup time \t%s'%(ebyteE32.WUTIME.get(self.config['wutime'])))
#         print('FEC         \t%s'%(ebyteE32.FEC.get(self.config['fec'])))
#         maxp = ebyteE32.MAXPOW.get(self.config['model'][3:6], 0)
#         print('TX power    \t%s'%(ebyteE32.TXPOWER.get(self.config['txpower'])[maxp]))
#         print('================================================')
# 
# 
#     def waitForDeviceIdle(self):
#         ''' Wait for the E32 LoRa module to become idle (AUX pin high) '''
#         if self.AUX is None:
#             utime.sleep_ms(500)
#             return
#         
#         count = 0
#         # loop for device busy
#         while not self.AUX.value():
#             # increment count
#             count += 1
#             # maximum wait time 100 ms
#             if count == 10:
#                 break
#             # sleep for 10 ms
#             utime.sleep_ms(10)
#             
#             
#     def saveConfigToJson(self):
#         ''' Save config dictionary to JSON file ''' 
#         with open('E32config.json', 'w') as outfile:  
#             ujson.dump(self.config, outfile)    
# 
# 
#     def loadConfigFromJson(self):
#         ''' Load config dictionary from JSON file ''' 
#         with open('E32config.json', 'r') as infile:
#             result = ujson.load(infile)
#         print(self.config)
#         
#     
#     def calcFrequency(self):
#         ''' Calculate the frequency (= minimum frequency + channel * 1MHz)''' 
#         # get minimum and maximum frequency
#         freqkey = int(self.config['model'].split('T')[0])
#         minfreq = ebyteE32.FREQ.get(freqkey)[0]
#         maxfreq = ebyteE32.FREQ.get(freqkey)[2]
#         # calculate frequency
#         freq = minfreq + self.config['channel']
#         if freq > maxfreq:
#             self.config['frequency'] = maxfreq
#             self.config['channel'] = hex(maxfreq - minfreq)
#         else:
#             self.config['frequency'] = freq
# 
#         
#     def setTransmissionMode(self, transmode):
#         ''' Set the transmission mode of the E32 LoRa module '''
#         if transmode != self.config['transmode']:
#             self.config['transmode'] = transmode
#             self.setConfig('setConfigPwrDwnSave')
#             
#             
#     def setConfig(self, save_cmd):
#         ''' Set config parameters for the ebyte E32 LoRa module '''
#         try:
#             # send the command
#             result = self.sendCommand(save_cmd)
#             # check result
#             if len(result) != 6:
#                 return 'NOK setConfig'
#             # debug 
#             if self.debug:
#                 # decode result
#                 self.decodeConfig(result) 
#                 # show config
#                 self.showConfig()
#             # save config to json file
# #            self.saveConfigToJson()
#             return 'OK setConfig'
#         
#         except Exception as E:
#             if self.debug: 
#                 print('Error on setConfig: ',E)
#             return 'NOK setConfig'  
#  
# 
#     def setOperationMode(self, mode):
#         ''' Set operation mode of the E32 LoRa module '''
#         # get operation mode settings (default normal)
#         bits = ebyteE32.OPERMODE.get(mode, '00')
# #         if self.debug:
# #             print('mode, bits', mode, bits)
#         # set operation mode
#         self.M0.value(int(bits[0]))
#         self.M1.value(int(bits[1]))
#         # wait a moment
#         utime.sleep_ms(50)
