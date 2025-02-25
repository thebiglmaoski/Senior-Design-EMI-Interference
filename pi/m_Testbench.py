import serial
import time
import RPi.GPIO as GPIO
import os
import datetime
import csv
import smbus
import subprocess

# Function Definitions
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

def setup(Addr):
    global address
    address = Addr

def read(chn):
    bus.write_byte(address, channels[chn])
    bus.read_byte(address)
    return bus.read_byte(address)

def write_to_printer(g_code):
    ser.write(g_code.encode())
    time.sleep(1)
    response = ser.readline()
    rx = response.decode().strip()
    # print(rx)
    return rx

def wait_for_movement():
    while(True):
        g_code = 'M400\r\n'
        response = write_to_printer(g_code)
        if response == 'ok':
            break
        print("waiting for movement")
    print("movement complete")

def move_to_coord(x, y, z):
    g_code = f'G0 X{x} Y{y} Z{z}\r\n'
    response = write_to_printer(g_code)

def get_result():
    flip_val = GPIO.input(FLIP_PIN)
    error_val = GPIO.input(ERROR_PIN)
    critical_val = GPIO.input(CRITICAL_PIN)

    if ( not (flip_val or error_val or critical_val) ):
        return 0
    else:
        # Beep Printer
        g_code = 'M300\r\n'
        response = write_to_printer(g_code)
        print (f"Blasting @ X:{x} Y:{y} Z:{z}")

        if ( flip_val and not(error_val or critical_val) ):
            return 1
        elif ( error_val and not(flip_val or critical_val) ):
            return 2
        elif ( critical_val and not(flip_val or error_val) ):
            return 3
        else:
            return -1

def blast(x, y, z):
    print(f"Blasting @ [{x},{y},{z}]")
    maxCharge = 0
    # Begin Charge
    print(f"LED ON")
    GPIO.output(LED_PIN, GPIO.HIGH) # Set Safety LED High
    print(f"PWM ON")
    pwm.start(dutyCycle)
    time.sleep(.25)
    for i in range(50):
        print(f"PWM OFF")
        pwm.stop()   
        time.sleep(.001)
        charge = read(2)            # Read Charge
        maxCharge = charge
        print (f"{i} : {(charge/255)*1000*3.3} V")
        if (charge >= chargeLevel):
            break
        print(f"PWM ON")
        pwm.start(dutyCycle)            # Start Charge
        time.sleep(.25)

    # Wait for Complete Discharge
    while (charge > 0):
        # Turn on Pulse
        print(f"BLAST ON")
        GPIO.output(PULSE_PIN, GPIO.HIGH)
        time.sleep(.01)
        print(f"BLAST OFF")
        GPIO.output(PULSE_PIN, GPIO.LOW)
        # Read Charge
        charge = read(2)    

    print(f"LED OFF")
    GPIO.output(LED_PIN, GPIO.LOW)   # Set LED Low

    return maxCharge

def panic():
    print(f"PANIC BLAST ON")
    GPIO.output(PULSE_PIN, GPIO.HIGH)   # Turn on Pulse
    time.sleep(.5)
    print(f"PANIC BLAST OFF")
    GPIO.output(PULSE_PIN, GPIO.LOW)    # Turn off Pulse

    print("More safety?")

    
# User Inputs
x_res=10
y_res= 10
z_res = 1 # mm

x_min = 100
x_max = 160
x_len = (x_max - x_min) + 1

y_min= 150
y_max = 180
y_len = (y_max - y_min) + 1

z_min = 10
z_max = 13
z_len = (z_max - z_min) + 1

desiredVoltage = 600

# Main
bus = smbus.SMBus(1)
channels = [0x40, 0x41, 0x43]
address = None #initialize global variable
setup(0x48)

LED_PIN = 18
PULSE_PIN = 16
PWM_PIN = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(PULSE_PIN, GPIO.OUT)
GPIO.setup(PWM_PIN, GPIO.OUT)

FLIP_PIN = 20
ERROR_PIN = 21
CRITICAL_PIN = 22

GPIO.setup(FLIP_PIN, GPIO.IN)
GPIO.setup(ERROR_PIN, GPIO.IN)
GPIO.setup(CRITICAL_PIN, GPIO.IN)

frequency = 10000
dutyCycle = 50
pwm = GPIO.PWM(PWM_PIN, frequency)


chargeLevel = ( (desiredVoltage/1000)/3.3 ) * 255

# Setup Printer
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=2, stopbits=serial.STOPBITS_ONE, xonxoff = False)

# Set to absolute coordinates
g_code = 'G90\r\n'
write_to_printer(g_code)

# Home
g_code = 'G28\r\n'
write_to_printer(g_code)
wait_for_movement()

# Move to current
move_to_coord(x_min,y_min,z_min)
wait_for_movement()

date = datetime.datetime.now()
data = [] # [ [result_code, chargeVoltage, [x, y, z] ] ]
result_code = ["Normal", "Bit Flip Detected", "Internal Error", "Critical Failure", "External Failure"]


print("STARTING")
try:
    for y in range(5):
        for x in range(5):
            for z in range(z_len):
                move_to_coord(x_min+x,y_min+y,z_min+z)
                wait_for_movement()
                voltage = blast(x_min+x,y_min+y,z_min+z)
                data.append([voltage, get_result(), x_min+x, y_min+y, z_min+z])
except KeyboardInterrupt:
    panic()
    data.append([0, 4])
    pass

os.makedirs("data", exist_ok=True)
filename = f"data/{date.year}-{date.month}-{date.day}_{date.hour}-{date.minute}_{desiredVoltage}_{frequency}.csv"
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    field = ["id", "voltage", "result", "x", "y", "z"]

    writer.writerow(field)
    for i in data:
        writer.writerow(data[i])

ser.close()
GPIO.cleanup()

# MAX COORD
# X, Y  : 220mm
# Z     : 250mm

# TESTED FOR 50um
# Z CAN ACHIEVE 25um
# MAXIMUM RES x,y : 12.5um
# MAXIMUM RES z : 2.5um