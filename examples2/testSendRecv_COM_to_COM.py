import time
import serial

from at import *

PACKET_SIZE =  1000000 # 1 # 512 # 58
PERIOD_S = 25

IDLE = 0
SENDING = 1
RECEIVING = 2

state = IDLE

serdev1 = serial.Serial('COM17', baudrate=115200, timeout=0) # UART_ANDROID_BAUD_RATE
#serdev1 = serial.Serial('COM17', baudrate=19200) # UART_ANDROID_BAUD_RATE
print(serdev1)

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
                        #message += str(AT_PATTERN_CHAR * AT_CHAR_NUMBER) + begin_message + '    '
                        #message += '>' + str(AT_PATTERN_CHAR * AT_CHAR_NUMBER, 'ascii') + '?_' + '< '
                        message += ' #%7d ' % (teller)
                        message += '- %7.3f ' % (te-ts)
                        message += '- %7.3f ' % (t2-t1)
                        message += '1234567890' * 150 # 45 # 46 # 240 #
                        message += ' %8d ' % (len(message) + 30)
                        message += ' #%7d ' % (teller)
                        #message += str(AT_PATTERN_CHAR * AT_CHAR_NUMBER) + end_message + '    '
                        message += '      END<'
                        message = message.encode('UTF-8')
                        MSG_LEN = len(message) - 2

                        print('\nSending - len %d\n%s\n' % (len(message), message), end='')
                        #print('\nSending - len %d\n' % (len(message)), end='')
                        ts = time.time()
                        state = SENDING

                    n = serdev1.write(message[sended:sended + PACKET_SIZE])
                    if n > 0:
                        sended += n
                        print('sended, n', sended, n)
                        if sended == len(message):
                            te = time.time()
                            #if teller < 5:
                            if True:
                                sended = 0
                                state = IDLE
                            print('\nSended #', teller)
                            teller += 1
                            t1 = t2

        msg = serdev1.read_all()
        if msg:
            message_flow += msg
            # print('message_flow', message_flow)
        if len(message_flow) >= (AT_CHAR_NUMBER + 1 + 1):
            at_pos = message_flow.find(AT_PATTERN_CHAR * AT_CHAR_NUMBER)
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
                    if at == data_to_LoRa_bufer:
                        data_to_LoRa_state = at_data
                        print('serdev1.read AT:', at, at_data, '|', at_bin, at_data_bin)
                        if at_data not in ('0', '1', '2', '3', '4', '5'):
                            print('in message', message_flow)
                    elif at == Android_uart_event:
                        print('serdev1.read EV:', at, at_data, '|', at_bin, at_data_bin)
                        if at_data not in ('0', '1', '2', '3', '4', '5', '6', '7'):
                            print('in message', message_flow)
                    else:
                        print('serdev1.read __:', at, at_data, '|', at_bin, at_data_bin)
                        #print('in message', message_flow)

                    #print('in message', message_flow)
                    message_flow = message_flow[at_pos + 1 + 1:]
                    #print('in message', message_flow)

        if msg:
            if 1:
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
                    message = message_flow[begin:end+4]
                    try:
                        message = str(message, 'UTF-8')
                    except:
                        message = message
                    if len(message) != MSG_LEN:
                        err += 1
                    print()
                    print('Received - len %d - err %d'% (len(message), err), False if len(message) != MSG_LEN else '')
                    print(message)
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
