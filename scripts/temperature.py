import math
from machine import ADC, Pin
from utime import sleep_ms


DELAY = 1000

V_IN = 3.3
DUTY_TO_V = V_IN / (2**16 - 1)

# https://www.farnell.com/datasheets/2131310.pdf
T1, T2, T3 = 248.15, 273.15, 298.15
R1, R2, R3 = 1000, 200, 80


def steinhart_hart(t1, t2, t3, r1, r2, r3):
    l1, l2, l3 = math.log(r1), math.log(r2), math.log(r3)
    y1, y2, y3 = 1/t1, 1/t2, 1/t3
    
    gamma_2 = (y2 - y1)/(l2 - l1)
    gamma_3 = (y3 - y1)/(l3 - l1)

    c = ((gamma_3 - gamma_2)/(l3 - l2))*(1/(l1 + l2 + l3))
    b = gamma_2 - c*(l1**2 + l1*l2 + l2**2)
    a = y1 - (b + c*l1**2)*l1

    return a, b, c


def temperature(adc, a, b, c, r_div):
    duty = adc.read_u16()
    v_in = V_IN
    v_out = duty*DUTY_TO_V
    r_therm = r_div*(v_in/v_out - 1)

    # steinhart-hart
    temp = 1 / (a + b*math.log(r_therm) + c*math.log(r_therm)**3)

    return temp


a, b, c = steinhart_hart(T1, T2, T3, R1, R2, R3)
adc = ADC(Pin(26))

while True:
    print(temperature(adc, a, b, c, int(1e3)))
    sleep_ms(1000)




