import serial
from LoRaE32 import ebyteE32

class ebyteE32_win(ebyteE32):
    ''' class to interface an ESP32 via serial commands to the EBYTE E32 Series LoRa modules '''
    

    def __init__(self, Model='433T30D', Port='COM1', Baudrate=9600, Parity='8N1', AirDataRate='2.4k', Address=0x0000, Channel=0x17, debug=False):
        ''' constructor for ebyte E32 LoRa module '''
        super().__init__(Model, Port, Baudrate, Parity, AirDataRate, Address, Channel, debug)
        

    def start(self):
        ''' Start the ebyte E32 LoRa module '''
        super().start()
        
        # make UART instance
        self.serdev = serial.Serial(self.config['port'], baudrate=self.config['baudrate'])
        if not self.serdev.isOpen():
            self.serdev.open()
        
        if self.debug:
            print('self.serdev', self.serdev)
        # set config to the ebyte E32 LoRa module
        # self.setConfig('setConfigPwrDwnSave')
        return 'OK start'
        
    
    def setM0(self, value):
        self.serdev.rts = (value == 0)
    
    
    def setM1(self, value):
        self.serdev.dtr = (value == 0)
    
    
    def getAUX(self):
        #print('AUX', not self.serdev.dsr)
        return not self.serdev.dsr
        #return not self.serdev.ri
    
    
    def is_any(self):
        return self.serdev.in_waiting


    def read(self)->bytes:
        return self.serdev.read_all() # serdev.read_all() is serdev.read(serdev.in_waiting)
        

    def flush(self):
        self.serdev.flush()
