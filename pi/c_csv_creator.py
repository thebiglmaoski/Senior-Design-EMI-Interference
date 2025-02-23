import csv
import datetime
import os

# import RPi.GPIO as GPIO

result_codes = ["No Fault", "Bit Flip Detected", "Critical Error"] # Latch up? Other Errors?
bitFlip = 0 # Replace with the desired GPIO pin number
ErrorCode = 1
BrownOutCode = 2

# GPIO.setup(bitFlip, GPIO.IN)
# GPIO.setup(ErrorCode, GPIO.IN)
# GPIO.setup(BrownOutCode, GPIO.IN)

# bitFlip_val = GPIO.input(bitFlip)
# ErrorCode_val = GPIO.input(ErrorCode)
# BrownOutCode_val = GPIO.input(BrownOutCode)

# print(bitFlip_val)
# print(ErrorCode_val)
# print(BrownOutCode_val)

# GET INPUTS
# EXAMPLE:
results = [0, 2, 1, 1, 0, 0, 1, 1, 0, 1, 0]


date = datetime.datetime.now()

desiredVoltage = 200
frequency = 10000

os.makedirs("data", exist_ok=True)
filename = f"data/{date.year}-{date.month}-{date.day}_{date.hour}-{date.minute}_{desiredVoltage}_{frequency}.csv"
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    field = ["id", "voltage", "result"]

    writer.writerow(field)
    for i in range(10):
        writer.writerow([i, 201.48, result_codes[results[i]]])
