###########################################
# sending transparent 
###########################################
# transmitter - address 0001 - channel 02
# message     - address 0001 - channel 02
# receiver(s) - address 0001 - channel 02
###########################################
import time

from LoRaE32_win import ebyteE32_win as ebyteE32
e32 = ebyteE32(Port='COM17', Baudrate=115200, AirDataRate='19.2k', Address=0x0001, Channel=0x02, debug=False)

# from LoRaE32_ESP32 import ebyteE32_ESP32 as ebyteE32
# M0pin = 18
# M1pin = 5
# AUXpin = 4
# e32 = ebyteE32(M0pin, M1pin, AUXpin, Baudrate=38400, AirDataRate='19.2k', Address=0x0001, Channel=0x02, debug=True)

e32.reset()

e32.start()
e32.setConfig('setConfigPwrDwnSave')

to_address = 0x0001
to_channel = 0x02

from_address = 0x0001
from_channel = 0x02

e32.configMessage(to_address, to_channel)
e32.getVersion()
e32.getConfig() 
e32.configMessage(to_address, to_channel)
print()

teller = 0
t1 = time.time()

try:
    while True:
        if e32.getAUX():
            t2 = time.time()
            #message = { 'msg': 'HELLO WORLD %s - %s - %f\n'%(str(teller), time.ctime(), t2-t1) }
            message = '>START    ' + '%9d - %7.4f '%(teller, t2-t1) + '1234567890' * 122
            #message = '>START    ' + '%9d '%(teller) + '1234567890' * 11 # 48
            
#             n = e32.PACKET_SIZE - len(message) % e32.PACKET_SIZE - 10 - 1
#             if n > 0:
#                 message += '-' * n

            message += '      END<\n'
            e32.sendMessage(to_address, to_channel, message, useChecksum=False)
            print('Sending transparent - address %s - channel %d - len %d - message \n%s'%(to_address, to_channel, len(message), message), end='')
            teller += 1
            t1 = t2
            
            #time.sleep(0.05)
            
#         message = e32.recvMessage(from_address, from_channel, useChecksum=False)
#         if message:
#             print('Receiving transparent : address %d - channel %d'%(from_address, from_channel), end='')
#             print(' - message %s'%(message))
#             #time.sleep(2.000)

finally:
    e32.stop()
