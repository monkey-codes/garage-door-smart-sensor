#!/usr/bin/env python3
from gpiozero import DistanceSensor
from time import sleep
import smbus
from time import sleep, strftime
from datetime import datetime
from LCD1602 import CharLCD1602
from collections import deque
import paho.mqtt.client as mqtt

lcd1602 = CharLCD1602()    

trigPin = 23
echoPin = 24
sensor = DistanceSensor(echo=echoPin, trigger=trigPin ,max_distance=3)

broker = "homeassistant.local"
port = 1883
config_topic = "homeassistant/device/garagepi/config"
state_topic = "homeassistant/device/garagepi/state"
username = ""
password = ""

client = mqtt.Client()
client.username_pw_set(username, password)
client.connect(broker, port, 60)
config = '''
{
  "dev": {
    "ids": "garagepi",
    "name": "Garage Pi",
    "mf": "monkey codes",
    "mdl": "Pi 1 Model B",
    "sw": "1.0",
    "sn": "ea334450945afc",
    "hw": "1.0"
  },
  "o": {
    "name":"monkeycodes",
    "sw": "1.0",
    "url": "https://github.com/monkey-codes/garage-door-smart-sensor"
  },
  "cmps": {
    "ultrasonic_distance": {
      "p": "sensor",
      "device_class":"distance",
      "unit_of_measurement":"cm",
      "value_template":"{{ value_json.distance}}",
      "unique_id":"ultrsnqdst"
    },
    "cpu_temp": {
      "p": "sensor",
      "device_class":"temperature",
      "unit_of_measurement":"°C",
      "value_template":"{{ value_json.cpu_temp}}",
      "unique_id":"cputemp"
    }
  },
  "state_topic":"homeassistant/device/garagepi/state",
  "qos": 2
}'''
client.publish(config_topic, config)
sample = '''
{
 "distance": 102.3,
 "cpu_temp": 45.2
}'''

def get_cpu_temp():     # get CPU temperature from file "/sys/class/thermal/thermal_zone0/temp"
    tmp = open('/sys/class/thermal/thermal_zone0/temp')
    cpu = tmp.read()
    tmp.close()
    return 'CPU Temp: {:.2f}'.format( float(cpu)/1000 ) + ' C '
 
def get_time_now():     # get system time
    return datetime.now().strftime('Time: %H:%M:%S')

def get_distance():
    return f'Distance: {(sensor.distance * 100):.2f}'

def publish():
    tmp = open('/sys/class/thermal/thermal_zone0/temp')
    cpu = tmp.read()
    tmp.close()
    cpu_temp = '{:.2f}'.format( float(cpu)/1000 )

    data = f'{{ "distance": {(sensor.distance * 100):.2f}, "cpu_temp": {cpu_temp} }}'
    #print(data)
    client.publish(state_topic, data)

def loop2():
    lcd1602.init_lcd()
    display_queue = deque([get_cpu_temp, get_time_now, get_distance])
    while True:
        lcd1602.clear()
        value1 = display_queue[0]()
        value2 = display_queue[1]()
        lcd1602.write(0, 0, value1)
        lcd1602.write(0, 1, value2)
        #print(value1) print(value2)
        display_queue.rotate(-1)
        publish()
        sleep(2)

    

def loop(): 
    lcd1602.init_lcd()
    while True:
        lcd1602.clear()
        #lcd1602.write(0, 0, 'd:' + str(sensor.distance * 100))
        lcd1602.write(0, 0, f'Distance: {(sensor.distance * 100):.2f}')
        print('Distance: ', sensor.distance * 100,'cm')
        sleep(1)
        
if __name__ == '__main__':     # Program entrance
    print ('Program is starting...')
    try:
        loop2()
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        sensor.close()
        
        print("Ending program")
