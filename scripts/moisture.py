from machine import Pin, ADC
from time import sleep_ms


vcc = Pin(16, Pin.OUT)
adc = ADC(Pin(26))


DELAY = int(1e3)
V_IN = 3.3
DUTY_TO_V = V_IN / (2**16 - 1)


while True:
    vcc.on()
    sleep_ms(DELAY)
    duty = adc.read_u16()
    vcc.off()

    v = duty*DUTY_TO_V

    print(v)

    sleep_ms(int(60e3))

