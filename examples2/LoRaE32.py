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
import json


class ebyteE32:
    ''' class to interface an ESP32 via serial commands to the EBYTE E32 Series LoRa modules '''

    PACKET_SIZE = 58 ## 58-ok # 512-ok
    
    # UART parity strings
    PARSTR = { '8N1':'00', '8O1':'01', '8E1':'10' }
    PARINV = { v:k for k, v in PARSTR.items() }
    # UART parity bits
    PARBIT = { 'N':None, 'E':0, 'O':1 }
    # UART baudrate
    BAUDRATE = { 1200:'000', 2400:'001', 4800:'010', 9600:'011',
                 19200:'100', 38400:'101', 57600:'110', 115200:'111' }
    BAUDRINV = { v:k for k, v in BAUDRATE.items() }
    # LoRa datarate
    DATARATE = { '0.3k':'000', '1.2k':'001', '2.4k':'010',
                 '4.8k':'011', '9.6k':'100', '19.2k':'101' }
    DATARINV = { v:k for k, v in DATARATE.items() }
    # Commands
    CMDS = { 'setConfigPwrDwnSave':0xC0,
             'getConfig':0xC1,
             'setConfigPwrDwnNoSave':0xC2,
             'getVersion':0xC3,
             'reset':0xC4 }
    # operation modes (set with M0 & M1)
    OPERMODE = { 'normal':'00', 'wakeup':'10', 'powersave':'01', 'sleep':'11' }
    # model frequency ranges (MHz)
    FREQ = { 170:[160, 170, 173], 400:[410, 470, 525], 433:[410, 433, 441],
             868:[862, 868, 893], 915:[900, 915, 931] }
    # version info frequency
    FREQV = { '0x32':433, '0x38':470, '0x45':868, '0x44':915, '0x46':170 }
    # model maximum transmision power
    # 20dBm = 100mW - 27dBm = 500 mW - 30dBm = 1000 mW (1 W)
    MAXPOW = { 'T20':0, 'T27':1, 'T30':2 }
    # transmission mode
    TRANSMODE = { 0:'transparent', 1:'fixed' }
    # IO drive mode
    IOMODE = { 0:'TXD AUX floating output, RXD floating input',
               1:'TXD AUX push-pull output, RXD pull-up input' }
    # wireless wakeup times from sleep mode
    WUTIME = { 0b000:'250ms', 0b001:'500ms', 0b010:'750ms', 0b011:'1000ms',
               0b100:'1250ms', 0b101:'1500ms', 0b110:'1750ms', 0b111:'2000ms' }
    # Forward Error Correction (FEC) mode
    FEC = { 0:'off', 1:'on' }
    # transmission power T20/T27/T30 (dBm)
    TXPOWER = { '00':['20dBm', '27dBm', '30dBm'],
                '01':['17dBm', '24dBm', '27dBm'],
                '10':['14dBm', '21dBm', '24dBm'],
                '11':['10dBm', '18dBm', '21dBm'] }

    def __init__(self, Model='433T30D', Port='U2', Baudrate=9600, Parity='8N1', AirDataRate='2.4k', Address=0x0000, Channel=0x17, debug=False):
        ''' constructor for ebyte E32 LoRa module '''
        # configuration in dictionary
        self.config = {}
        self.config['model'] = Model               # E32 model (default 868T20D)
        self.config['port'] = Port                 # UART channel on the ESP (default U1)
        self.config['baudrate'] = Baudrate         # UART baudrate (default 9600)
        self.config['parity'] = Parity             # UART Parity (default 8N1)
        self.config['datarate'] = AirDataRate      # wireless baudrate (default 2.4k)
        self.config['address'] = Address           # target address (default 0x0000)
        self.config['channel'] = Channel           # target channel (0-31, default 0x06)
        self.calcFrequency()                       # calculate frequency (min frequency + channel*1 MHz)
        self.config['transmode'] = 0               # transmission mode (default 0 - tranparent)
        self.config['iomode'] = 1                  # IO mode (default 1 = not floating)
        self.config['wutime'] = 0                  # wakeup time from sleep mode (default 0 = 250ms)
        self.config['fec'] = 1                     # forward error correction (default 1 = on)
        self.config['txpower'] = '00'              # transmission power (default 0 = 20dBm/100mW)
        # 
        self.serdev = None                         # instance for UART
        self.debug = debug
        

    def start(self):
        ''' Start the ebyte E32 LoRa module '''
        # check parameters
        if int(self.config['model'].split('T')[0]) not in self.FREQ:
            self.config['model'] = '868T20D'
        #if self.config['port'] not in self.PORT:
        #    self.config['port'] = 'U1'
        if int(self.config['baudrate']) not in self.BAUDRATE:    
            self.config['baudrate'] = 9600
        if self.config['parity'] not in self.PARSTR:
            self.config['parity'] = '8N1'
        if self.config['datarate'] not in self.DATARATE:
            self.config['datarate'] = '2.4k'
        if self.config['channel'] > 31:
            self.config['channel'] = 31

        # set config to the ebyte E32 LoRa module
        # self.setConfig('setConfigPwrDwnNoSave')
        
    def configMessage(self, to_address, to_channel):
        # type of transmission
        if (to_address == self.config['address']) and (to_channel == self.config['channel']):
            # transparent transmission mode
            # print('transparent transmission mode')
            # all modules with the same address and channel will receive the payload
            self.setTransmissionMode(0)
        else:
            # fixed transmission mode
            # print('fixed transmission mode')
            # only the module with the target address and channel will receive the payload
            self.setTransmissionMode(1)
        # put into wakeup mode (includes preamble signals to wake up device in powersave or sleep mode)
        #self.setOperationMode('wakeup')
        self.setOperationMode('normal')
        self.flush()
        time.sleep(0.050)
        self.waitForDeviceIdle()
        time.sleep(0.050)
  
    def sendMessage(self, to_address, to_channel, payload, useChecksum=False):
        ''' Send the payload to ebyte E32 LoRa modules in transparent or fixed mode. The payload is a data dictionary to
            accomodate key value pairs commonly used to store sensor data and is converted to a JSON string before sending.
            The payload can be appended with a 2's complement checksum to validate correct transmission.
            - transparent mode : all modules with the same address and channel of the transmitter will receive the payload
            - fixed mode : only the module with this address and channel will receive the payload;
                           if the address is 0xFFFF all modules with the same channel will receive the payload'''
#         # type of transmission
#         if (to_address == self.config['address']) and (to_channel == self.config['channel']):
#             # transparent transmission mode
#             # print('transparent transmission mode')
#             # all modules with the same address and channel will receive the payload
#             self.setTransmissionMode(0)
#         else:
#             # fixed transmission mode
#             # print('fixed transmission mode')
#             # only the module with the target address and channel will receive the payload
#             self.setTransmissionMode(1)
#         # put into wakeup mode (includes preamble signals to wake up device in powersave or sleep mode)
#         #self.setOperationMode('wakeup')
#         self.setOperationMode('normal')
            
        # check payload
        if (type(payload) != dict) and (type(payload) != str):
            print('payload is not a dictionary or str', payload)
            return 'NOK sendMessage'
        # encode message
        msg = b''
        if self.config['transmode'] == 1:     # only for fixed transmission mode
            1/0
#             msg.append(to_address//256)          # high address byte
#             msg.append(to_address%256)           # low address byte
#             msg.append(to_channel)               # channel
            msg = bytes([to_address//256, to_address%256, to_channel])
        if type(payload) == dict:
            js_payload = json.dumps(payload)     # convert payload to JSON string
        else:
            js_payload = payload
        
#             for i in range(len(js_payload)):      # message
#                 msg.append(ord(js_payload[i]))    # ascii code of character
        
        #msg += js_payload.encode(encoding='UTF-8')
        msg += js_payload.encode('UTF-8')
        
        if useChecksum:                       # attach 2's complement checksum
            msg.append(int(self.calcChecksum(js_payload), 16))
        # debug
        if self.debug:
            print('msg', msg)
        
        #print('msg', msg)
        
        sended = 0
        while sended < len(msg):
            if self.getAUX():
                # wait for idle module
                self.flush()
                time.sleep(0.050) # 5ms
                self.waitForDeviceIdle()
                time.sleep(0.050) # 5ms
                # send the message
                #print(sended, msg[sended:sended + self.PACKET_SIZE])
                # n = self.serdev.write(bytes(msg[sended:sended + self.PACKET_SIZE]))
                n = self.serdev.write(msg[sended:sended + self.PACKET_SIZE])
                if n > 0:
                    sended += n
                    self.flush()
#                 if self.getAUX():
#                     sended += n
            #print(sended, n, msg[sended])
            #print(sended, msg[sended:sended + self.PACKET_SIZE])
            
#            print(js_payload, msg)
        
#             n = self.PACKET_SIZE - len(msg) % self.PACKET_SIZE
#             if n > 0:
#                 self.serdev.write(b' ' * n)

#         self.waitForDeviceIdle()
#         time.sleep(0.050) # 5ms
#         self.flush()
#         time.sleep(0.050) # 5ms
#         self.waitForDeviceIdle()
#         time.sleep(0.050) # 5ms
#         return 'OK sendMessage'
        
        
    def recvMessage(self, from_address, from_channel, useChecksum=False):
        ''' Receive payload messages from ebyte E32 LoRa modules in transparent or fixed mode. The payload is a JSON string
            of a data dictionary to accomodate key value pairs commonly used to store sensor data. If checksumming is used, the
            checksum of the received payload including the checksum byte should result in 0 for a correct transmission.
            - transparent mode : payload will be received if the module has the same address and channel of the transmitter
            - fixed mode : only payloads from transmitters with this address and channel will be received;
                           if the address is 0xFFFF, payloads from all transmitters with this channel will be received'''
#         # type of transmission
#         if (from_address == self.config['address']) and (from_channel == self.config['channel']):
#             # transparent transmission mode
#             # print('transparent transmission mode')
#             # all modules with the same address and channel will receive the message
#             self.setTransmissionMode(0)
#         else:
#             # fixed transmission mode
#             # print('fixed transmission mode')
#             # only the module with the target address and channel will receive the message
#             self.setTransmissionMode(1)
#         # put into normal mode
#         self.setOperationMode('normal')
            
            
        # receive message
        js_payload = self.read()
        # debug
#             if self.debug:
#                 print('js_payload', js_payload)
        # did we receive anything ?
        if (js_payload == b'') or (js_payload == None):
            # nothing
            return b''
        else :
            # return js_payload.decode('ascii')
            #return str(js_payload, 'ascii')
            #return str(js_payload, 'UTF-8')
            
            # decode message
            msg = ''
            for i in range(len(js_payload)):
                msg += chr(js_payload[i])
            if self.debug:
                print('msg', msg)
            # checksum check
            if useChecksum:
                cs = int(self.calcChecksum(msg),16)
                if cs != 0:
                    # corrupt
                    return 'corrupt message >' + msg + ' <, checksum ' + str(cs) 
                else:
                    # message ok, remove checksum
                    msg = msg[:-1]
#                 try:
#                     # JSON to dictionary
#                     return json.loads(msg)
#                 except:
#                     return msg
            return msg
        
    
    def calcChecksum(self, payload):
        ''' Calculates checksum for sending/receiving payloads. Sums the ASCII character values mod256 and returns
            the lower byte of the two's complement of that value in hex notation. '''
        return '%2X' % (-(sum(ord(c) for c in payload) % 256) & 0xFF)


    def reset(self):
        ''' Reset the ebyte E32 Lora module '''
        try:
            # send the command
            res = self.sendCommand('reset')
            # discard result
            return 'OK reset'
          
        except Exception as E:
            if self.debug:
                print('error on reset', E)
            return 'NOK reset'


    def stop(self):
        ''' Stop the ebyte E32 LoRa module '''
        try:
            if self.serdev != None:
                try:
                    self.serdev.deinit()
                except:
                    self.serdev.close()
                del self.serdev
            return 'OK stop'
            
        except Exception as E:
            if self.debug:
                print('error on stop UART', E)
            return 'NOK stop'
        
    
    def sendCommand(self, command):
        ''' Send a command to the ebyte E32 LoRa module.
            The module has to be in sleep mode '''
        # put into sleep mode
        self.setOperationMode('sleep')
        # send command
        HexCmd = self.CMDS.get(command)
        if self.debug:
            print('HexCmd', HexCmd)
        if HexCmd in [0xC0, 0xC2]:        # set config to device
            header = HexCmd
            HexCmd = self.encodeConfig()
            HexCmd[0] = header
        else:                             # get config, get version, reset
            HexCmd = [HexCmd]*3
        if self.debug:
            print('HexCmd', HexCmd)
        if self.config['baudrate'] != 9600:
            self.serdev.baudrate = 9600;
        n = self.serdev.write(bytes(HexCmd))
        if n != len(HexCmd):
            print('Error on serdev.write()', n)
            return 'NOK sendCommand'    
        # wait for result
        time.sleep(0.050)
        # read result
        if command == 'reset':
            result = b''
        else:
            result = self.read()
            # wait for result
            time.sleep(0.050)
            # debug
            if self.debug:
                print('result', result)
        if self.config['baudrate'] != 9600:
            self.serdev.baudrate = self.config['baudrate'];
        return result
        
    
    def getVersion(self):
        ''' Get the version info from the ebyte E32 LoRa module '''
        try:
            # send the command
            result = self.sendCommand('getVersion')
            # check result
            if len(result) != 4:
                return 'NOK getVersion'
            # decode result
            freq = self.FREQV.get(hex(result[1]),'unknown')
            # show version
            if result[0] == 0xc3:
                print('================= E32 MODULE ===================')
                print('model       \t%dMhz'%(freq))
                print('version     \t%d'%(result[2]))
                print('features    \t%d'%(result[3]))
                print('================================================')
            return 'OK getVersion'
        
        except Exception as E:
            if self.debug:
                print('Error on getVersion: ',E)
            return 'NOK getVersion'
        
    
    def getConfig(self):
        ''' Get config parameters from the ebyte E32 LoRa module '''
        try:
            # send the command
            result = self.sendCommand('getConfig')
            # check result
            if len(result) != 6:
                return 'NOK getConfig'
            # decode result
            self.decodeConfig(result)
            # show config
            self.showConfig()
            return 'OK getConfig'

        except Exception as E:
            if self.debug:
                print('Error on getConfig: ',E)
            return 'NOK getConfig'  
    

    def decodeConfig(self, message):
        ''' decode the config message from the ebyte E32 LoRa module to update the config dictionary '''
        # message byte 0 = header
        header = int(message[0])
        # message byte 1 & 2 = address
        self.config['address'] = int(message[1])*256 + int(message[2])
        # message byte 3 = speed (parity, baudrate, datarate)
        bits = '{0:08b}'.format(message[3])
        self.config['parity'] = self.PARINV.get(bits[0:2])
        self.config['baudrate'] = self.BAUDRINV.get(bits[2:5])
        self.config['datarate'] = self.DATARINV.get(bits[5:])
        # message byte 4 = channel
        self.config['channel'] = int(message[4])
        # message byte 5 = option (transmode, iomode, wutime, fec, txpower)
        bits = '{0:08b}'.format(message[5])
        self.config['transmode'] = int(bits[0:1])
        self.config['iomode'] = int(bits[1:2])
        self.config['wutime'] = int(bits[2:5])
        self.config['fec'] = int(bits[5:6])
        self.config['txpower'] = bits[6:]
        
    
    def encodeConfig(self):
        ''' encode the config dictionary to create the config message of the ebyte E32 LoRa module '''
        # Initialize config message
        message = []
        # message byte 0 = header
        message.append(0xC0)
        # message byte 1 = high address
        message.append(self.config['address']//256)
        # message byte 2 = low address
        message.append(self.config['address']%256)
        # message byte 3 = speed (parity, baudrate, datarate)
        bits = '0b'
        bits += self.PARSTR.get(self.config['parity'])
        bits += self.BAUDRATE.get(self.config['baudrate'])
        bits += self.DATARATE.get(self.config['datarate'])
        message.append(int(bits, 2))
        # message byte 4 = channel
        message.append(self.config['channel'])
        # message byte 5 = option (transmode, iomode, wutime, fec, txpower)
        bits = '0b'
        bits += str(self.config['transmode'])
        bits += str(self.config['iomode'])
        bits += '{0:03b}'.format(self.config['wutime'])
        bits += str(self.config['fec'])
        bits += self.config['txpower']
        message.append(int(bits, 2))
        return message
    

    def showConfig(self):
        ''' Show the config parameters of the ebyte E32 LoRa module on the shell '''
        print('=================== CONFIG =====================')
        print('model       \tE32-%s'%(self.config['model']))
        print('frequency   \t%dMhz'%(self.config['frequency']))
        print('address     \t0x%04x'%(self.config['address']))
        print('channel     \t0x%02x'%(self.config['channel']))
        print('datarate    \t%sbps'%(self.config['datarate']))                
        print('port        \t%s'%(self.config['port']))
        print('baudrate    \t%dbps'%(self.config['baudrate']))
        print('parity      \t%s'%(self.config['parity']))
        print('transmission\t%s'%(self.TRANSMODE.get(self.config['transmode'])))
        print('IO mode     \t%s'%(self.IOMODE.get(self.config['iomode'])))
        print('wakeup time \t%s'%(self.WUTIME.get(self.config['wutime'])))
        print('FEC         \t%s'%(self.FEC.get(self.config['fec'])))
        maxp = self.MAXPOW.get(self.config['model'][3:6], 0)
        print('TX power    \t%s'%(self.TXPOWER.get(self.config['txpower'])[maxp]))
        print('================================================')


    def is_any(self):
        # abstract
        raise NotImplementedError("Please implement abstruct method")
    
    def read(self)->bytes:
        # abstract
        raise NotImplementedError("Please implement abstruct method")
    
    def setM0(self, value):
        # abstract
        raise NotImplementedError("Please implement abstruct method")
    
    def setM1(self, value):
        # abstract
        raise NotImplementedError("Please implement abstruct method")
    
    def getAUX(self):
        # abstract
        raise NotImplementedError("Please implement abstruct method")
    
    def flush(self):
        # abstract
        raise NotImplementedError("Please implement abstruct method")

    def waitForDeviceIdle(self):
        ''' Wait for the E32 LoRa module to become idle (AUX pin high) '''
#         if self.getAUX() is None:
#             time.sleep(0.500)
#             return
#         
#         count = 0
        # loop for device busy
        while not self.getAUX():
            pass # wait
        time.sleep(0.050)
        while not self.getAUX():
            pass # wait
#             # increment count
#             count += 1
#             # maximum wait time 100 ms
#             if count == 10:
#                 break
#             # sleep for 10 ms
#             time.sleep(0.010)
            
            
    def saveConfigToJson(self):
        ''' Save config dictionary to JSON file ''' 
        with open('E32config.json', 'w') as outfile:  
            json.dump(self.config, outfile)    


    def loadConfigFromJson(self):
        ''' Load config dictionary from JSON file ''' 
        with open('E32config.json', 'r') as infile:
            result = json.load(infile)
        print(self.config)
        
    
    def calcFrequency(self):
        ''' Calculate the frequency (= minimum frequency + channel * 1MHz)''' 
        # get minimum and maximum frequency
        freqkey = int(self.config['model'].split('T')[0])
        minfreq = self.FREQ.get(freqkey)[0]
        maxfreq = self.FREQ.get(freqkey)[2]
        # calculate frequency
        freq = minfreq + self.config['channel']
        if freq > maxfreq:
            self.config['frequency'] = maxfreq
            self.config['channel'] = hex(maxfreq - minfreq)
        else:
            self.config['frequency'] = freq

        
    def setTransmissionMode(self, transmode):
        ''' Set the transmission mode of the E32 LoRa module '''
        if transmode != self.config['transmode']:
            self.config['transmode'] = transmode
            self.setConfig('setConfigPwrDwnNoSave')
            
            
    def setConfig(self, save_cmd):
        ''' Set config parameters for the ebyte E32 LoRa module '''
        # send the command
        result = self.sendCommand(save_cmd)
        # check result
        if len(result) != 6:
            return 'NOK setConfig'
        # debug 
        if self.debug:
            # decode result
            self.decodeConfig(result) 
            # show config
            self.showConfig()
        # save config to json file
#            self.saveConfigToJson()
        return 'OK setConfig'


    def setOperationMode(self, mode):
        ''' Set operation mode of the E32 LoRa module '''
        # get operation mode settings (default normal)
        bits = self.OPERMODE.get(mode, '00')
#         if self.debug:
#             print('mode, bits', mode, bits)
        # set operation mode
        self.setM0(int(bits[0]))
        self.setM1(int(bits[1]))
        # wait a moment
        time.sleep(0.050)
