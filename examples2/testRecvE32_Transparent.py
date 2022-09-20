###########################################
# receiving transparent
###########################################
# transmitter - address 0001 - channel 02
# message     - address 0001 - channel 02
# receiver(s) - address 0001 - channel 02
###########################################

from LoRaE32_win import ebyteE32_win as ebyteE32
import time

e32 = ebyteE32(Port='COM3', Baudrate=115200, AirDataRate='19.2k', Address=0x0001, Channel=0x02, debug=False)

e32.start()
e32.setConfig('setConfigPwrDwnSave')
e32.getVersion()
e32.getConfig()
print()

from_address = 0x0001
from_channel = 0x02

e32.configMessage(from_address, from_channel)

msg = ''
while True:
    #if e32.is_any():
    message = e32.recvMessage(from_address, from_channel, useChecksum=False)
    if message:
#         print('Receiving transparent : address %d - channel %d'%(from_address, from_channel), end='')
#         print(' - message %s'%(message))
        #print('' , len(message), message, end='')
        if 0:
            print(message, end='')
        else:
            msg +=message
            start = msg.find('>START')
            end = msg.find('END<')
            if (start >= 0) and (end > 0) and (start < end):
                Message = msg[start:end+4]
                print(len(Message))
                print(Message)
                msg = msg[end+4:]
                #print(2, len(msg), msg)

        #time.sleep(2.000)

e32.stop()
