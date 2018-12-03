import time
import RPi.GPIO as GPIO
import datetime
from time import localtime, strftime

#  A
# F B
#  G
# E C
#  D DP
#
# The lines over are supposed to be
# a "drawing" of the segments and
# their respective positions.

# Modes
CLOCK_MODE = 1
COUNTER_MODE = 2
TIMER_MODE = 3

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
counter_start = 0
counter_end = 0

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

def setmode():
    print("setmode")

def addhour():
	print("addhour")

def addmin():
	print("addmin")

def addsec():
	print("addsec")

def startstop():
	print("startstop")

def clearclock():
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
	func = switcher.get(channel, lambda: "Invalid month")
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
	panel = clearpanel
	intlist = list(str(integer))
	intlist = intlist[::-1]
	for x in range(0,len(intlist)):
		panel[x] = numbers[int(intlist[x])]

	GPIO.output(PIN_LATCH, 0)
	for x in range(0,len(panel)):
		shiftout(panel[x])

	GPIO.output(PIN_LATCH, 1)

def gettime():
	time = strftime("%H%M%S", localtime())
	return int(time)

def formattime(time):
	return int(strftime("%H%M%S", time))

if __name__ == '__main__':
	clockmode = CLOCK_MODE

	while(clockmode == CLOCK_MODE):
		drawinteger(gettime())
		time.sleep(0.5)

	#while(clockmode == COUNTER_MODE):
		#drawinteger()
