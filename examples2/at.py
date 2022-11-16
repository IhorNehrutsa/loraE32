AT_PATTERN = "@@@@@" # шаблон
AT_PATTERN_LEN = len(AT_PATTERN) # довжина шаблону
AT_COMMAND_LEN = 1
AT_VALUE_LEN = 5 # довжина значення команди може бути 1, 2 або 5
AT_MAX_SIZE = AT_PATTERN_LEN + AT_COMMAND_LEN + AT_VALUE_LEN

Tangenta1 = 'T'  # next byte is '0'-unpressed, '1'-pressed

data_to_LoRa_bufer = 'B'  # next byte is (data_bufer_XXXX)
data_to_Android_bufer = 'b'  # next byte is (data_bufer_XXXX)
# @@@@@b1 // means that the data_to_LoRa_bufer stores less than 1/4 of the full length
# @@@@@b3 // means that the data_to_LoRa_bufer stores MORE than 3/4 of the full length
data_bufer_empty = '0'
data_bufer_0_4 = '0'
data_bufer_1_4 = '1'
data_bufer_2_4 = '2'
data_bufer_3_4 = '3'
data_bufer_4_4 = '4'
data_bufer_full = '4'
data_bufer_lose = '5'

ESP_ID = 'I'  # next byte is unique number which is factory-programmed by Espressif
Get_ESP_ID = 'i'

Message_ID_Length = 'M'

Message_Begin_End = 'S'

Message_Data = 'D'

AIR_RATE = { '0.3k':'0', '1.2k':'1', '2.4k':'2', '4.8k':'3', '9.6k':'4', '19.2k':'5' }
AirRate = 'A'

Power = 'P'

Mode = 'O'

LoRa_uart_event = 'E'  # next byte is (event.type+'0')
Android_uart_event = 'e'  # next byte is (event.type+'0')
#
# from C:\Users\<user>\.platformio\packages\framework-espidf\components\driver\include\driver\uart.h
UART_DATA = '0'              # UART data event
UART_BREAK = '1'             # UART break event
UART_BUFFER_FULL = '2'       # UART RX buffer full event
UART_FIFO_OVF = '3'          # UART FIFO overflow event
UART_FRAME_ERR = '4'         # UART RX frame error event)
UART_PARITY_ERR = '5'        # UART RX parity event
UART_DATA_BREAK = '6'        # UART TX data and break event
UART_PATTERN_DET = '7'       # UART pattern detected

Reset = 'R'

Internal_Error = 'Z'

def AT_VALUE_SIZE(at_cmd):
    if at_cmd == Message_Data:
        return 5
    elif at_cmd == Message_ID_Length:
        return 4
    else:
        return 1

def IS_AT_TO_RESIEVER(at_cmd):
    return (at_cmd == Message_Data) or (at_cmd == Message_ID_Length) or (at_cmd == Message_Begin_End)

class esp:
    ID = 0
    Message_ID = 0
    Message_Length = 0
    Message_Ofset = 0

def get_at(message):
    at = None
    at_value = None
    if len(message) >= (AT_PATTERN_LEN + 1):
        at_pos = message.find(AT_PATTERN.encode())
        if at_pos >= 0:
            if len(message) >= (at_pos + AT_PATTERN_LEN + 1):
                at_pos += AT_PATTERN_LEN
                at_bin = message[at_pos:at_pos + 1]
                # at = str(at_bin)
                at = at_bin.decode()
                at_size = AT_VALUE_SIZE(at)
                print("at_size=", at_size, at_pos, message)
                if len(message) >= (at_pos + at_size):
                    at_value_bin = message[at_pos + 1:at_pos + 1 + at_size]

                    if at == ESP_ID:
                        at_value = at_value_bin.to_int()
                    elif at == Message_ID_Length:
                        at_value_bin = message[at_pos + 1:at_pos + 1 + 2]
                        esp.Message_ID = at_value_bin.decode()

                        at_value_bin = message[at_pos + 1 + 2:at_pos + 1 + 2 + 2]
                        esp.Message_Length = at_value_bin.decode()

                    elif at == Message_Data:
                        at_value_bin = message[at_pos + 1:at_pos + 1 + 2]
                        esp.Message_ID = at_value_bin.decode()

                        at_value_bin = message[at_pos + 1 + 2:at_pos + 1 + 2 + 2]
                        esp.Message_Ofset = at_value_bin.decode()

                    else:
                        at_value = at_value_bin.decode()

                    print('\n@@@@@ AT:', at, at_value)  # , '|', at_bin, at_value_bin)
                    if at == data_to_LoRa_bufer:
                        data_to_LoRa_state = at_value
                        if at_value not in ('0', '1', '2', '3', '4', '5'):
                            print('message', message)
                    elif at == Android_uart_event:
                        if at_value not in ('0', '1', '2', '3', '4', '5', '6', '7'):
                            print('message', message)
                    else:
                        #print('message', message)
                        pass

                    #print('message', message)
                    message = message[at_pos + 1 + at_size:]
                    #print('message', message)
    return at, at_value, message

def str_to_bytes(message):
    # b = []
    # for x in message:
    #     b.append(ord(x))  # ascii code of character

    # b = [None] * len(message)
    # for i in range(len(message)):
    #     b[i] = ord(message[i])  # ascii code of character
    # return b

    return [ord(x) for x in message]

def bytes_to_str(message):
    msg = ''
    for i in range(len(message)):
        msg += chr(message[i])
    return msg