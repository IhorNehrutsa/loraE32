###########################################
# receiving transparent
###########################################
# transmitter - address 0001 - channel 02
# message     - address 0001 - channel 02
# receiver(s) - address 0001 - channel 02
###########################################

MSG_LEN = 2460
MSG_LEN = 560

import time

from LoRaE32_win import ebyteE32_win as ebyteE32
e32 = ebyteE32(Port='COM4', Baudrate=115200, AirDataRate='19.2k', Address=0xFFFF, Channel=23, debug=False)

# from LoRaE32_ESP32 import ebyteE32_ESP32 as ebyteE32
# M0pin = 18
# M1pin = 5
# AUXpin = 4
# e32 = ebyteE32(M0pin, M1pin, AUXpin, Baudrate=115200, AirDataRate='0.3k', Address=0x0001, Channel=0x02, debug=False)

e32.start()
#e32.reset()
e32.setConfig('setConfigPwrDwnSave')

from_address = 0xFFFF # 0x0001
from_channel = 23 # 0x02

to_address = 0xFFFF # 0x0001
to_channel = 23 # 0x02

e32.configMessage(from_address, from_channel)
e32.getVersion()
e32.getConfig()
e32.configMessage(from_address, from_channel)
print()

err = 0
message_flow = b''
try:
    while True:
        #e32.sendMessage('message')
        #print('message')
        #time.sleep(1)
        #continue

        msg = e32.receive_message()
        if msg:
            if 0:
                try:
                    msg = str(msg, 'UTF-8')
                except:
                    msg = msg
                #print(msg)
                print(msg, end='')
                #print('' , len(msg), msg, end='')
                #print('\n' , len(msg), msg)
            else:
                #print(len(msg), msg)
                #print(message_flow)
                message_flow +=msg
                begin = message_flow.find(b'>BEGIN')
                end = message_flow.rfind(b'END<')
                if (begin >= 0) and (end > 0) and (begin < end):
                    message = message_flow[begin:end+4]
                    try:
                        message = str(message, 'UTF-8')
                    except:
                        message = message
                    if len(message) != MSG_LEN:
                        err += 1
                    print()
                    print('Received - address %s - channel %d - len %d - err %d'% (from_address, from_channel, len(message), err), False if len(message) != MSG_LEN else '')
                    print(message)
                    message_flow = message_flow[end+4+1:]
                    #print(len(message_flow), message_flow)

                    if 1:#len(message) == MSG_LEN:
                        print('Sending  - address %s - channel %d - len %d\n%s'%(to_address, to_channel, len(message), message))
                        #e32.sendMessage(to_address, to_channel, message, useChecksum=False)
                        e32.sendMessage(message)
                        print('Sended.')
                        message = ''

finally:
    e32.stop()
