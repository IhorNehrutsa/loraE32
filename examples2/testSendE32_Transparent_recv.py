###########################################
# sending transparent 
###########################################
# transmitter - address 0001 - channel 02
# message     - address 0001 - channel 02
# receiver(s) - address 0001 - channel 02
###########################################
import time

from LoRaE32_win import ebyteE32_win as ebyteE32
e32 = ebyteE32(Port='COM17', Baudrate=115200, AirDataRate='0.3k', Address=0x0001, Channel=0x02, debug=False)

# from LoRaE32_ESP32 import ebyteE32_ESP32 as ebyteE32
# M0pin = 18
# M1pin = 5
# AUXpin = 4
# e32 = ebyteE32(M0pin, M1pin, AUXpin, Baudrate=115200, AirDataRate='0.3k', Address=0x0001, Channel=0x02, debug=False)

e32.start()
#e32.reset()
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
t1 = time.time() - 100
ts = time.time()
te = time.time()
MSG_LEN = 0

err = 0
message_flow = b''
try:
    while True:
        if e32.getAUX():
        #if e32.is_AUX_high(0.005):
            t2 = time.time()
            if t2 - te > te - ts + 4:
            #if True:
                message = '>START   #'
                message += ' %8d '%(teller)
                message += '- %7.3f - %7.3f '%(te-ts, t2-t1) + '1234567890' * 10  # 150 # 45 # 46 # 240 # 
                
    #             n = e32.PACKET_SIZE - len(message) % e32.PACKET_SIZE - 10 - 1
    #             if n > 0:
    #                 message += '-' * n

                message += ' %8d ' % (len(message) + 20)
                message += '      END<\n'

                MSG_LEN = len(message) - 1

                print()
                print('Sending - address %s - channel %d - len %d\n%s'%(to_address, to_channel, len(message), message), end='')
                ts = time.time()
                #e32.sendMessage(to_address, to_channel, message, useChecksum=False)
                e32.sendMessage(message)
                te = time.time()
                print('Sended.')
                teller += 1
                t1 = t2
        
            time.sleep(1)
            
        #msg = e32.recvMessage(from_address, from_channel, useChecksum=False)
        #msg = e32.receive_message_wait1()
        #msg = e32.receive_message_wait2()
        msg = e32.receive_message()  # faster
        #msg = e32.receive_message2()  # slower
        if msg:
            if 1:
                msg = str(msg, 'UTF-8')
                #print(msg)
                print(msg, end='')
                #print('' , len(msg), msg, end='')
                #print('\n' , len(msg), msg)
            else:
                #print(msg)
                message_flow +=msg
                #print('message_flow=', message_flow)
                start = message_flow.find(b'>START')
                end = message_flow.rfind(b'END<')
                if (start >= 0) and (end > 0) and (start < end):
                    message = message_flow[start:end+4]
                    message = str(message, 'UTF-8')
                    if len(message) != MSG_LEN:
                        err += 1
                    print('Received - address %s - channel %d - len %d - err %d'% (from_address, from_channel, len(message), err), False if len(message) != MSG_LEN else '')
                    print(message)
                    message_flow = message_flow[end+4+1:]
                    #print(len(message_flow), message_flow)

finally:
    e32.stop()
