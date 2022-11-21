import time
import serial

from at import *

PACKET_SIZE = 512 # 1 # 512 # 58
PERIOD_S = 5 # 10  # 15

IDLE = 0
SENDING = 1
RECEIVING = 2

state = IDLE

serdev = serial.Serial('COM17', baudrate=115200, timeout=0)  # UART_ANDROID_BAUD_RATE
#serdev = serial.Serial('COM17', baudrate=115200)  # UART_ANDROID_BAUD_RATE
print(serdev)

Air_Rate = AIR_RATE['9.6k']

def to_at(at:str, value:int):
    if at == Message_ID_Length:
        s = AT_PATTERN + at + chr(esp.Message_ID & 0xFF) + chr((esp.Message_ID >> 8) & 0xFF) + chr(esp.Message_Length & 0xFF) + chr((esp.Message_Length >> 8) & 0xFF)
        print(len(s), s)
        return s
    else:
        s = AT_PATTERN + at + chr(value & 0xFF)
        print(len(s), s)
        return s

def write_at(at:str, value:int):
    #print('write_at()', at, value, serdev.out_waiting)
    serdev.timeout = None
    serdev.flush()
    serdev.write(AT_PATTERN.encode())
    serdev.write(at.encode())
    if at == Message_ID_Length:
        b = bytes([esp.Message_ID & 0xFF, (esp.Message_ID >> 8) & 0xFF, esp.Message_Length & 0xFF, (esp.Message_Length >> 8) & 0xFF])
    else:
        b = bytes([value & 0xFF])
    #print('b=', b)
    serdev.write(b)
    serdev.flush()
    serdev.timeout = 0

# write_at(Get_ESP_ID, ord('?'))
# write_at(ESP_ID, 0)
# write_at(Get_ESP_ID, ord('?'))

esp.Message_ID = 1
t1 = time.time()
t_send_begin = time.time()
t_send_end = time.time() - PERIOD_S
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
            #if t2 - t_send_end > t_send_end - t_send_begin + 5:
            if t2 - t_send_end > PERIOD_S:
            #if True:
                if data_to_LoRa_state < data_bufer_3_4:
                    if sended == 0:
                        mess = ''
                        mess += '<<<       '
                        #mess += '<BEGIN'
                        #mess += '>' + AT_PATTERN + Lora_AirRate + str(Lora_AirRate.to_bytes(2, 'little'))[2:-1] + '<'
                        #mess += '>' + AT_PATTERN + Lora_AirRate + str(Lora_AirRate & 0xFF) + str((Lora_AirRate >> 8) & 0xFF) + '<'
                        #mess += '>' + AT_PATTERN + Lora_AirRate + Lora_AirRate + '<'
                        #mess += '>' + AT_PATTERN + Lora_AirRate + '?' + '<'
                        mess += ' #%7d ' % (esp.Message_ID)
                        mess += '- %7.3f ' % (t_send_end - t_send_begin)
                        mess += '- %7.3f ' % (t2 - t1)
                        mess += '1234567890' * 1250  # 150 # 45 # 46 # 240 #
                        mess += ' #%7d ' % (esp.Message_ID)
                        #mess += '>' + AT_PATTERN + Lora_AirRate + '?' + '<'
                        #mess += 'END>'
                        mess += '       >>>'

                        esp.Message_Length=len(mess)
                        message = ''
                        # message += to_at(ESP_ID, 0)
                        # message += to_at(Get_ESP_ID, ord('?'))

                        # message += AT_PATTERN + Message_Begin_End + 'B'
                        # message += to_at(Message_ID_Length, None)
                        message += mess
                        # message += AT_PATTERN + Message_Begin_End + 'E'

                        message_ = str_to_bytes(message)

                        MESSAGE_LEN = len(message_)
                        print('\nSending #%d %d %d\n%s' % (esp.Message_ID, MESSAGE_LEN, len(mess), message))
                        #print('\nSending #%d %d %d\n%s' % (esp.Message_ID, MESSAGE_LEN, len(mess), message_))

                        t_send_begin = time.time()
                        state = SENDING

                    n = serdev.write(message_[sended:sended + PACKET_SIZE])
                    if n > 0:
                        sended += n
                        # print('Sended=', sended, 'n=', n)
                        if sended >= MESSAGE_LEN:
                            #serdev.flush()
                            print('Sended #%d %d' % (esp.Message_ID, sended))
                            t_send_end = time.time()
                            #if esp.Message_ID < 10:
                            if True:
                                sended -= MESSAGE_LEN
                                state = IDLE
                            esp.Message_ID += 1
                            t1 = t2

                            # write_at(Lora_AirRate, Lora_AirRate)

        msg = None
        if serdev.in_waiting:
            msg = serdev.read_all()

        if msg:
            message_flow += msg
        #     print('msg=', msg)
        #     print('message_flow=', message_flow)

            at, at_value, message_flow = get_at(message_flow)
            if at:
                # print('at, at_value, message_flow=', at, at_value, message_flow)
                print('at, at_value', at, at_value)
                if at == data_to_LoRa_bufer:
                    data_to_LoRa_state = at_value

        if msg:
            if 0:
                #print(msg)
                msg = bytes_to_str(msg)
                print('msg=', msg)
                #print(msg, end='')
                #print('' , len(msg), msg, end='')
                #print('\n' , len(msg), msg)
            else:
                begin = message_flow.find(b'<<<')
                end = message_flow.rfind(b'>>>')
                # begin = message_flow.find((AT_PATTERN + "SB").encode())
                # end = message_flow.rfind((AT_PATTERN + "SE").encode())
                if begin >= 0:
                    state = RECEIVING
                if (begin >= 0) and (end > 0) and (begin < end):
                    message_in = message_flow[begin:end+4]

                    message_in = bytes_to_str(message_in)

                    print()
                    if len(message_in) != MESSAGE_LEN:
                        print('len(message_in) != MESSAGE_LEN', len(message_in), MESSAGE_LEN)
                        err += 1
                    print('Received %d - err %d'% (len(message_in), err))
                    print(message_in)
                    print('Received %d - err %d'% (len(message_in), err))
                    message_flow = message_flow[end+4+1:]
                    #print(len(message_flow), message_flow)
                    state = IDLE

        time.sleep(0.1)

finally:
    try:
        serdev.reset_output_buffer()
        serdev.close()
        print('serdev.close()')
    except:
        pass
