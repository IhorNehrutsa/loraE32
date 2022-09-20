print('echo_beacon_esp32.py')

import time, gc

import machine
from machine_msg import machine_reset_cause

from LoRaE32_ESP32 import ebyteE32_ESP32 as ebyteE32

# check if the device woke from a deep sleep
machine_reset_cause(machine.reset_cause()) 
if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    print('woke from a deep sleep')

BEACON_TIME = 5 # 15 seconds
DEEPSLEEP_TIME = 60_000 # 60 seconds
BEFORE_DEEPSLEEP_TIME = 15 # 60 seconds

M0pin = 18
M1pin = 5
AUXpin = 4

from_address = 0x0000
from_channel = 0x17

to_address = 0x0000
to_channel = 0x17

in_message = None

in_counter = 0
out_counter = 0

tt = 0  # time.time() - BEACON_TIME
ttt = time.time()

try:
    e32 = ebyteE32(M0pin, M1pin, AUXpin, debug=False)
    print(e32.start())
    print(e32.getVersion())
    print(e32.getConfig())

    while True:
        in_message = None
        if e32.is_any():
            in_message = e32.recvMessage(from_address, from_channel, useChecksum=False)
            ttt = time.time()
            
            if in_message:
                in_counter += 1
                if (in_message[-2:] == '\r\n') or (in_message[-2:] == '\n\r'):
                    in_message = in_message[:-2]
                print('IN:', in_counter, '>' , in_message , '<')
                tmp = e32.sendMessage(to_address, to_channel, 'echo:' + in_message, useChecksum=False)
            
        tmp = time.time()
        if tmp >= tt + BEACON_TIME:
            tt = tmp
            out_counter += 1
        
            t = time.localtime()
            out_message = 'beacon: %02d/%02d/%d %2d:%02d:%02d %d' % (t[2], t[1], t[0], t[3], t[4], t[5], out_counter)
            tmp = e32.sendMessage(to_address, to_channel, out_message + '\r\n', useChecksum=False)
            print('OUT:>' + out_message + '<')

            time.sleep(0.1)
            gc.collect()
    
#         if (tmp := time.time()) >= ttt + BEFORE_DEEPSLEEP_TIME:
#             print('ESP32 is going to deep sleep')
# 
#             # put the device to sleep for DEEPSLEEP_TIME ms
#             machine.deepsleep(DEEPSLEEP_TIME)
        
        time.sleep(0.1)

except Exception as E:
    print(E)
    print(e32.reset())
    print(e32.stop())
