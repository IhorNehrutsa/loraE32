###########################################
# sending transparent 
###########################################
# transmitter - address 0001 - channel 02
# message     - address 0001 - channel 02
# receiver(s) - address 0001 - channel 02
###########################################
import time

from LoRaE32_win import ebyteE32_win as ebyteE32
e32 = ebyteE32(Port='COM3', Baudrate=115200, AirDataRate='9.6k', Address=0x0001, Channel=0x02, debug=False)

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

teller = 1
t1 = 0
ts = time.time()
te = time.time()
MSG_LEN = 0
try:
    while True:
        if e32.getAUX():
        #if e32.is_AUX_high(0.005):
            t2 = time.time()
            if t2 - t1 > 5+7:
                #message = { 'msg': 'HELLO WORLD %s - %s - %f\n'%(str(teller), time.ctime(), t2-t1) }
                message = '>START   #' + '%9d - %7.4f - %7.4f '%(teller, te-ts, t2-t1) + '1234567890' * 40

                #message = '>START   #' + '%9d - %7.4f - %7.4f '%(teller, te-ts, t2-t1) + ' ' * 500
                #message = '>START    ' + '%9d '%(teller) + '1234567890' * 11 # 48
                
    #             n = e32.PACKET_SIZE - len(message) % e32.PACKET_SIZE - 10 - 1
    #             if n > 0:
    #                 message += '-' * n

                message += '      END<\n'

                MSG_LEN = len(message) - 1

                print()
                print('Sending - address %s - channel %d - len %d - message \n%s'%(to_address, to_channel, len(message), message), end='')
                ts = time.time()
                e32.sendMessage(to_address, to_channel, message, useChecksum=False)
                te = time.time()
                print('Sended.')
                teller += 1
                t1 = t2
        
            #time.sleep(5)
            
        #msg = e32.recvMessage(from_address, from_channel, useChecksum=False)
        #msg = e32.receive_message_wait1()
        msg = e32.receive_message_wait2()
        #msg = e32.receive_message1()
        if msg:
            msg = str(msg, 'UTF-8')
            print('Received - address %s - channel %d - len %d'% (from_address, from_channel, len(msg)), False if len(msg) != MSG_LEN else '')
            print(msg)

finally:
    e32.stop()
