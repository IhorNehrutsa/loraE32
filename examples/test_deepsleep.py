print('test_deepsleep.py')
# Complete project details at https://RandomNerdTutorials.com

from machine import deepsleep, reset_cause, DEEPSLEEP_RESET
from machine import Pin
from time import sleep
from esp32 import wake_on_ext0, WAKEUP_ALL_LOW, WAKEUP_ANY_HIGH

AUXpin = 4

wake1 = Pin(AUXpin, Pin.IN, Pin.PULL_UP)

#level parameter can be: esp32.WAKEUP_ANY_HIGH or esp32.WAKEUP_ALL_LOW
wake_on_ext0(pin = wake1, level = WAKEUP_ALL_LOW)

print(reset_cause())
# check if the device woke from a deep sleep
if reset_cause() == DEEPSLEEP_RESET:
    print('woke from a deep sleep')

# led = Pin (2, Pin.OUT)
# 
# #blink LED
# led.value(1)
# sleep(1)
# led.value(0)
# sleep(1)

# wait 5 seconds so that you can catch the ESP awake to establish a serial communication later
# you should remove this sleep line in your final script
sleep(5)

print('Im awake, but Im going to sleep')

#sleep for 10 seconds (10000 milliseconds)
deepsleep(100_000) # 10_000
