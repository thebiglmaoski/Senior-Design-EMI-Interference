import serial
import smbus   
import time
import RPi.GPIO as GPIO

# Function Definitions
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
        print("Moving...")
    # print("movement complete")

def move_to_coord(x, y, z):
    g_code = f'G0 X{x} Y{y} Z{z}\r\n'
    response = write_to_printer(g_code)

def blast(x, y, z):
    # Release charge
    GPIO.output(LED_PIN, GPIO.HIGH) # Set Safety LED High
    pwm.start(dutyCycle)            # Start Charge
    charge = read(2)                # Read Charge
    while (charge >= chargeLevel):  # Wait for Charge
        charge = read(2)            # Read Charge
    g_code = 'M300\r\n'             
    response = write_to_printer(g_code)
    print (f"Blasting @ X:{x} Y:{y} Z:{z}")
    GPIO.output(PULSE_PIN, GPIO.HIGH)   # Turn on Pulse
    pwm.stop()                          # Stop Pulse
    GPIO.output(PULSE_PIN, GPIO.LOW)    # Turn off Pulse
    while (charge > 0):     # PWM still on so never 0
        charge = read(2)    # Read Charge
    GPIO.output(LED_PIN, GPIO.LOW)   # Set LED Low

# Main
ser = serial.Serial('COM5', 115200, timeout=2, stopbits=serial.STOPBITS_ONE, xonxoff = False)

bus =      .SMBus(1)
channels = [0x40, 0x41, 0x43]
address = None #initialize global variable
setup(0x48)

LED_PIN = 12
PULSE_PIN = 13
PWM_PIN = 14

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(PULSE_PIN, GPIO.OUT)
GPIO.setup(PWM_PIN, GPIO.OUT)

frequency = 1000
dutyCycle = 50
chargeLevel = 0.2
pwm = GPIO.PWM(PWM_PIN, frequency)


# Set to relative coordinates
g_code = 'G91\r\n'
write_to_printer(g_code)

# Move probe to home coordinates
g_code = 'G28\r\n'
write_to_printer(g_code)
wait_for_movement()

# Raise probe and prepare for commands
move_to_coord(0,0,20)

try:
    while(1):
        action = input("Enter X, Y, Z, or Blast: ")
        action = action.lower().strip()
        match action:
            case "x":
                x = input("Input X Movement: ")
                x = x.strip()
                if (not x.isdigit()):
                    print("Invalid Input.")
                    continue
                # Move to input
                move_to_coord(x,0,0)
                # Wait
                wait_for_movement()
            case "y":
                y = input("Input Y Movement: ")
                y = y.strip()
                if (not y.isdigit()):
                    print("Invalid Input.")
                    continue
                # Move to input
                move_to_coord(0,y,0)
                # Wait
                wait_for_movement()
            case "z":
                z = input("Input Z Movement: ")
                z = z.strip()
                if (not z.isdigit()):
                    print("Invalid Input.")
                    continue
                # Move to input
                move_to_coord(0,0,z)
                # Wait
                wait_for_movement()
            case "blast":
                blast()
            case _:
                print("Invalid Operation.")
        
except KeyboardInterrupt:
    print("Exiting...")

ser.close()
pwm.stop()
GPIO.cleanup()