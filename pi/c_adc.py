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
    data = bus.read_byte(address)
    return data

def blast():
    # Release charge
    GPIO.output(LED_PIN, GPIO.HIGH) # Set Safety LED High
    pwm.start(dutyCycle)            # Start Charge
    time.sleep(.25)
    for i in range(50):
        pwm.stop()   
        time.sleep(.001)
        charge = read(2)            # Read Charge
        print (f"{i} : {(charge/255)*1000*3.3} V")
        if (charge >= chargeLevel):
            break
        pwm.start(dutyCycle)            # Start Charge
        time.sleep(.25)
    pwm.stop()   
    GPIO.output(PULSE_PIN, GPIO.HIGH)   # Turn on Pulse
    time.sleep(.1)                   # Stop Pulse
    GPIO.output(PULSE_PIN, GPIO.LOW)    # Turn off Pulse
    while (charge > 0):     # PWM still on so never 0
        charge = read(2)    # Read Charge
        GPIO.output(PULSE_PIN, GPIO.HIGH)   # Turn on Pulse
        time.sleep(.1)
        GPIO.output(PULSE_PIN, GPIO.LOW)    # Turn off Pulse
    GPIO.output(LED_PIN, GPIO.LOW)   # Set LED Low

def panic():
    GPIO.output(PULSE_PIN, GPIO.HIGH)   # Turn on Pulse
    time.sleep(.1)                      # Stop Pulse
    GPIO.output(PULSE_PIN, GPIO.LOW)    # Turn off Pulse
# Main
# ser = serial.Serial('COM5', 115200, timeout=2, stopbits=serial.STOPBITS_ONE, xonxoff = False)

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

frequency = 10000
dutyCycle = 50
pwm = GPIO.PWM(PWM_PIN, frequency)
# pwm.stop()

desiredVoltage = 600
chargeLevel = ( (desiredVoltage/1000)/3.3 ) * 255

# pwm = GPIO.PWM(PWM_PIN, frequency)
print("STARTING")
try:
    # pulse()
    for i in range(10):
        blast()
except KeyboardInterrupt:
    panic()
    pass

# ser.close()
pwm.stop()
GPIO.cleanup()