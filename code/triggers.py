#!/usr/bin/env python
import RPi.GPIO as GPIO
import time
import os
import glob

os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
#HLT sensor
sensor1 = base_dir + "28-0516b34c6aff" + "/w1_slave"
#Mash tun sensor
sensor2 = base_dir + "28-0416b3894bff" + "/w1_slave"

#LEDs that will simulate the SSR used for pumps and heating
LedRed = 15    # Heating
LedYellow = 13    # Wort Pump
LedGreen = 11    # HLT Pump

def read_temp_raw(sensor):
    f = open(sensor, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp_c(sensor):
    lines = read_temp_raw(sensor)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = int(temp_string) / 1000.0
        temp_c = round(temp_c, 1)
        return temp_c

GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
GPIO.setup(LedGreen, GPIO.OUT)   # Set LedPin's mode is output
GPIO.setup(LedYellow, GPIO.OUT)   # Set LedPin's mode is output
GPIO.setup(LedRed, GPIO.OUT)   # Set LedPin's mode is output

######################################
# Mashing process
# 
# For testing purposes, the mashing temperature will be set as really low.
# 
#
#####################################

try:
    while True:
        temp=read_temp_c(sensor1)
        print str(temp) + "oC"
        if temp < 30:
           GPIO.output(LedGreen, GPIO.HIGH)
           GPIO.output(LedRed, GPIO.HIGH)
           GPIO.output(LedYellow, GPIO.HIGH)
        elif temp > 30 and temp < 31:
           GPIO.output(LedYellow, GPIO.HIGH)
           GPIO.output(LedGreen, GPIO.LOW)
           GPIO.output(LedRed, GPIO.LOW)

except KeyboardInterrupt:
    GPIO.cleanup()

