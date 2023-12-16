import alarm
import time
import board
import busio
import simpleio
import terminalio
import digitalio
import displayio
from analogio import AnalogIn
import adafruit_displayio_ssd1306
from simpleio import map_range
from adafruit_bitmap_font import bitmap_font
from adafruit_progressbar.verticalprogressbar import HorizontalProgressBar
from adafruit_display_text.label import Label
from digitalio import DigitalInOut, Direction, Pull

#### TODO
# safe steps and stats in memory when there were no steps in the last 5 mins (deep sleep)

print("Waking up")
pin_alarm = alarm.pin.PinAlarm(pin=board.GP15, value=False, pull=True)

# release displays
displayio.release_displays()

# Our reset button
btn = DigitalInOut(board.GP15)
btn.direction = Direction.INPUT
btn.pull = Pull.UP

# Display power
displayPWR = digitalio.DigitalInOut(board.GP11)
displayPWR.direction = digitalio.Direction.OUTPUT
displayPWR.value = True

# Battery Analog
analog_bat = AnalogIn(board.GP27)

# TDR Analog
tdrData = AnalogIn(board.GP28)

# TDR signal
tdrPower = digitalio.DigitalInOut(board.GP25)
tdrPower.direction = digitalio.Direction.OUTPUT
tdrPower.value = False

# Voltage Func
def get_voltage(pin):
    return ((pin.value * 3.3) / 65536)*2

# wait for display to wake up
time.sleep(5)

# Create the I2C interface for the oled
i2c2 = busio.I2C(scl=board.GP21, sda=board.GP20)

# Display bus
display_bus = displayio.I2CDisplay(i2c2, device_address=60)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)
display.brightness = 0.01

# Fonts
small_font = "fonts/Roboto-Medium-16.bdf"
#  glyphs for fonts
glyphs = b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-,.: '
#  loading bitmap fonts
small_font = bitmap_font.load_font(small_font)
small_font.load_glyphs(glyphs)

# Config
step_goal = 10000
countdown = 0 #  variable for the step goal progress bar
clock = 0 #  variable used to keep track of time for the steps per hour counter
clock_count = 0 #  holds the number of hours that the step counter has been running
clock_check = 0 #  holds the result of the clock divided by 3600 seconds (1 hour)
last_step = 0 #  state used to properly counter steps
mono = time.monotonic() #  time.monotonic() device
steps_log = 0 #  holds total steps to check for steps per hour
steps_remaining = 0 #  holds the remaining steps needed to reach the step goal
sph = 0 #  holds steps per hour
reset_pending = False
brightness_pending = True
brightness_mono = time.monotonic()

# Display content
splash = displayio.Group()
display.show(splash)

# Progress bar
prog_bar = HorizontalProgressBar((1, 1), (127, 10))
splash.append(prog_bar)

# Steps countdown
steps_countdown = Label(small_font, text='%d Left' % step_goal)
steps_countdown.x = 1
steps_countdown.y = 22

# Steps taken
text_steps = Label(small_font, text="0 Done    ")
text_steps.x = 1
text_steps.y = 40

# Steps per hour
text_sph = Label(small_font, text="0/H")
text_sph.x = 1
text_sph.y = 58

# Add to display
splash.append(text_sph)
splash.append(steps_countdown)
splash.append(text_steps)

start_time=time.monotonic()

tdrPower.value = True
tdrPower.value = False

while True:
    voltage = get_voltage(tdrData)
    if voltage > 1:
        print(voltage)



#while True:
#    voltage = get_voltage(analog_bat)
#    if (voltage <= 2.6):
#        prog_bar.progress = 100
#        steps_countdown.text = ''
#        text_sph.text = ''
#        text_steps.text = 'Battery LOW !!!'
#	time.sleep(2)
#        text_steps.text = 'Shutting DOWN !!!'
#	time.sleep(2)
#        display.sleep()
#	displayio.release_displays()
#	displayPWR.value = False
#	alarm.exit_and_deep_sleep_until_alarms(pin_alarm)
#    #print(voltage)
#	
#    #  setting up steps to hold step count
#    steps = 10
#
#    #  creating the data for the ProgressBar
#    countdown = map_range(steps, 0, step_goal, 0.0, 1.0)
#
#    #  actual counting of the steps
#    #  if a step is taken:
#    if abs(steps-last_step) > 1:
#        step_time = time.monotonic()
#        #  updates last_step
#        last_step = steps
#        #  updates the display
#        text_steps.text = '%d Done' % steps
#        clock = step_time - mono
#
#        #  logging steps per hour
#        if clock > 3600:
#            #  gets number of hours to add to total
#            clock_check = clock / 3600
#            #  logs the step count as of that hour
#            steps_log = steps
#            #  adds the hours to get a new hours total
#            clock_count += round(clock_check)
#            #  divides steps by hours to get steps per hour
#            sph = steps_log / clock_count
#            #  adds the sph to the display
#            text_sph.text = '%d/H' % sph
#            #  resets clock to count to the next hour again
#            clock = 0
#            mono = time.monotonic()
#
#        #  adjusting countdown to step goal
#        prog_bar.progress = float(countdown*100)
#
#    #  displaying countdown to step goal
#    if step_goal - steps > 0:
#        steps_remaining = step_goal - steps
#        steps_countdown.text = '%d Left' % steps_remaining
#    else:
#        steps_countdown.text = 'Nice Job!'
#
#    # reset
#    if btn.value is False and reset_pending:
#        if (int(time.monotonic() - reset_mono) > 5):
#            reset_pending = False
#        else:
#            reset_prog = int((((time.monotonic() - reset_mono))/5)*100)
#            if reset_prog > 100:
#                reset_prog = 100
#            prog_bar.progress = float(reset_prog)
#            text_steps.text = 'Keep pressing'
#            if reset_prog == 100:
#                countdown = 0 #  variable for the step goal progress bar
#                clock = 0 #  variable used to keep track of time for the steps per hour counter
#                clock_count = 0 #  holds the number of hours that the step counter has been running
#                clock_check = 0 #  holds the result of the clock divided by 3600 seconds (1 hour)
#                last_step = 0 #  state used to properly counter steps
#                mono = time.monotonic() #  time.monotonic() device
#                steps_log = 0 #  holds total steps to check for steps per hour
#                steps_remaining = 0 #  holds the remaining steps needed to reach the step goal
#                sph = 0 #  holds steps per hour
#                text_steps.text = 'Reset Release'
#                sensor.pedometer_enable = False
#                sensor.pedometer_enable = True
#                prog_bar.progress = float(0)
#                reset_pending = False
#                while btn.value is False:
#                    time.sleep(0.001)
#    else:
#        reset_pending = False
#        text_steps.text = '%d Done' % steps
#        prog_bar.progress = float(countdown*100)
#    if btn.value is False and reset_pending is False:
#        #display.wake()
#        if brightness_pending is False:
#	   display.brightness = 1
#        brightness_pending = True
#        reset_mono = time.monotonic()
#        brightness_mono = time.monotonic()
#        a_state = False
#        reset_pending = True
#    if brightness_pending is True and (int(time.monotonic() - brightness_mono) > 5):
#        display.brightness = 0.01
#    if brightness_pending is True and (int(time.monotonic() - brightness_mono) > 10):
#        display.sleep()
#	displayio.release_displays()
#	displayPWR.value = False
#	print("going to light sleep")
#	time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 150)
#	alarm.light_sleep_until_alarms(time_alarm, pin_alarm)
#	print("out of light sleep")
#        btn = DigitalInOut(board.GP15)
#        btn.direction = Direction.INPUT
#        btn.pull = Pull.UP       
#	steps = sensor.pedometer_steps
#	time.sleep(0.5)
#	print(btn.value)
#	if (btn.value is False and steps == 0):
#		print("going to deep sleep")
#		time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 300)
#		alarm.exit_and_deep_sleep_until_alarms(time_alarm, pin_alarm)
#        brightness_pending = True
#        brightness_mono = time.monotonic()
#	displayPWR.value = True
#	time.sleep(1)
#	display_bus = displayio.I2CDisplay(i2c2, device_address=60)
#	display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)
#	display.brightness = 1
#	display.show(splash)
#        #btn = DigitalInOut(board.GP15)
#        #btn.direction = Direction.INPUT
#        #btn.pull = Pull.UP       
#
#    time.sleep(0.001)
#