"""
TO DO:
    - ADC
    - Verbose Debug
    - Better Reset/Reprogram
    - Logic
"""

# Imports
import time
import subprocess
import RPi.GPIO as GPIO

# Functions
def flash_program():
    try:
        return_code = subprocess.call("echo ./MSP430Flasher", shell=True)
        match return_code:
            case 0:
                print("Successfully Flashed")
            case 1:
                print("Error: Could not initialize device interface")
            case 2:
                print("Error: Could not close device interface")
            case 3:
                print("Debug Error: Invalid Parameter(s)")
            case 4:
                print("Error: Could not find device")
            case _:
                print(f"Error: {return_code}")
        return return_code
    except:
        print("ERROR: Unable to Flash")
        return -1
    

def reset_subject(option):
    match option:
        case 0: # Normal or Bit Flip Detected
            # Signal MSP430 program restart
            GPIO.output(22, GPIO.HIGH)
            status = GPIO.input(23)
            while (not status):
                status = GPIO.input(23)
            GPIO.output(22, GPIO.LOW)
        case 1: # Fatal Error
            for i in range(5):
                if (flash_program()):
                    print("Error: Attempt {i} - Unable to Reprogram")
                    continue
                time.sleep(1)
                status = GPIO.input(23)
                if (status):
                    print("Successful reprogramming")
                    return 0
                print("Error: Attempt {i} - Unable to Reprogram")
            print("Error: Failure to reprogram. Chip failure possible")
                

def read_charge():
    # Read ADC for charge
    return 0

def blast():
    # Release charge
    GPIO.output(12, GPIO.HIGH)
    charge = read_charge()
    while (charge > 0): # PWM still on so never 0
        charge = read_charge()
    GPIO.output(12, GPIO.LOW)

def record():
    none = GPIO.input(20)
    if (none):
        # Record no bit flips info
        reset_subject(0)
        return 0
    flip = GPIO.input(21)
    for i in range(5):
        if (flip):
            reset_subject(0)
            # Record bit flip
            return 1
        flip = GPIO.input(21)
    # Reprogram / Reset Subject
    reset_subject(1)
    # Record fatal error
    return 2


# User Inputs
charge = 0
chargeLevel = 0.8
channel = 0
frequency = 1000
dutyCycle = 50

# MAIN
LED_GPIO = 1    # Turn on warning LED

pwm = GPIO.PWM(channel, frequency)

try:
    while True:
        # Start PWM
        pwm.start(dutyCycle)
        
        # Wait for charge to reach specified level
        charge = read_charge()
        while (charge < chargeLevel):
            charge = read_charge()
        
        # Initiate injection and restart
        blast()
        pwm.stop()
        record()
        time.sleep(1)
except KeyboardInterrupt:
    # Stop PWM
    pwm.stop()
    # Discharge
    blast()
    pass

# Wait for capacitor bank to discharge
# blast()
# or
while (charge > 0):
    charge = read_charge()
    
LED_GPIO = 0    # Turn off warning LED

GPIO.cleanup()





