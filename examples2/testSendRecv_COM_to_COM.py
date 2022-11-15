import time
import serial

from at import *

PACKET_SIZE = 512 # 1 # 512 # 58
PERIOD_S = 25  # 15

IDLE = 0
SENDING = 1
RECEIVING = 2

state = IDLE

serdev1 = serial.Serial('COM17', baudrate=115200, timeout=0)  # UART_ANDROID_BAUD_RATE
#serdev1 = serial.Serial('COM17', baudrate=115200)  # UART_ANDROID_BAUD_RATE
print(serdev1)

Air_Rate = AIR_RATE['9.6k']

def to_at(at:str, value:int):
    if at in (Message_ID, Message_Length):
        return AT_PATTERN + at + chr(value & 0xFF) + chr((value >> 8) & 0xFF)
    else:
        return AT_PATTERN + at + chr(value & 0xFF)

def write_at(serdev, at:str, value:int):
    serdev.flush()
    serdev.timeout = None
    serdev.write(AT_PATTERN.encode())
    serdev.write(at.encode())
    #
    serdev.write(value & 0xFF)
    if at in (Message_ID, Message_Length):
        serdev.write((value >> 8) & 0xFF)
    #
    serdev.timeout = 0
    serdev.flush()

message_id = 1
t1 = time.time()
ts = time.time()
te = time.time() - PERIOD_S
MESSAGE_LEN = 0

err = 0
message_flow = b''

sended = 0
data_to_LoRa_state = data_bufer_empty
message_flow = b''
try:
    while True:
        t2 = time.time()
        #if False:
        if state != RECEIVING:
            #if t2 - te > te - ts + 5:
            if t2 - te > PERIOD_S:
            #if True:
                if data_to_LoRa_state < data_bufer_3_4:
                    if sended == 0:
                        mess = ''
                        #mess += '<BEGIN'
                        #mess += '>' + AT_PATTERN + AirRate + str(AirRate.to_bytes(2, 'little'))[2:-1] + '<'
                        #mess += '>' + AT_PATTERN + AirRate + str(AirRate & 0xFF) + str((AirRate >> 8) & 0xFF) + '<'
                        #mess += '>' + AT_PATTERN + AirRate + AirRate + '<'
                        #mess += '>' + AT_PATTERN + AirRate + '?' + '<'
                        mess += ' #%7d ' % (message_id)
                        mess += '- %7.3f ' % (te-ts)
                        mess += '- %7.3f ' % (t2-t1)
                        mess += '1234567890' * 150  # 150 # 45 # 46 # 240 #
                        mess += ' #%7d ' % (message_id)
                        #mess += '>' + AT_PATTERN + AirRate + '?' + '<'
                        #mess += 'END>'

                        message = ''
                        message += to_at(Message_ID, message_id)
                        message += AT_PATTERN + Message + 'B'
                        message += to_at(Message_Length, len(mess))
                        message += mess
                        message += AT_PATTERN + Message + 'E'

                        MESSAGE_LEN = len(message)

                        print('\nSending - len %d\n%s' % (MESSAGE_LEN, message))
                        message = message.encode('UTF-8')
                        #print('\nSending - len %d\n%s' % (MESSAGE_LEN, message))

                        ts = time.time()
                        state = SENDING

                    n = serdev1.write(message[sended:sended + PACKET_SIZE])
                    if n > 0:
                        sended += n
                        # print('Sended=', sended, 'n=', n)
                        if sended == MESSAGE_LEN:
                            te = time.time()
                            #if message_id < 5:
                            if True:
                                sended = 0
                                state = IDLE
                            print('Sended #', message_id)
                            message_id += 1
                            t1 = t2

                            # write_at(serdev1, AirRate, AirRate)

        msg = None
        msg = serdev1.read_all()
        if msg:
            message_flow += msg
            print('msg=', msg)
            print('message_flow=', message_flow)

            #at, at_value, message_flow = get_at(message_flow)
            #print('message_flow=', at, at_value, message_flow)

        if msg:
            if 0:
                #print(msg)
                print('msg=', msg)
                try:
                #    msg = str(msg, 'UTF-8')
                    pass
                except:
                #    msg = msg
                    pass
                #print(msg, end='')
                #print('' , len(msg), msg, end='')
                #print('\n' , len(msg), msg)
            else:
                begin = message_flow.find(b'<BEGIN')
                end = message_flow.rfind(b'END>')
                if begin >= 0:
                    state = RECEIVING
                if (begin >= 0) and (end > 0) and (begin < end):
                    message_in = message_flow[begin:end+4]
                    try:
                        message_in = str(message_in, 'UTF-8')
                    except:
                        message_in = message_in
                    if len(message_in) != MESSAGE_LEN:
                        err += 1
                    print()
                    print('Received - len %d - err %d'% (len(message_in), err), False if len(message_in) != MESSAGE_LEN else '')
                    print(message_in)
                    print('Received')
                    message_flow = message_flow[end+4+1:]
                    #print(len(message_flow), message_flow)
                    state = IDLE

        time.sleep(0.1)

finally:
    try:
        serdev1.close()
    except:
        pass
