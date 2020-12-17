import pigpio
import time
import signal
import sys
import os
import simple_pid
import datetime
import csv

pi = pigpio.pi()
pid = simple_pid.PID()

# Configuration
FAN_PIN = 18            # BCM pin used to drive PWM fan
#WAIT_TIME = 1           # [s] Time to wait between each refresh
T_sleep = 0.1
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
#    print("temp is {0}".format(temp)) # Uncomment for testing
    return temp

# Set fan speed
def setFanSpeed(speed):
    pi.set_PWM_dutycycle(FAN_PIN, speed)
    return()

class logData:
    
    def __init__(self):
        self.time_data = []
        self.Temp_data = []
        self.Fan_data = []

    def store_data(self, Temp, FanSpeed):
        t = datetime.datetime.now()
        T = Temp
        FanSpeed = FanSpeed
        self.time_data.append(t)
        self.Temp_data.append(Temp)
        self.Fan_data.append(FanSpeed)

    def write_data(self):
#        data_dict = {'Time': time_data, 'Temperature': Temp_data, 'Fan_Output' : Fan_data}
        with open('data.csv', mode='w') as data_file:
            data_writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#            for t, T, O in self.time_data, self.Temp_data, self.Fan_data:
            i = 0
            while i < len(self.time_data):
                data_writer.writerow([self.time_data[i], self.Fan_data[i], self.Temp_data[i]])
                i += 1


# Operating Sequence. Load cpu before starting using load.py
# 1. Set fan speed to 10 and wait for temperature to stabilize.
# 2. Get start time, Save T1, change fan speed to 80, wait for temp to change.
# 3. Get lag time, Wait for temperature to stabilize and get end time, save T2.
# 4. Calculate K, T_L, T
try:
    data = logData()
    setFanSpeed(10)                                                                         
    # Handle fan speed every WAIT_TIME sec
    T1_list = []
    T1_err = 1000
    print("Waiting for stabilization at fan = 10")                                          #1
    while T1_err > 0.2:
        if len(T1_list) < 100:
            T1 = float(getCpuTemperature())
            T1_list.append(T1)
            data.store_data(T1, 10)
        else:
            T1_list.pop(0)
            T1 = float(getCpuTemperature())
            T1_list.append(T1)
            data.store_data(T1, 10)
            T1_err = abs(T1 - (sum(T1_list) / len(T1_list)))
        print("Waiting for stabilization at fan = 10.  " + "T1: " + str(T1) + " T1_err: " + str(T1_err))
        time.sleep(T_sleep)
        #sys.stdout.write("CPU T_err: %d%% T: %d%%   \r" % (T_err, T))
        #sys.stdout.flush()
    print("Temperature Stabilized at:", T1)
    print("Changing Fan Speed and waiting for stabilization")
    time_start = datetime.datetime.now()
    setFanSpeed(80)                                                                           #2
    T2_err = 1000
    T2_list = []
    T2 = float(getCpuTemperature())
    data.store_data(T2, 80)
    while abs(T2 - (sum(T1_list) / len(T1_list))) < 5:
         T2 = float(getCpuTemperature())
         data.store_data(T2, 80)
         print("Waiting for change... T: ", T2)
         time.sleep(T_sleep)
    time_change = datetime.datetime.now()
    while T2_err > 0.2:
        if len(T2_list) < 100:
            T2 = float(getCpuTemperature())
            data.store_data(T2, 80)
            T2_list.append(T2)
        else:
            T2 = float(getCpuTemperature())
            T2_list.append(T2)
            data.store_data(T2, 80)
            T2_err = abs(T2 - (sum(T2_list) / len(T2_list)))
        print("Waiting for stabilization at fan = 80.  " + "T2: " + str(T2) + " T2_err: " + str(T2_err))
        time.sleep(T_sleep)
        #sys.stdout.write("CPU T_err: %d%% T: %d%%   \r" % (T_err, T))
        #sys.stdout.flush()
    time_end = datetime.datetime.now()                                                      #3
    print("Temperature Stabilized at: ", T2)
    print("T1, T2, Time_start, Time_change, Time_end: " , T1, T2, time_start, time_change, time_end)
    data.write_data()


except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt
    setFanSpeed(100)
    pi.stop()
