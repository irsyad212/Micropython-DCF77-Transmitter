# Based on: https://github.com/smre/DCF77/blob/master/DCF77.py

import time
import math
import machine

# Offset from UTC in seconds
OFFSET = 2*3600

# Seconds in a minute
ONE_MINUTE = 60

# Is It DST
DST = True

# LED Indicator
led = machine.Pin(2, machine.Pin.OUT)

# Transmitter Initalizer (change frequency in the main code)
signal = machine.PWM(machine.Pin(5), freq=10, duty=10)

# Get localtime (tz is not supported)
def localtime():
    return time.time() + OFFSET

#Convert int to BCD 
def to_binary(value, size):
    binary_value = '{0:b}'.format(int(value))
    return ("".join(reversed(binary_value))) + ('0' * (size - len(binary_value)))

#Convert int to BCD String
def bcd(value, size):
    if size <= 4:
        return to_binary(value, size)
    else:
        ones = to_binary(math.floor(value % 10), 4)
        tens = to_binary(math.floor(value / 10), size - 4)
        return ones + tens

# Calculate even parity bit
def even_parity(value):
    return str(value.count('1') % 2)

def CodeTime(t, dst):
    dcf = '0' * 17

    if(dst):
        dcf += '10'
    else :
        dcf += '01'
        
    dcf += '01'
    
    tm = time.gmtime(t)
    year = tm[0]
    month = tm[1]
    mday = tm[2]
    hour = tm[3]
    minute = tm[4]
    weekday = tm[6]
    
    # minutes + parity bit
    dcf += bcd(minute, 7)
    dcf += even_parity(bcd(minute, 7))

    # hours + parity bit
    dcf += bcd(hour, 6)
    dcf += even_parity(bcd(hour, 6))

    # day of month
    dcf += bcd(mday, 6)
    
    wday = weekday
    
    if(wday == 0):
        wday = 7
        
    # day of week
    dcf += bcd(wday + 1, 3)

    # month number
    dcf += bcd(month, 5)

    # year (within century) + parity bit for all date bits
    dcf += bcd(year % 100, 8)
    dcf += even_parity(bcd(month, 6) + bcd(wday + 1, 3) + bcd(month, 5) + bcd(year % 100, 8))

    # special "59th" second (no amplitude modulation)
    dcf += '-'
    
    return dcf

def DcfOut():
    now = localtime()+ONE_MINUTE
    tm = time.gmtime(now)
    second = tm[5]
    seq = CodeTime(now, DST)
    code = seq[second]

    if(code == '-'):
        led.value(1)
        signal.duty(512)
        time.sleep(0.9)
    elif(code == '0'):
        led.value(0)
        signal.duty(0)
        time.sleep(0.09)
        led.value(1)
        signal.duty(512)
        time.sleep(0.89)
    elif(code == '1'):
        led.value(0)
        signal.duty(0)
        time.sleep(0.19)
        led.value(1)
        signal.duty(512)
        time.sleep(0.79)
    else:
        led.value(1)
        signal.duty(512)
    
def main():
    # Change Frequency here
    signal.init(freq=77500, duty=512)
    print(CodeTime(localtime()+ONE_MINUTE, DST))
    
    while(1):
        DcfOut()
    
if(__name__ == '__main__'):
    main()