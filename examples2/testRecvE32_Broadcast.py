###########################################
# receiving fixed broadcast
###########################################
# transmitter - address 0001 - channel 02
# message     - address FFFF - channel 04
# receiver(s) - address 0003 - channel 04
###########################################

from LoRaE32_win import ebyteE32_win as ebyteE32

import time

e32 = ebyteE32(Port='COM3', Address=0x0003, Channel=0x04, debug=False)

e32.start()
e32.setConfig('setConfigPwrDwnNoSave')
e32.getVersion()
e32.getConfig()

from_address = 0xFFFF
from_channel = 0x04

while True:
    print('Receiving fixed broadcast : address %d - channel %d'%(from_address, from_channel), end='')
    message = e32.recvMessage(from_address, from_channel, useChecksum=True)
    print(' - message %s'%(message))
    time.sleep(2.000)

e32.stop()