import time
import serial

from at import *

PACKET_SIZE =  1000000 # 1 # 512 # 58
PERIOD_S = 5

IDLE = 0
SENDING = 1
RECEIVING = 2

state = IDLE

serdev1 = serial.Serial('COM17', baudrate=115200, timeout=0) # UART_ANDROID_BAUD_RATE
#serdev1 = serial.Serial('COM17', baudrate=19200) # UART_ANDROID_BAUD_RATE
print(serdev1)

AirRate = AIR_RATE['4.8k']

def write_at(serdev, at:str, value:int):
    serdev.flush()
    serdev.timeout = None
    serdev.write((AT_PATTERN_CHAR).encode() * AT_CHAR_NUMBER)
    serdev.write(at.encode())
    serdev.write(value)
    serdev.timeout = 0
    serdev.flush()

teller = 1
t1 = time.time()
ts = time.time()
te = time.time() - PERIOD_S
MSG_LEN = 0

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
                        message = '>BEGIN    '
                        #message += AT_PATTERN_CHAR * AT_CHAR_NUMBER + begin_message + '    '
                        #message += '>' + AT_PATTERN_CHAR * AT_CHAR_NUMBER + '?_' + '< '
                        #message += '>' + AT_PATTERN_CHAR * AT_CHAR_NUMBER + SetAirRate + str(AirRate.to_bytes(2, 'little'))[2:-1] + '< '
                        #message += '>' + AT_PATTERN_CHAR * AT_CHAR_NUMBER + SetAirRate + str(AirRate & 0xFF) + str((AirRate >> 8) & 0xFF) + '< '
                        message += '>' + AT_PATTERN_CHAR * AT_CHAR_NUMBER + SetAirRate + AirRate + '< '
                        message += ' #%7d ' % (teller)
                        message += '- %7.3f ' % (te-ts)
                        message += '- %7.3f ' % (t2-t1)
                        message += '1234567890' * 150 # 45 # 46 # 240 #
                        message += ' %8d ' % (len(message) + 30)
                        message += ' #%7d ' % (teller)
                        message += '>' + AT_PATTERN_CHAR * AT_CHAR_NUMBER + GetAirRate + '?' + '< '
                        #message += AT_PATTERN_CHAR * AT_CHAR_NUMBER + end_message + '    '
                        message += '      END<'
                        message = message.encode('UTF-8')
                        MSG_LEN = len(message)

                        print('\nSending - len %d\n%s' % (len(message), message))
                        ts = time.time()
                        state = SENDING

                    n = serdev1.write(message[sended:sended + PACKET_SIZE])
                    if n > 0:
                        sended += n
                        print('Sended=', sended, 'n=', n)
                        if sended == len(message):
                            te = time.time()
                            #if teller < 5:
                            if True:
                                sended = 0
                                state = IDLE
                            print('Sended #', teller)
                            teller += 1
                            t1 = t2

                            # write_at(serdev1, SetAirRate, AirRate)

        msg = serdev1.read_all()
        if msg:
            print(msg)
            message_flow += msg
            # print('message_flow', message_flow)
        if len(message_flow) >= (AT_CHAR_NUMBER + 1 + 1):
            pattern = AT_PATTERN_CHAR.encode() * AT_CHAR_NUMBER
            at_pos = message_flow.find(pattern)
            if at_pos >= 0:
                if len(message_flow) >= (at_pos + AT_CHAR_NUMBER + 1 + 1):
                    at_pos += AT_CHAR_NUMBER
                    at_bin = message_flow[at_pos:at_pos + 1]
                    at_data_bin = message_flow[at_pos + 1:at_pos + 1 + 1]
                    at = str(at_bin, 'UTF-8')
                    try:
                        at_data = str(at_data_bin, 'UTF-8')
                    except:
                        at_data = at_data_bin
                    print('\n@@@@@ AT:', at, at_data, '|', at_bin, at_data_bin)
                    if at == data_to_LoRa_bufer:
                        data_to_LoRa_state = at_data
                        if at_data not in ('0', '1', '2', '3', '4', '5'):
                            print('message_flow', message_flow)
                    elif at == Android_uart_event:
                        if at_data not in ('0', '1', '2', '3', '4', '5', '6', '7'):
                            print('message_flow', message_flow)
                    else:
                        #print('message_flow', message_flow)
                        pass

                    #print('message_flow', message_flow)
                    message_flow = message_flow[at_pos + 1 + 1:]
                    #print('message_flow', message_flow)

        if msg:
            if 0:
                print(msg)
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
                begin = message_flow.find(b'>BEGIN')
                end = message_flow.rfind(b'END<')
                if begin >= 0:
                    state = RECEIVING
                if (begin >= 0) and (end > 0) and (begin < end):
                    message_in = message_flow[begin:end+4]
                    try:
                        message_in = str(message_in, 'UTF-8')
                    except:
                        message_in = message_in
                    if len(message_in) != MSG_LEN:
                        err += 1
                    print()
                    print('Received - len %d - err %d'% (len(message_in), err), False if len(message_in) != MSG_LEN else '')
                    print(message_in)
                    print('Received')
                    message_flow = message_flow[end+4+1:]
                    #print(len(message_flow), message_flow)
                    state = IDLE

        time.sleep(0.01)

finally:
    try:
        serdev1.close()
    except:
        pass
    try:
        serdev2.close()
    except:
        pass
