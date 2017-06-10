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

def mashing(temp_target, mash_time):
    try:
        start_temp = read_temp_c(sensor1)
        print "Start temperature of the mash: " + str(start_temp)
        elapsed_time = 0
        start_time = time.time()
        mash_time = mash_time * 60
        while mash_time >= elapsed_time:
            temp=read_temp_c(sensor1)
            print str(temp) + "oC"
            temp_diff = temp - start_temp
            start_temp = read_temp_c(sensor1)
            if temp_diff >= 0.5:
               print "Temperature is rising over 1oC per minute" 
            if temp < temp_target:
               GPIO.output(LedGreen, GPIO.HIGH)
               GPIO.output(LedRed, GPIO.HIGH)
               GPIO.output(LedYellow, GPIO.HIGH)
            elif temp > temp_target:
               GPIO.output(LedYellow, GPIO.HIGH)
               GPIO.output(LedGreen, GPIO.LOW)
               GPIO.output(LedRed, GPIO.LOW)
            time.sleep(30)
            elapsed_time = time.time() - start_time
            print "Step time:" + str(elapsed_time)
        GPIO.cleanup()
    except KeyboardInterrupt:
        GPIO.cleanup()

if __name__ == "__main__":
   mashing(30, 3)
