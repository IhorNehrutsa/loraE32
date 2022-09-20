###########################################
# sending transparent
###########################################
# transmitter - address 0001 - channel 02
# message     - address 0001 - channel 02
# receiver(s) - address 0001 - channel 02
###########################################

from LoRaE32_win import ebyteE32_win as ebyteE32
import time

e32 = ebyteE32(Port='COM4', Address=0x0001, Channel=0x02, debug=False)

e32.start()
e32.setConfig('setConfigPwrDwnNoSave')
e32.getVersion()
e32.getConfig()

to_address = 0x0001
to_channel = 0x02

teller = 0
t1 = time.time()
while True:
    # print(e32.getAUX())
    if e32.getAUX():
        t2 = time.time()
        #message = { 'msg': 'HELLO WORLD %s - %s - %f\n'%(str(teller), time.ctime(), t2-t1) }
        message = 'HELLO WORLD %s - %s - %f\n'%(str(teller), time.ctime(), t2-t1) 
        print('Sending transparent : address %s - channel %d - message %s'%(to_address, to_channel, message), end='')
        e32.sendMessage(to_address, to_channel, message, useChecksum=False)
        teller += 1
        #time.sleep(2.000)
        t1 = t2
    
e32.stop()