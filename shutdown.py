import RPi.GPIO as GPIO
import time
import os

SHUTDOWN_PIN = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(SHUTDOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def Shutdown(channel):
    print("Shutting Down")
    time.sleep(5)
    os.system("sudo shutdown -h now")

GPIO.add_event_detect(SHUTDOWN_PIN, GPIO.FALLING, callback=Shutdown, bouncetime=2000)

while 1:
    time.sleep(2)