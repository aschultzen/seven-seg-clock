
#!/usr/bin/env python

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
segmentClock=11
segmentLatch=13
segmentData=15

GPIO.setup(segmentClock,GPIO.OUT)
GPIO.setup(segmentData,GPIO.OUT)
GPIO.setup(segmentLatch,GPIO.OUT)

GPIO.output(segmentClock,GPIO.LOW)
GPIO.output(segmentData,GPIO.LOW)
GPIO.output(segmentLatch,GPIO.LOW)

number=0

def showNumber(value):
    number = abs(value) #Remove negative signs and any decimals
    x=0
    while(x<2):
        remainder=number % 10
        postNumber(remainder, False)
        number = number/10
        x += 1

    #Latch the current segment data
    GPIO.output(segmentLatch,GPIO.LOW)
    GPIO.output(segmentLatch,GPIO.HIGH) #Register moves storage register on the rising edge of RCK

#Given a number, or - shifts it out to the display
def postNumber(number, decimal):
    segments=bytes()
    a=1<<0
    b=1<<6
    c=1<<5
    d=1<<4
    e=1<<3
    f=1<<1
    g=1<<2
    dp=1<<7
    if   number == 1: segments =     b | c                  
    elif number == 2: segments = a | b |     d | e |     g 
    elif number == 3: segments = a | b | c | d |         g
    elif number == 4: segments =     b | c |         f | g
    elif number == 5: segments = a |     c | d     | f | g
    elif number == 6: segments = a |     c | d | e | f | g
    elif number == 7: segments = a | b | c                
    elif number == 8: segments = a | b | c | d | e | f | g
    elif number == 9: segments = a | b | c | d     | f | g
    elif number == 0: segments = a | b | c | d | e | f 
    elif number == ' ': segments = 0
    elif number == 'c': segments = g | e | d
    elif number == '-': segments = g
    else : segments = 0

    y=0
    while(y<8):
       GPIO.output(segmentClock,GPIO.LOW)
       GPIO.output(segmentData,segments & 1 << (7-y))
       GPIO.output(segmentClock,GPIO.HIGH)
       y += 1

while (number < 10):
    showNumber(number)
    number = number+1
    print number
    time.sleep(1)

GPIO.cleanup()


