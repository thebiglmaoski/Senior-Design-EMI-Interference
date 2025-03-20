import time

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

# Color Display
# x = 0
# for i in range(24):
#   colors = ""
#   for j in range(5):
#     code = str(x+j)
#     colors = colors + "\33[" + code + "m\\33[" + code + "m\033[0m "
#   print(colors)
#   x = x + 5

# Preparing
# anim = [CYELLOW, CYELLOW2]
# for i in range(50):
#     sec1 = anim[i%2]
#     sec2 = anim[(i+1)%2]
#     print(f"Starting {sec1}E{sec2}r{sec1}r{sec2}o{sec1}r {sec2}F{sec1}r{sec2}y{sec1}e{sec2}r{CEND}", end="\r")
#     time.sleep(0.2)

fmtString = f"{CGREY}-----====={CEND} Starting {CYELLOW2}ERROR {CYELLOW}FRYER {CGREY}=====-----{CEND}"
for i in range(len(fmtString)):
    print(f"{fmtString[:i+1]}{CEND}", end="\r", flush=True)
    time.sleep(0.025)

print("\n")
try:
    iteration = 0
    while (1):
        print(f"Waiting for Movement{"."*((iteration%3)+1)}   ", end='\r', flush=True)
        iteration +=1
        time.sleep(0.5)
except:
    print(f"\n\nBeginning {CRED2}Fault Injection{CEND}\n")



# Running
status_codes = ["Complete", "Charging", "Incomplete"]  
result_codes = ["No Effect", "Bit Flip", "Reset Occured"]      
total_runs = 75
desired_voltage = 200
# ID/TOTAL  : 0v [xxxxxxxxxxxxxxxxx] Vd     :   STATUS
# 78/300    : 0v [xxxxxxxxxxxxxxxxx] 600v   :   Charging...
#                                               Complete, Charging, Incomplete
# 

NE_totals = 280
BF_totals = 5
RO_totals = 15
NULL_totals = 0

# data = [ [ ["o", "o", "o", "o", "o"], 
#            ["r", "b", "f", "o", "o"], 
#            ["r", "r", "b", "o", "o"], 
#            ["x", "x", "o", "o", "o"], 
#            ["f", "o", "o", "o", "o"] ], 

#          [ ["o", "o", "o", "o", "o"], 
#            ["r", "f", "o", "o", "o"], 
#            ["r", "b", "o", "o", "o"], 
#            ["o", "o", "o", "o", "o"], 
#            ["o", "o", "o", "o", "o"] ], 

#          [ ["o", "o", "o", "o", "o"], 
#            ["o", "o", "o", "o", "o"], 
#            ["r", "o", "o", "o", "o"], 
#            ["o", "o", "o", "o", "o"], 
#            ["o", "o", "o", "o", "o"] ]]

# data = [ [ [" ", " ", " ", " ", " "], 
#            [" ", " ", " ", " ", " "], 
#            [" ", " ", " ", " ", " "], 
#            [" ", " ", " ", " ", " "], 
#            [" ", " ", " ", " ", " "] ], 

#          [ [" ", " ", " ", " ", " "], 
#            [" ", " ", " ", " ", " "], 
#            [" ", " ", " ", " ", " "], 
#            [" ", " ", " ", " ", " "], 
#            [" ", " ", " ", " ", " "] ], 

#          [ [" ", " ", " ", " ", " "], 
#            [" ", " ", " ", " ", " "], 
#            [" ", " ", " ", " ", " "], 
#            [" ", " ", " ", " ", " "], 
#            [" ", " ", " ", " ", " "] ] ]

data = [[[ " " for j in range(5)]  for j in range(5)] for i in range(3)] 

# for layer in data:
#     print("NEW LAYER:")
#     print("+ - - - - - +")
#     for y in layer:
#         print(f"| ", end="")
#         for x in y:
#             if x == "r":
#                 print(f"{CRED}{x}{CEND} ", end="")
#             elif x == "b":
#                 print(f"{CVIOLET}{x}{CEND} ", end="")
#             elif x == "f":
#                 print(f"{CBLUE2}{x}{CEND} ", end="")
#             else:
#                 print(f"{CGREY}{x}{CEND} ", end="")
#         print(f"|")
#     print("+ - - - - - +")    

try:
    for current_run in range(total_runs):
        run_progress = ((current_run+1)/total_runs)*100
        try:
            for voltage in range(desired_voltage+1):
                time.sleep(.01)
                progress = int((voltage/desired_voltage)*10)
                remaining = (10-progress)
                print(f"{current_run+1}/{total_runs}\t| 0v [{CYELLOW}{'▨'*progress}{CEND}{(' '*remaining)}] {desired_voltage}v\t| {CYELLOW2}{status_codes[1]}{CEND}", end='\r', flush=True)
            print(f"{current_run+1}/{total_runs}\t| 0v [{CYELLOW}{'■'*progress}{CEND}] {desired_voltage}v\t| {CGREEN}{status_codes[0]}{CEND}", end='\n', flush=True)
        except:
            print(f"{current_run+1}/{total_runs}\t| 0v [{CYELLOW}{'■'*progress}{CYELLOW}{('□'*remaining)}{CEND}] {desired_voltage}v\t| {CRED}{status_codes[2]}{CEND}", end='\n', flush=True)
            # Wait for Force Quit
            time.sleep(0.5)
        print(f"┗━━━━━━━| {CBLUE2 if (current_run%3 == 1) else CRED2 if (current_run%3 == 2) else CGREY}{result_codes[current_run%3]}{CEND}\t\t| {run_progress:02.2f}%\t{CGREY}(ETA: 00:01:15){CEND}")

        data[current_run%3][current_run//15][(current_run//3)%5] = "f" if (current_run%3 == 1) else "r" if (current_run%3 == 2) else "o"
        print(data)
        # print("\t+ - - - - - +")
        # for y in data[current_run%3]:
        #     print(f"\t| ", end="")
        #     for x in y:
        #         if x == "r":
        #             print(f"{CRED}{x}{CEND} ", end="")
        #         elif x == "b":
        #             print(f"{CVIOLET}{x}{CEND} ", end="")
        #         elif x == "f":
        #             print(f"{CBLUE2}{x}{CEND} ", end="")
        #         else:
        #             print(f"{CGREY}{x}{CEND} ", end="")
        #     print(f"|")
        # print("\t+ - - - - - +\n")   

        print("\t+ - - - - - +\t+ - - - - - +\t+ - - - - - +")
        for y in range(len(data[0])):
            print(f"\t| ", end="")
            for layer in range(3):
                for x in data[layer][y]:
                    if x == "r":
                        print(f"{CRED}{x}{CEND} ", end="")
                    elif x == "b":
                        print(f"{CVIOLET}{x}{CEND} ", end="")
                    elif x == "f":
                        print(f"{CBLUE2}{x}{CEND} ", end="")
                    elif x == "o":
                        print(f"{CGREY}{x}{CEND} ", end="")
                    else:
                        print(f"{x} ", end="")
                if (layer != 2):
                    print(f"|\t| ", end="")
            print("|")
        print("\t+ - - - - - +\t+ - - - - - +\t+ - - - - - +")  
            # for x in data[1][y]:
            #     if x == "r":
            #         print(f"{CRED}{x}{CEND} ", end="")
            #     elif x == "b":
            #         print(f"{CVIOLET}{x}{CEND} ", end="")
            #     elif x == "f":
            #         print(f"{CBLUE2}{x}{CEND} ", end="")
            #     elif x == "o":
            #         print(f"{CGREY}{x}{CEND} ", end="")
            #     else:
            #         print(f"{x} ", end="")
            # print(f"|\t| ", end="")
            # for x in data[2][y]:
            #     if x == "r":
            #         print(f"{CRED}{x}{CEND} ", end="")
            #     elif x == "b":
            #         print(f"{CVIOLET}{x}{CEND} ", end="")
            #     elif x == "f":
            #         print(f"{CBLUE2}{x}{CEND} ", end="")
            #     elif x == "o":
            #         print(f"{CGREY}{x}{CEND} ", end="")
            #     else:
            #         print(f"{x} ", end="")       
            # print("|")
        # print("\t+ - - - - - +\t+ - - - - - +\t+ - - - - - +")  
        


except:
    print(f"┗━━━━━━━| {CGREY}INVALID{CEND}\t\t| {run_progress:02.2f}%\t{CGREY}(ETA: 00:00:00){CEND}")
    print("\n")

fmtFinal = f"{CGREY}-----====={CEND} Stopped {CYELLOW2}ERROR {CYELLOW}FRYER {CGREY}=====-----{CEND}"
for i in range(len(fmtFinal)):
    print(f"{fmtFinal[:i+1]}{CEND}", end="\r", flush=True)
    time.sleep(0.025)
print("\n")

print(f"{CBOLD}SUMMARY:{CEND}\n\tNo Effect\t: {NE_totals}\n\tBit Flips\t: {BF_totals}\n\tResets\t\t: {RO_totals}\n\tIncomplete\t: {NULL_totals}\n")

fmtExit = f"Goodbye {CGREY}:){CEND}"
for i in range(len(fmtExit)):
    print(f"{fmtExit[:i+1]}{CEND}", end="\r", flush=True)
    time.sleep(0.025)
time.sleep(0.5)  
print(f"Goodbye {CGREY};){CEND}", end="\r", flush=True)
time.sleep(0.5)
print(f"Goodbye {CGREY}:){CEND}", end="\n\n", flush=True)
time.sleep(0.5)

# ------------------- SIMPLE
"""
toolbar_width = 40
# setup toolbar
print(f"[{(" " * toolbar_width)}]", end="", flush=True)
print(f"{"\b" * (toolbar_width+1)}", end="", flush=True) # return to start of line, after '['
progress = 0
try:
    for i in range(toolbar_width):
        time.sleep(0.1) # do real work here
        # update the bar
        print("▨", end="", flush=True)
        progress = i
    print(f"{"\b" * (toolbar_width+1)}", end="", flush=True) # return to start of line, after '['
    print(f"[{("■" * toolbar_width)}]", flush=True)
except:
    print(f"{"□" * (toolbar_width-progress-1)}", end="", flush=True)
    print(f"{"\b" * (toolbar_width)}", end="", flush=True)
    print(f"{("■" * (progress+1))}", flush=True)"
"""
