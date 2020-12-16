import pigpio
import time
import signal
import sys
import os
import simple_pid
import datetime

pi = pigpio.pi()
pid = simple_pid.PID()

# Configuration
FAN_PIN = 18            # BCM pin used to drive PWM fan
#WAIT_TIME = 1           # [s] Time to wait between each refresh
pi.set_PWM_frequency(FAN_PIN, 20000)
pi.set_PWM_range(FAN_PIN, 100)
print("PWM Frequency: (2000?):", pi.get_PWM_frequency(FAN_PIN))
pid.sample_time = 1
pid.output_limits = (0, 100)

pid.setpoint = 35
pid.tunings = (-1, 0, 0)

# Get CPU's temperature
def getCpuTemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    temp =(res.replace("temp=","").replace("'C\n",""))
    #print("temp is {0}".format(temp)) # Uncomment for testing
    return temp

# Set fan speed
def setFanSpeed(speed):
    pi.set_PWM_dutycycle(FAN_PIN, speed)
    return()

try:
    setFanSpeed(10)
    # Handle fan speed every WAIT_TIME sec
    T1_list = []
    T1_err = 1000
    print("Waiting for stabilization at fan = 10")
    while T1_err > 0.3:
        if len(T1_list) < 1000:
            T1 = float(getCpuTemperature())
            T1_list.append(T1)
        else:
            T1_list.pop(0)
            T1 = float(getCpuTemperature())
            T1_list.append(T1)
            T1_err = abs(T1 - (sum(T1_list) / len(T1_list)))
        print("T1: " + str(T1) + " T1_err: " + str(T1_err))
        #sys.stdout.write("CPU T_err: %d%% T: %d%%   \r" % (T_err, T))
        #sys.stdout.flush()
    print("Temperature Stabilized at:", T1)
    print("Changing Fan Speed and waiting for stabilization")
    time_start = datetime.datetime.now()
    setFanSpeed(80)
    T2_err = 1000
    T2_list = []
    T2 = float(getCpuTemperature())
    while abs(T2 - (sum(T1_list) / len(T1_list))) < 2:
         T2 = float(getCpuTemperature())
         print("Waiting for change... T: ", T2)
    time_change = datetime.datetime.now()
    while T2_err > 0.3:
        if len(T2_list) < 1000:
            T2 = float(getCpuTemperature())
            T2_list.append(T2)
        else:
            T2 = float(getCpuTemperature())
            T2_list.append(T2)
            T2_err = abs(T2 - (sum(T2_list) / len(T2_list)))
        print("T2: " + str(T2) + " T2_err: " + str(T2_err))
        #sys.stdout.write("CPU T_err: %d%% T: %d%%   \r" % (T_err, T))
        #sys.stdout.flush()
    time_end = datetime.datetime.now()
    print("Temperature Stabilized at: ", T2)
    print("T1, T2, Time_start, Time_change, Time_end: " , T1, T2, time_start, time_change, time_end)


except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt
    setFanSpeed(100)
    pi.stop()