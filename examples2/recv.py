import serial
import time

serdev = serial.Serial('COM4', baudrate=115200, timeout=None, write_timeout=None)

e32.start()
#e32.setConfig('setConfigPwrDwnSave')
e32.getVersion()
e32.getConfig()

print()


while True:
    #message = serdev.read()
    #message = serdev.read_all()
    message = serdev.read(serdev.in_waiting)
    if message:
        message = message.decode('ascii')
        
#         print('Receiving transparent : address %d - channel %d'%(from_address, from_channel), end='')
#         print(' - message %s'%(message))
#        print('' , len(message), message, end='')
        print(message, end='')
        #print(message)
        #time.sleep(2.000)

