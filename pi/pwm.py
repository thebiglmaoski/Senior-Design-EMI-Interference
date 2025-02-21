# import serial
import smbus   
import time
import RPi.GPIO as GPIO

# Function Definitions
# def setup(Addr):
#     global address
#     address = Addr

# def read(chn):
#     # while (1):
#     bus.write_byte(address, channels[chn])
#         # print(bus.read_byte(address))
#         # print(bus.read_byte(address))
#         # print()
#         # time.sleep(.5)
#     return bus.read_byte(address)

# def write_to_printer(g_code):
#     ser.write(g_code.encode())
#     time.sleep(1)
#     response = ser.readline()
#     rx = response.decode().strip()
#     # print(rx)
#     return rx

# def wait_for_movement():
#     while(True):
#         g_code = 'M400\r\n'
#         response = write_to_printer(g_code)
#         if response == 'ok':
#             break
#         print("Moving...")
#     # print("movement complete")

# def move_to_coord(x, y, z):
#     g_code = f'G0 X{x} Y{y} Z{z}\r\n'
#     response = write_to_printer(g_code)

def blast():
    # Release charge
    print(f"LED ON")
    GPIO.output(LED_PIN, GPIO.HIGH) # Set Safety LED High
    print(f"PWM ON")
    pwm.start(dutyCycle)
    time.sleep(2)
    print(f"PWM OFF")
    pwm.stop()
    # time.sleep(1)
    pulse()
    time.sleep(1)
    print(f"LED OFF")
    GPIO.output(LED_PIN, GPIO.LOW)   # Set LED Low

def charge_only():
    print(f"PWM ON")
    pwm.start(dutyCycle)
    time.sleep(2.5)
    print(f"PWM OFF")
    pwm.stop()

def pulse():
    print(f"BLAST ON")
    GPIO.output(PULSE_PIN, GPIO.HIGH)   # Turn on Pulse
    time.sleep(.5)
    print(f"BLAST OFF")
    GPIO.output(PULSE_PIN, GPIO.LOW)    # Turn off Pulse

def pulse_on():
    GPIO.output(PULSE_PIN, GPIO.HIGH)   # Turn on Pulse

# Main
# ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=2, stopbits=serial.STOPBITS_ONE, xonxoff = False)

# bus = smbus.SMBus(1)
# channels = [0x40, 0x41, 0x43]
# address = None #initialize global variable
# setup(0x48)

LED_PIN = 18
PULSE_PIN = 16
PWM_PIN = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(PULSE_PIN, GPIO.OUT)
GPIO.setup(PWM_PIN, GPIO.OUT)

frequency = 10000
dutyCycle = 50
pwm = GPIO.PWM(PWM_PIN, frequency)
pwm.stop()

desiredVoltage = 200
chargeLevel = .2 # ( (desiredVoltage/1000)/3.3 ) * 255

# pwm = GPIO.PWM(PWM_PIN, frequency)
print("STARTING")
try:
    # pulse()
    for i in range(3):
        blast()
except KeyboardInterrupt:
    pass

# ser.close()
GPIO.cleanup()
print("CLEAN")