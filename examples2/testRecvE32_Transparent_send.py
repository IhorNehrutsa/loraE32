###########################################
# receiving transparent
###########################################
# transmitter - address 0001 - channel 02
# message     - address 0001 - channel 02
# receiver(s) - address 0001 - channel 02
###########################################

MSG_LEN = 12560

import time

from at import *

from LoRaE32_win import ebyteE32_win
e32 = ebyteE32_win(Port='COM4', Baudrate=115200, AirDataRate='19.2k', Address=0x0000, Channel=23, debug=False)

# from LoRaE32_ESP32 import ebyteE32_ESP32 as ebyteE32
# M0pin = 18
# M1pin = 5
# AUXpin = 4
# e32 = ebyteE32(M0pin, M1pin, AUXpin, Baudrate=115200, AirDataRate='0.3k', Address=0x0001, Channel=0x02, debug=False)

e32.start()
#e32.reset()
e32.setConfig('setConfigPwrDwnSave')

from_address = 0x0000 # 0x0001
from_channel = 23 # 0x02

to_address = 0x0000 # 0x0001
to_channel = 23 # 0x02

e32.configMessage(from_address, from_channel)
e32.getVersion()
e32.getConfig()
e32.configMessage(from_address, from_channel)
print()

e32.sendMessage(b"TEST")

err = 0
message_flow = b''
send_counter = 0
try:
    while True:
        #e32.sendMessage('message')
        #print('message')
        #time.sleep(1)
        #continue

        msg = e32.receive_message()
        if msg:
            if 0:
                msg = bytes_to_str(msg)
                #print(msg)
                print(msg, end=' ')
            else:
                #print('msg=', msg)
                message_flow +=msg
                begin = message_flow.find(b'<<<')
                end = message_flow.rfind(b'>>>')
                e = 3
#                 begin = message_flow.find((AT_PATTERN + "SB").encode())
#                 end = message_flow.rfind((AT_PATTERN + "SE").encode())
#                 e = AT_PATTERN_LEN + 2
                if (begin >= 0) and (end > 0) and (begin < end):
                    message = message_flow[begin:end + e]
                    #msg = bytes_to_str(msg)
                    if len(message) != MSG_LEN:
                        err += 1
                    print()
                    print('Received - address %s - channel %d - len %d - err %d'% (from_address, from_channel, len(message), err), False if len(message) != MSG_LEN else '')
                    #print(message)
                    message_flow = message_flow[end + e:]
                    #print('message_flow=', message_flow)

                    print('Sending  - address %s - channel %d - len %d\n%s'%(to_address, to_channel, len(message), message))
                    sended = e32.sendMessage(message)
                    send_counter += 1
                    print('Sended N', send_counter, sended, len(message), sended == len(message))
                    message = ''

finally:
    try:
        e32.serdev.reset_output_buffer()
        e32.serdev.close()
        print('serdev.close()')
    except:
        pass
