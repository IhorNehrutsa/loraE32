###########################################
# receiving transparent
###########################################
# transmitter - address 0001 - channel 02
# message     - address 0001 - channel 02
# receiver(s) - address 0001 - channel 02
###########################################

MSG_LEN = 1550

from LoRaE32_win import ebyteE32_win as ebyteE32
import time

e32 = ebyteE32(Port='COM4', Baudrate=115200, AirDataRate='9.6k', Address=0x0001, Channel=0x02, debug=False)

e32.reset()

e32.start()
e32.setConfig('setConfigPwrDwnSave')

from_address = 0x0001
from_channel = 0x02

to_address = 0x0001
to_channel = 0x02


e32.configMessage(from_address, from_channel)
e32.getVersion()
e32.getConfig()
e32.configMessage(from_address, from_channel)
print()

err = 0
message_flow = b''
try:
    while True:
        #msg = e32.recvMessage(from_address, from_channel, useChecksum=False)
        msg = e32.receive_message_wait1()
        #msg = e32.receive_message1()
        #msg = e32.receive_message2()
        if msg:
            if 0:
                msg = str(msg, 'UTF-8')
                print(msg)
                #print(msg, end='')
                #print('' , len(msg), msg, end='')
            else:
                #print(msg)
                #print(message_flow)
                message_flow +=msg
                start = message_flow.find(b'>START')
                end = message_flow.rfind(b'END<')
                if (start >= 0) and (end > 0) and (start < end):
                    message = message_flow[start:end+4]
                    message = str(message, 'UTF-8')
                    if len(message) != MSG_LEN:
                        err += 1
                    print()
                    print('Received - address %s - channel %d - len %d - err %d'% (from_address, from_channel, len(message), err), False if len(message) != MSG_LEN else '')
                    print(message)
                    message_flow = message_flow[end+4+1:]
                    #print(len(message_flow), message_flow)

                    if len(message) == MSG_LEN:
                        print('Sending  - address %s - channel %d - len %d\n%s'%(to_address, to_channel, len(message), message))
                        e32.sendMessage(to_address, to_channel, message, useChecksum=False)
                        print('Sended.')
                        message = ''

finally:
    e32.stop()
