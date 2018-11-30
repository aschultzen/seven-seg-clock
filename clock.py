import time
import RPi.GPIO as GPIO
from time import gmtime, strftime

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
TWO = SEG,_A + SEG_B + SEG_G + SEG_E + SEG_D
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

GPIO.setmode(GPIO.BOARD)
PIN_DATA  = 15
PIN_LATCH = 13
PIN_CLOCK = 11

GPIO.setup(PIN_DATA,  GPIO.OUT, initial=0)
GPIO.setup(PIN_LATCH, GPIO.OUT, initial=0)
GPIO.setup(PIN_CLOCK, GPIO.OUT, initial=0)

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
	time = strftime("%H%M%S", gmtime())
	return int(time)

if __name__ == '__main__':
	clockmode = CLOCK_MODE
	countdown = datetime.datetime(1981, 6, 16, 4, 0, 0)

	while(clockmode == CLOCK_MODE):
		drawinteger(gettime())
		time.sleep(0.5)

	while(clockmode == COUNTER_MODE):
		drawinteger(countdown)
