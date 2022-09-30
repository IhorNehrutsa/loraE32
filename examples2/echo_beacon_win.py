print('echo_beacon_win.py')

import time, gc

from LoRaE32_win import ebyteE32_win as ebyteE32


BEACON_TIME = 5 # 15 seconds
DEEPSLEEP_TIME = 60_000 # 60 seconds
BEFORE_DEEPSLEEP_TIME = 15 # 60 seconds

from_address = 10 # 0xFFFF # 0x0000
from_channel = 0x17

to_address = 10 # 0xFFFF # 0x0000
to_channel = 0x17

in_message = None

in_counter = 0
out_counter = 0

tt = 0  # time.time() - BEACON_TIME
ttt = time.time()

try:
    e32 = ebyteE32(Port='COM3', debug=True)
    print(e32.start())
    print(e32.getVersion())
    print(e32.getConfig())
    
    while True:
        in_message = None
        if e32.in_waiting():
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
finally:    
    print(e32.reset())
    print(e32.stop())
