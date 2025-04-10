import serial
import time
import RPi.GPIO as GPIO
import os
import datetime
import csv
import smbus
import sys
# import matplotlib.pyplot as plt

# MAX COORD
X_MAXIMUM_COORD = 220
Y_MAXIMUM_COORD = 220
Z_MAXIMUM_COORD = 250

# MINIMUM RESOLUTION
X_MINIMUM_RES = .050
Y_MINIMUM_RES = .050
Z_MINIMUM_RES = .025

# UNTESTED MINIMUM RESOLUTION
X_MINIMUM_RES = .0125
Y_MINIMUM_RES = .0125
Z_MINIMUM_RES = .0025

# COLOR CONSTANTS
CBOLD     = '\33[1m'
CRED    = '\33[31m'
CGREEN  = '\33[32m'
CYELLOW = '\33[33m'
CBLUE   = '\33[34m'
CVIOLET = '\33[35m'
CBEIGE  = '\33[36m'
CEND    = '\33[0m'
CGREY    = '\33[90m'
CRED2    = '\33[91m'
CGREEN2  = '\33[92m'
CYELLOW2 = '\33[93m'
CBLUE2   = '\33[94m'
CVIOLET2 = '\33[95m'
CBEIGE2  = '\33[96m'
CWHITE2  = '\33[97m'

# Functions
def read(chn):
    bus.write_byte(address, channels[chn])
    bus.read_byte(address)
    return bus.read_byte(address)

def write_to_printer(g_code):
    ser.write(g_code.encode())
    time.sleep(1)
    response = ser.readline()
    rx = response.decode().strip()
    return rx

def move_to_coord(x, y, z):
    g_code = f'G0 X{x} Y{y} Z{z}\r\n'
    response = write_to_printer(g_code)

def wait_for_movement():
    iteration = 0
    while(True):
        g_code = 'M400\r\n'
        response = write_to_printer(g_code)
        if response == 'ok': break
        print(f"Waiting for Movement{'.'*((iteration%3)+1)}   ", end='\r', flush=True)
        iteration += 1
    print("                         ", end='\r')  # Clear waiting movement
    # print("Movement Complete              \n")

def get_result():
    global NE_totals; global BF_totals; global RO_totals
    global data
    flip_val = 0; reset_val = 0
    temp_start = time.time()
    # print(f"{x} {y} {z}", flush=True)
    print(f"| Start Waiting = {temp_start}\t", end="", flush=True)
    for i in range(10000): # was 10000
        flip_val += GPIO.input(FLIP_PIN)
        reset_val += GPIO.input(RESET_PIN)
    temp_end = time.time()
    temp_total = temp_end - temp_start
    print(f"\tEnd Waiting = {temp_end}", end="", flush=True)
    print(f"\tTotal = {temp_total}", end="\n", flush=True)
    print(f"RESULTS: {flip_val} {reset_val}")
    if ( not (flip_val > 0 or reset_val > 0) ):
        NE_totals += 1
        print(f"┗━━━━━━━| {CGREY}No Effect{CEND}\t\t|", end="", flush=True)
        data[z][y][x] = f"{CGREY}o{CEND}"
        # ax.scatter(new_y, new_x, new_z, edgecolors='gray', marker='o', facecolors='none', s=25, alpha=0.5)
        return 0
    else:
        write_to_printer('M300\r\n') # Beep printer
        if ( flip_val > 0 and not(reset_val > 0) ):
            BF_totals += 1
            print(f"| Bit Flip = {flip_val}", end="\n", flush=True)
            print(f"┗━━━━━━━| {CBLUE2}Bit Flip{CEND}\t\t|", end="", flush=True)
            data[z][y][x] = f"{CBLUE2}f{CEND}"
            # ax.scatter(new_y, new_x, new_z, color='blue', marker='o', s=50)
            return 1
        elif ( reset_val > 0 and not(flip_val > 0) ):
            RO_totals += 1
            print(f"┗━━━━━━━| {CRED2}Reset Occured{CEND}\t\t|", end="", flush=True)
            data[z][y][x] = f"{CRED2}r{CEND}"
            # ax.scatter(new_y, new_x, new_z, color='red', marker='o', s=50)
            return 2
        elif ( reset_val > 0 and flip_val > 0 ):
            BF_totals += 1; RO_totals += 1
            print(f"| Reset = {reset_val}\t\tBit Flip = {flip_val}", end="\n", flush=True)
            print(f"┗━━━━━━━| {CVIOLET}Both Detected{CEND}\t\t|", end="", flush=True)
            data[z][y][x] = f"{CVIOLET}b{CEND}"
            # ax.scatter(new_y, new_x, new_z, color='darkviolet', marker='o', s=50)
            return 3
        else:
            data[z][y][x] = f"{CGREY}b{CEND}"
            # ax.scatter(new_y, new_x, new_z, color='black', marker='o', s=25)
            return -1

def blast():
    global IC_totals
    global progress
    global remaining
    print(f"{current_run}/{total_runs}\t| 0v [{CYELLOW}{'▨'*0}{CEND}{(' '*10)}] {desiredVoltage}v\t| {CYELLOW2}Charging{CEND}", end='\r', flush=True)
    maxCharge = 0
    # Begin Charge
    GPIO.output(LED_PIN, GPIO.HIGH) # Set Safety LED High
    # print(f"PWM ON")
    pwm.start(dutyCycle)
    time.sleep(.25)
    for i in range(50):
        # print(f"PWM OFF")
        pwm.stop()   
        time.sleep(.001)
        charge = read(2)            # Read Charge
        voltageCharge = (charge/255)*1000*3.3
        if (charge >= chargeLevel):
            print(f"{current_run}/{total_runs}\t| 0v [{CYELLOW}{'■'*10}{CEND}] {desiredVoltage}v\t| {CGREEN}Complete{CEND}", end='\n', flush=True)
            break
        # print(f"PWM ON")
        progress = int((voltageCharge/desiredVoltage)*10)
        remaining = (10-progress)
        print(f"{current_run}/{total_runs}\t| 0v [{CYELLOW}{'▨'*progress}{CEND}{(' '*remaining)}] {desiredVoltage}v\t| {CYELLOW2}Charging{CEND}", end='\r', flush=True)
        if i == 49:
            print(f"{current_run}/{total_runs}\t| 0v [{CYELLOW}{'■'*progress}{CYELLOW}{('□'*remaining)}{CEND}] {desiredVoltage}v\t| {CRED}Incomplete{CEND}", end='\n', flush=True)
            IC_totals += 1
            break
        pwm.start(dutyCycle)            # Start Charge
        time.sleep(.25)
    
    # print(f"BLAST ON")
    GPIO.output(PULSE_PIN, GPIO.HIGH)
    time.sleep(.01)
    # print(f"BLAST OFF")
    GPIO.output(PULSE_PIN, GPIO.LOW)
    result = get_result()

    # if (interactive):
    #     fig.canvas.draw() 
    #     fig.canvas.flush_events() 

    # Wait for Complete Discharge
    while (charge > 0):
        # Turn on Pulse
        # print(f"BLAST ON")
        GPIO.output(PULSE_PIN, GPIO.HIGH)
        time.sleep(.01)
        # print(f"BLAST OFF")
        GPIO.output(PULSE_PIN, GPIO.LOW)
        # Read Charge
        charge = read(2)    

    # print(f"Discharged...")
    GPIO.output(LED_PIN, GPIO.LOW)   # Set LED Low

    progress = 0
    remaining = 0
    return maxCharge, result

def panic():
    pwm.stop()
    # print(f"PANIC BLAST ON")
    GPIO.output(PULSE_PIN, GPIO.HIGH)   # Turn on Pulse
    time.sleep(.5)
    # print(f"PANIC BLAST OFF")
    GPIO.output(PULSE_PIN, GPIO.LOW)    # Turn off Pulse

def graph_ascii():
    line = f"{'- '*x_len}"
    full = f"\t+ {line}+"
    print(f"{full * z_len}") 
    for y in range(y_len):
        print(f"\t| ", end="")
        for layer in range(z_len):
            # print(data[layer][y])
            for x in data[layer][y]:
                print(f"{x} ", end="")
            if (layer != z_len-1):
                print(f"|\t| ", end="")
        print("|")
    print(f"{full * z_len}")  

def calibrate():
    global x_min
    global y_min
    global z_min
    x = 0
    y = 0
    z = 0
    print(f"Entering {CYELLOW2}Calibration{CEND} Mode:\n")
    while(1):
        action = input(f"Enter {CRED}x{CEND}, {CBLUE}y{CEND}, {CGREEN}z{CEND}, or {CVIOLET}exit{CEND}: ")
        action = action.lower().strip().split(" ")
        if len(action) > 1:
            match action[0]:
                case "x":
                    try:
                        x_fmt = round(float(action[1]),3)
                        x += x_fmt if ( x+x_fmt <= X_MAXIMUM_COORD and x+x_fmt >= 0) else 0
                    except:
                        print(f"{CRED2}Invalid Input...{CEND} {action[1]}")
                        continue
                case "y":
                    try:
                        y_fmt = round(float(action[1]),3)
                        y += y_fmt if ( y+y_fmt <= Y_MAXIMUM_COORD and y+y_fmt >= 0) else 0
                    except:
                        print(f"{CRED2}Invalid Input...{CEND} {action[1]}")
                        continue
                case "z":
                    try:
                        z_fmt = round(float(action[1]),3)
                        z += z_fmt if ( z+z_fmt <= Z_MAXIMUM_COORD and z+z_fmt >= 0) else 0
                    except:
                        print(f"{CRED2}Invalid Input...{CEND} {action[1]}")
                        continue
                case _:
                    print(f"{CRED2}Invalid Multi-Operation...{CEND} {action[0]}")
                    continue
        else:
            match action[0]:
                case "x":
                    x_in = input("Input X Movement: ")
                    try:
                        x_in_fmt = round(float(x_in),3)
                        x += x_in_fmt if ( x+x_in_fmt <= X_MAXIMUM_COORD and x+x_in_fmt >= 0) else 0
                    except:
                        print(f"{CRED2}Invalid Input...{CEND} {x_in}")
                        continue    
                case "y":
                    y_in = input("Input Y Movement: ")
                    try:
                        y_in_fmt = round(float(y_in),3)
                        y += y_in_fmt if ( y+y_in_fmt <= Y_MAXIMUM_COORD and y+y_in_fmt >= 0) else 0
                    except:
                        print(f"{CRED2}Invalid Input...{CEND} {y_in}")
                        continue
                case "z":
                    z_in = input("Input Z Movement: ")
                    try:
                        z_in_fmt = round(float(z_in),3)
                        z += z_in_fmt if ( z+z_in_fmt <= Z_MAXIMUM_COORD and z+z_in_fmt >= 0) else 0
                    except:
                        print(f"{CRED2}Invalid Input...{CEND} {z_in}")
                        continue
                case "exit":
                    x_min = x
                    y_min = y
                    z_min = z
                    break
                case _:
                    print(f"{CRED2}Invalid Operation...{CEND} {action}")
                    continue
        move_to_coord(x,y,z)
        wait_for_movement()
    
def print_help():
    print("Usage:")
    print("\tpython ./m_testbench.py [options]")
    print("Options:")
    print("\t-h, --help \t\t: Display script usage and possible flags")
    print("\t-g, --graph \t\t: Output results as 3D graph after operation")
    print("\t-i, --interactive \t: Output results as 3D graph during operation")
    print("\t-a, --ascii \t\t: Display ASCII graph of results during operation (Only available in CLI)")
    print("\t-c, --calibrate \t: Enter calibration mode before executing tests")
    print("\t-f, --fast \t\t: Ignore home mechanism (Only use if homed already)")
    print("\t-t, --terminal \t\t: Display CLI instead of GUI")
    sys.exit()

def blast_handler():
    global current_run; global run_data
    global new_x; global new_y; global new_z; 
    start_time = time.time()
    new_x = x_min+x*.5
    new_y = y_min+y*.5
    new_z = z_min+z*.1
    current_run += 1
    move_to_coord(new_x,new_y,new_z)
    wait_for_movement()
    voltage, result = blast()
    run_data.append([desiredVoltage, voltage, result_code[result], new_x, new_y, new_z])
    end_time = time.time()

    seconds_left=(int(end_time-start_time))*(total_runs-current_run)
    minutes_left=seconds_left // 60
    hours_left=minutes_left // 60
    seconds_left=seconds_left % 60
    print(f" {((current_run+1)/total_runs)*100:02.2f}%\t{CGREY} (ETA= {hours_left:02d}:{minutes_left:02d}:{seconds_left:02d}){CEND}")
    
    if (ascii_show): graph_ascii()

# Defaults
x_res = 1
x_len = 7 # (x_max - x_min)//x_res
x_min = 100 #101 #99  #97
x_max = x_min + x_len*x_res

y_res= 1
y_len = 10 # (y_max - y_min)//y_res
y_min= 100 #112 #113          # 110
y_max = y_min + y_len*y_res

z_res = 0.5 # mm
z_len = 3   # (z_max - z_min)//z_res
z_min = 9 #8 #9.5    #6           # 8
z_max = z_min + z_len*z_res

multi_voltage_mode = False
desiredVoltage = 200

# Read and Set Options
interactive = False; graph_show = False; ascii_show = False
calibration_mode = False; homing = True
arguments = sys.argv[1:]
for arg in arguments:
    match arg:
        case "-h" | "--help":           print_help()
        # Graphing Options
        case "-g" | "--graph":          graph_show = True
        case "-i" | "--interactive":    interactive = True
        case "-a" | "--ascii":          ascii_show = True
        # Setup Options
        case "-c" | "--calibrate":      calibration_mode = True
        case "-f" | "--fast":           homing = False
        # Operation Option
        case "-t" | "--terminal":       print("GUI already disabled")
        # Invalid Handling
        case _:                         print(f"{CRED2}Invalid Option:{CEND} {arg}")

# Read Config and Overwrite Defaults
try:
    with open("config.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            expanded = line.split("=")
            match expanded[0]:
                case "x_min":
                    try: x_min = float(expanded[1])
                    except: print(f"{CRED2}Invalid config.txt:{CEND} {expanded[0]}")
                case "y_min":
                    try: y_min = float(expanded[1])
                    except: print(f"{CRED2}Invalid config.txt:{CEND} {expanded[0]}")
                case "z_min":
                    try: z_min = float(expanded[1])
                    except: print(f"{CRED2}Invalid config.txt:{CEND} {expanded[0]}")
                case "voltage":
                    try: 
                        voltages = expanded[1].split(",")
                        if (len(voltages)>1):
                            multi_voltage_mode = True
                            desiredVoltages = []
                            for voltage in voltages: desiredVoltages.append(float(voltage))
                        else: desiredVoltage = float(expanded[1])
                    except: print(f"{CRED2}Invalid config.txt:{CEND} {expanded[0]}")
except FileNotFoundError: print(f"{CRED2}Error:{CEND} File not found. Continuing with default values.")
except Exception as e: print(f"{CRED2}An error occurred:{CEND} {e}")

# Setup ADC
bus = smbus.SMBus(1)
channels = [0x40, 0x41, 0x43]
address = 0x48

if (multi_voltage_mode):
    chargeLevels = []
    for voltage in desiredVoltages:
        chargeLevels.append(( (voltage/1000)/3.3 ) * 255)
else:
    chargeLevel = ( (desiredVoltage/1000)/3.3 ) * 255

# Setup GPIO
FLIP_PIN = 11; RESET_PIN = 13
LED_PIN = 18; PULSE_PIN = 16; PWM_PIN = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setup(FLIP_PIN, GPIO.IN)
GPIO.setup(RESET_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(PULSE_PIN, GPIO.OUT)
GPIO.setup(PWM_PIN, GPIO.OUT)

frequency = 10000; dutyCycle = 50
pwm = GPIO.PWM(PWM_PIN, frequency)
# pwm = HardwarePWM(pwm_channel=0, hz=10000, chip=0)

# Setup Printer
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=2, stopbits=serial.STOPBITS_ONE, xonxoff = False)
g_code = 'G90\r\n'  # Set to absolute posisitioning
write_to_printer(g_code)

if (homing):
    g_code = 'G28\r\n'      # Homing calibrate printer
    write_to_printer(g_code)
    wait_for_movement()
    move_to_coord(0,0,20)   # Move to default posistion
    wait_for_movement()

if (calibration_mode): calibrate()

# Move into Place
move_to_coord(x_min,y_min,20)
fmtString = f"{CGREY}-----====={CEND} Starting {CYELLOW2}ERROR {CYELLOW}FRYER {CGREY}=====-----{CEND}\n"
for i in range(len(fmtString)):
    print(f"{fmtString[:i+1]}{CEND}", end="\r", flush=True)
    time.sleep(0.025)
wait_for_movement()
move_to_coord(x_min,y_min,z_min)

# Setup Graph
# if (interactive): plt.ion()
# fig = plt.figure()
# ax = fig.add_subplot(projection='3d')
# ax.view_init(elev=15)
# ax.invert_xaxis()
# ax.set_xlabel('X Position')
# ax.set_ylabel('Y Position')
# ax.set_zlabel('Z Position')
# ax.set_xlim(x_min, x_max)
# ax.set_ylim(y_min, y_max)
# ax.set_zlim(z_min, z_max)

# Setup Final Data Tracks
date = datetime.datetime.now()
run_data = []
data = [[[ " " for x in range(x_len)] for y in range(y_len)] for z in range(z_len)] 
result_code = ["Normal", "Bit Flip Detected", "Reset Occured", "Bit Flip and Reset"]
NE_totals = 0; BF_totals = 0; RO_totals = 0; IC_totals = 0; current_run = 0

# Blasting Loop
wait_for_movement() # Make sure probe is in place
print(f"\n\nBeginning {CRED2}Fault Injection{CEND}\n")
try:
    total_runs = y_len*x_len*z_len
    for y in range(y_len):
        for x in range(x_len):
            for z in range(z_len):
                if (multi_voltage_mode):
                    for index, v in enumerate(desiredVoltages):
                        desiredVoltage = v; chargeLevel = chargeLevels[index]
                        blast_handler()
                else: blast_handler()
except KeyboardInterrupt:
    print(f"{current_run}/{total_runs}\t| 0v [{CYELLOW}{'■'*progress}{CYELLOW}{('□'*remaining)}{CEND}] {desiredVoltage}v\t| {CRED}Incomplete{CEND}", end='\n', flush=True)
    print(f"┗━━━━━━━| {CGREY}Ended Early{CEND}\t\t| {((current_run+1)/total_runs)*100:02.2f}%\t{CGREY} (ETA= 00:00:00{CEND}")
    panic()

# Move Probe to Safe Location
move_to_coord(x_min,y_min,20)
fmtFinal = f"{CGREY}-----====={CEND} Stopped {CYELLOW2}ERROR {CYELLOW}FRYER {CGREY}=====-----{CEND}"
for i in range(len(fmtFinal)):
    print(f"{fmtFinal[:i+1]}{CEND}", end="\r", flush=True)
    time.sleep(0.025)
print("\n")
wait_for_movement() # Validate probe has reached location
# move_to_coord(0,200,20)         # Move probe off board
# wait_for_movement()

# Terminate Communications
ser.close(); pwm.stop(); GPIO.cleanup()

# Print Results of Test
print(f"{CBOLD}SUMMARY:{CEND}\n\tNo Effect\t: {NE_totals}\n\tBit Flips\t: {BF_totals}\n\tResets\t\t: {RO_totals}\n")
if (IC_totals != 0):
    print(f"\tIncomplete\t: {IC_totals}\n")

# Export Results as ".csv"
if (multi_voltage_mode): path = f"data/{date.year}-{date.month}-{date.day}_{date.hour}-{date.minute:02d}_{'v_'.join(str(desiredVoltages))}v"
else: path = f"data/{date.year}-{date.month}-{date.day}_{date.hour}-{date.minute:02d}_{desiredVoltage}v"
os.makedirs("data", exist_ok=True)
filename = f"{path}.csv"
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    field = ["desiredVotlage","voltage", "result", "x", "y", "z"]
    writer.writerow(field)
    for i in run_data: writer.writerow(i)

# Export Results as Graph Image (.png)
# ax.view_init(elev=15, azim=-60, roll=0) # double check
# plt.savefig(f"{path}-graph.png")
# if (graph_show):
#     plt.show()

# Export Settings into Config File
with open("config.txt", "w") as file:
    file.write(f"x_min={x_min:.3f}\n")
    file.write(f"y_min={y_min:.3f}\n")
    file.write(f"z_min={z_min:.3f}\n")
    if (multi_voltage_mode):
        file.write("voltage=")
        for voltage in range(len(desiredVoltages)-1): file.write(f"{desiredVoltages[voltage]},")
        file.write(f"{desiredVoltages[len(desiredVoltage)-1]}")
    else: file.write(f"voltage={desiredVoltage}")

# Exit Animation
fmtExit = f"Goodbye {CGREY}:){CEND}"
for i in range(len(fmtExit)):
    print(f"{fmtExit[:i+1]}{CEND}", end="\r", flush=True)
    time.sleep(0.025)
time.sleep(0.5)  
print(f"Goodbye {CGREY};){CEND}", end="\r", flush=True)
time.sleep(0.5)
print(f"Goodbye {CGREY}:){CEND}", end="\n\n", flush=True)
time.sleep(0.5)