import pigpio
import time
import signal
import sys
import os
import simple_pid

pi = pigpio.pi()
pid = simple_pid.PID()

# Configuration
FAN_PIN = 18            # BCM pin used to drive PWM fan
WAIT_TIME = 1           # [s] Time to wait between each refresh
pi.set_PWM_frequency(FAN_PIN, 20000)
pi.set_PWM_range(FAN_PIN, 100)
print("PWM Frequency: (2000?):", pi.get_PWM_frequency(FAN_PIN))
pid.sample_time = WAIT_TIME
pid.output_limits = (0, 100)

# Configurable temperature and fan speed
MIN_TEMP = 40
MAX_TEMP = 60
FAN_LOW = 1
FAN_HIGH = 100
FAN_OFF = 0
FAN_MAX = 100
pid.setpoint = 35
pid.tunings = (-4.0, 0.5, 0.1)

# Get CPU's temperature
def getCpuTemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    temp =(res.replace("temp=","").replace("'C\n",""))
    print("temp is {0}".format(temp)) # Uncomment for testing
    return temp

# Set fan speed
def setFanSpeed(speed):
    pi.set_PWM_dutycycle(FAN_PIN, speed)
    return()

# Handle fan speed
def handleFanSpeed():
    temp = float(getCpuTemperature())
    # Turn off the fan if temperature is below MIN_TEMP
    if temp < MIN_TEMP:
        setFanSpeed(FAN_OFF)
        print("Fan OFF") # Uncomment for testing
    # Set fan speed to MAXIMUM if the temperature is above MAX_TEMP
    elif temp > MAX_TEMP:
        setFanSpeed(FAN_MAX)
        print("Fan MAX") # Uncomment for testing
    # Caculate dynamic fan speed
    else:
        step = (FAN_HIGH - FAN_LOW)/(MAX_TEMP - MIN_TEMP)
        temp -= MIN_TEMP
        setFanSpeed(FAN_LOW + ( round(temp) * step ))
        print(FAN_LOW + ( round(temp) * step )) # Uncomment for testing
    return ()

def handleFanSpeed_PID():
    temp = float(getCpuTemperature())
    output = pid(temp)
    setFanSpeed(output)
    print("Fan Speed:",output)

try:
    setFanSpeed(FAN_OFF)
    # Handle fan speed every WAIT_TIME sec
    while True:
    #    handleFanSpeed_PID()
        handleFanSpeed()
        time.sleep(WAIT_TIME)

except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt
    setFanSpeed(FAN_HIGH)
    pi.stop()
