import time
import RPi.GPIO as GPIO
import datetime
import signal
import sys
from time import localtime, strftime
from threading import Thread


#  A
# F B
#  G
# E C
#  D DP
#
# The lines over are supposed to be
# a "drawing" of the segments and
# their respective positions.

# Keep going?
forever = True

# Modes
CLOCK_MODE = 0
COUNTER_MODE = 1
TIMER_MODE = 2
NUM_STATES = 3
current_clock_state = 0

# Segments HEX codes
SEG_DP = 0x1
SEG_B = 0x2
SEG_C = 0x4
SEG_D = 0x8
SEG_E = 0x10
SEG_F = 0x40
SEG_G = 0x20
SEG_A = 0x80

# Number HEX codes
ZERO = SEG_A + SEG_B + SEG_C + SEG_D + SEG_E + SEG_F
ONE = SEG_B + SEG_C
TWO = SEG_A + SEG_B + SEG_G + SEG_E + SEG_D
THREE = SEG_A + SEG_B + SEG_G + SEG_C + SEG_D
FOUR = SEG_F + SEG_B + SEG_G + SEG_C
FIVE = SEG_A + SEG_F + SEG_G + SEG_C + SEG_D
SIX = SEG_A + SEG_G + SEG_C + SEG_D + SEG_E + SEG_F
SEVEN = ONE + SEG_A
EIGHT = ZERO + SEG_G
NINE = EIGHT - SEG_E  - SEG_D

# Letters
A = EIGHT - SEG_D
B = EIGHT - SEG_B - SEG_A
C = ZERO - SEG_B - SEG_C - SEG_G
D = EIGHT - SEG_F - SEG_A
E = EIGHT - SEG_B + SEG_C
F = EIGHT - SEG_D - SEG_C - SEG_B

numbers = [ZERO, ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE]
letters = [A, B, C, D, E, F]
clearpanel = [0x0, 0x0, 0x0, 0x0, 0x0, 0x0]
zeropanel = [ZERO, ZERO, ZERO, ZERO, ZERO, ZERO]
previous_integer = 0

# Button pins
WHITE_BUTTON_PIN = 3
GREEN_BUTTON_PIN = 5
PURPLE_BUTTON_PIN = 7
ORANGE_BUTTON_PIN = 16
ORANGE2_BUTTON_PIN = 18
GREY_BUTTON_PIN = 22

# Action pins
MODE_ACTION = ORANGE2_BUTTON_PIN
HOUR_ADD_ACTION = GREEN_BUTTON_PIN
MIN_ADD_ACTION = WHITE_BUTTON_PIN
SEC_ADD_ACTION = GREY_BUTTON_PIN
STARTSTOP_ACTION = ORANGE_BUTTON_PIN
CLEAR_ACTION = PURPLE_BUTTON_PIN

# Counter variables
counter_status = 0
counter_start = 0
counter_stop = 0
counter_seconds = 0
counter_minutes = 0
counter_hours = 0
counter_offsett = datetime.datetime(2018, 01, 01, 0, 0, 00)
counter_remaining = 0
# Setting GPIO mode
GPIO.setmode(GPIO.BOARD)

# Setting up the push-buttons
GPIO.setup(WHITE_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GREEN_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PURPLE_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ORANGE_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ORANGE2_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GREY_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Shift register pins
PIN_DATA  = 15
PIN_LATCH = 13
PIN_CLOCK = 11

# Shift register pins setup
GPIO.setup(PIN_DATA,  GPIO.OUT, initial=0)
GPIO.setup(PIN_LATCH, GPIO.OUT, initial=0)
GPIO.setup(PIN_CLOCK, GPIO.OUT, initial=0)

def signal_handler(sig, frame):
	global forever
	print("SIGINT received, exiting...")
	forever = False

signal.signal(signal.SIGINT, signal_handler)

def setmode():
	global current_clock_state
	current_clock_state = current_clock_state + 1
	current_clock_state = current_clock_state % NUM_STATES

def addhour():
	global counter_offsett
	counter_offsett = counter_offsett + datetime.timedelta(hours=1)
	print("addhour")

def addmin():
	global counter_offsett
	counter_offsett = counter_offsett + datetime.timedelta(minutes=1)
	print("addmin")

def addsec():
	global counter_offsett
	counter_offsett = counter_offsett + datetime.timedelta(seconds=1)
	print("addsec")

def startstop():
	global current_clock_state
	global counter_status
	if(current_clock_state == COUNTER_MODE):
		if(counter_status == 0):
			print("Starting counter")
			counter_status = 1
		else:
			print("Stop counter")
			counter_status = 0

def clearclock():
	global counter_offsett
	counter_offsett = datetime.datetime(2018, 01, 01, 0, 0, 00)
	print("clearclock")

def button_callback(channel):
	switcher = {
		MODE_ACTION: setmode,
		HOUR_ADD_ACTION: addhour,
		MIN_ADD_ACTION: addmin,
		SEC_ADD_ACTION: addsec,
		STARTSTOP_ACTION: startstop,
		CLEAR_ACTION: clearclock
	}
	func = switcher.get(channel, lambda: "Invalid value")
	func()

# Setup events for buttons
GPIO.add_event_detect(WHITE_BUTTON_PIN,GPIO.FALLING,callback=button_callback, bouncetime=200)
GPIO.add_event_detect(GREEN_BUTTON_PIN,GPIO.FALLING,callback=button_callback, bouncetime=200)
GPIO.add_event_detect(PURPLE_BUTTON_PIN,GPIO.FALLING,callback=button_callback, bouncetime=200)
GPIO.add_event_detect(ORANGE_BUTTON_PIN,GPIO.FALLING,callback=button_callback, bouncetime=200)
GPIO.add_event_detect(ORANGE2_BUTTON_PIN,GPIO.FALLING,callback=button_callback, bouncetime=200)
GPIO.add_event_detect(GREY_BUTTON_PIN,GPIO.FALLING,callback=button_callback, bouncetime=200)

def shiftout(byte):
	for x in range(8):
		GPIO.output(PIN_CLOCK, 0)
		GPIO.output(PIN_DATA, (byte >> x) & 1)
		GPIO.output(PIN_CLOCK, 1)

def drawinteger(integer):
	global previous_integer
	if integer != previous_integer:
		panel = [ZERO, ZERO, ZERO, ZERO, ZERO, ZERO]
		intlist = list(str(integer))
		intlist = intlist[::-1]
		for x in range(0,len(intlist)):
			panel[x] = numbers[int(intlist[x])]

		GPIO.output(PIN_LATCH, 0)
		for x in range(0,len(panel)):
			shiftout(panel[x])

		GPIO.output(PIN_LATCH, 1)
	previous_integer = integer

def gettime():
	time = strftime("%H%M%S", localtime())
	return int(time)

def formattime(sometime):
	#print(int(sometime.strftime("%H%M%S")))
	return (int(sometime.strftime("%H%M%S")))

def clocktick():
	global counter_offsett
	correction = 0
	reference = time.time()
	while(forever):
		start = time.time()
		correction = ((time.time() - reference) % 1)
		if(counter_status == 1):
			print("counter_status is now 1")
			counter_offsett = counter_offsett - datetime.timedelta(seconds=1)
		time.sleep(1 - (time.time() - start) - correction)

if __name__ == '__main__':
	thread = Thread(target = clocktick, args = ())
	thread.start()

	while(forever):
		while(current_clock_state == CLOCK_MODE and forever):
			drawinteger(gettime())
			time.sleep(0.5)

		while(current_clock_state == COUNTER_MODE and forever):
			#print("Counter mode!")
			drawinteger(formattime(counter_offsett))
			time.sleep(0.1)

		while(current_clock_state == TIMER_MODE and forever):
			print("Timer mode!")
			drawinteger(1)
			time.sleep(0.5)

	print("Thread killed, done.")
