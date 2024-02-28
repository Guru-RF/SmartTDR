import time
import board
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction
#, Pull


# TDR Analog
tdrData = AnalogIn(board.GP28)

# TDR signal
tdrPower = DigitalInOut(board.GP25)
tdrPower.direction = Direction.OUTPUT
tdrPower.value = False

# Voltage Func
def get_voltage(pin):
    return ((pin.value * 3.3) / 65536)*2

tdrPower.value = True


#t_end = time.time() + 1 
#while time.time() < t_end:
#    print(tdrData.value)
#    tdrPower.value = False
SAMPLES = 256

while True:
    start = time.monotonic()
    for _ in range(SAMPLES):
        adc_val = tdrData.value
    duration_secs = time.monotonic() - start
    sample_secs = duration_secs / SAMPLES
    rate = 1/sample_secs
    print('Time per sample: {}ms rate:{} Total time: {}ms'.format(sample_secs*1000, rate, duration_secs*1000))
