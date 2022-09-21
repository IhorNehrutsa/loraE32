###########################################
# receiving transparent
###########################################
# transmitter - address 0001 - channel 02
# message     - address 0001 - channel 02
# receiver(s) - address 0001 - channel 02
###########################################

from LoRaE32_win import ebyteE32_win as ebyteE32
import time

e32 = ebyteE32(Port='COM3', Baudrate=9600, AirDataRate='2.4k', Address=0x0001, Channel=0x02, debug=False)

e32.start()
e32.setConfig('setConfigPwrDwnSave')

from_address = 0x0001
from_channel = 0x02

e32.configMessage(from_address, from_channel)

e32.getVersion()
e32.getConfig()
print()

err = 0
msg = ''
while True:
    message = e32.recvMessage(from_address, from_channel, useChecksum=False)
    if message:
#         print('Receiving transparent : address %d - channel %d'%(from_address, from_channel), end='')
#         print(' - message %s'%(message))
        if 1:
            print(message, end='')
            #print('' , len(message), message, end='')
        else:
            msg +=message
            start = msg.find('>START')
            end = msg.rfind('END<')
            if (start >= 0) and (end > 0) and (start < end):
                Message = msg[start:end+4]
                if len(Message) != 1150:
                    err += 1
                print(len(Message), err, False if len(Message) != 1150 else '')
                print(Message)
                msg = msg[end+4:]
                #print(2, len(msg), msg)

        #time.sleep(2.000)

e32.stop()
