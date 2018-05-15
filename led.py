from flask import Flask, request, jsonify, g
import json
import requests
from pymongo import MongoClient
import RPi.GPIO as GPIO  
import time
from led_pins import*
from six.moves import input  
from zeroconf import ServiceBrowser, ServiceInfo, Zeroconf
import socket
from led_pins import*

#ping the IP address from google
desc = {'path': '/led'}
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8",80))
ip = s.getsockname()[0]
s.close

#creating information for zeroconf
info = ServiceInfo("_http._tcp.local.",
                   "led._http._tcp.local.",
                   socket.inet_aton(ip), 5000, 0, 0,
                   desc, "led.local.")
zeroconf = Zeroconf()
print("Registering Pi as a service...")
zeroconf.register_service(info)

#addressList = [["192.168.0.100", "192.168.0.101", "192.168.0.102"], [8080, 9999, 9999]]


# Flask
app = Flask(__name__)

#current values for red, green, blue, rate, and state
curr_red = 0
curr_blue = 0
curr_green = 0
rateSec = 0
On = 0

#set up the LED GPIO
modeNumber = led_pins["mode"]
redPin = led_pins["red"]
bluePin = led_pins["blue"]
greenPin = led_pins["green"]

if modeNumber == 10:
    GPIO.setmode(GPIO.BOARD)
elif modeNumber == 11:
    GPIO.setmode(GPIO.BCM)

GPIO.setup(redPin, GPIO.OUT)
GPIO.setup(bluePin, GPIO.OUT)
GPIO.setup(greenPin, GPIO.OUT)

 # 50Hz PWM Frequency
pwm_red = GPIO.PWM(redPin, 400)
pwm_blue = GPIO.PWM(bluePin, 400)
pwm_green = GPIO.PWM(greenPin, 400)
pwm_red.start(float(curr_red))
pwm_blue.start(float(curr_blue))
pwm_green.start(float(curr_green))

@app.route('/init', methods=['GET'])
def init():
    if request.method == 'GET': 
        return "LED"

#get method that returns the current values of parameters for GET and POSST
@app.route('/led', methods=['POST', 'GET'])
def led():
    if request.method == 'GET':
        global curr_red, curr_blue, curr_green, rateSec, On
        if rateSec == 0:
            data = {"intensity":{"red": str(curr_red), "blue": str(curr_blue), "green": str(curr_green), "rate": str(rateSec), "state": str(On)}}
        else:
            newRate = 1/rateSec;
            data = {"intensity":{"red": str(curr_red), "blue": str(curr_blue), "green": str(curr_green), "rate": str(newRate), "state": str(On)}}
        return json.dumps(data)
    
    elif request.method == 'POST':
        print("received a POST request")
        global curr_red, curr_blue, curr_green, rateSec, On
        led_data = request.json
        green_duty1 = led_data["green"]
        red_duty1 = led_data["red"]
        blue_duty1 = led_data["blue"]
        rateSec1 = led_data["rate"]
        On1 = led_data["state"]
        
        green_duty = float(green_duty1)
        red_duty = float(red_duty1)
        blue_duty = float(blue_duty1)
        rateSec = float(rateSec1)
        rateSec = 1/rateSec
        On = int(On1)
        
        print("green duty: " + green_duty1 + " red duty: " + red_duty1 + " blue duty: " + blue_duty1 + " On: " + On1)
        
        if On: 
            print("Changing the intensity with in the ON state")
            if curr_red < red_duty:
                while curr_red < red_duty:
                    curr_red = curr_red + rateSec
                    pwm_red.ChangeDutyCycle(curr_red)
                    print("increasing the red intensity, current red intensity is " + str(curr_red))
                    time.sleep(1)
            elif curr_red > red_duty:
                while curr_red > red_duty:
                    curr_red = curr_red - rateSec
                    if curr_red < 0:
                        pwm_red.ChangeDutyCycle(0)
                    else:
                        pwm_red.ChangeDutyCycle(curr_red)
                    print("decreasing the red intensity, current red intensity is " + str(curr_red))
                    time.sleep(1)
                
            if curr_blue < blue_duty:
                while curr_blue < blue_duty:
                    curr_blue = curr_blue + rateSec
                    pwm_blue.ChangeDutyCycle(curr_blue)
                    print("increasing the blue intensity, current blue intensity is " + str(curr_blue))
                    time.sleep(1)
            elif curr_blue > blue_duty:
                while curr_blue > blue_duty:
                    curr_blue = curr_blue - rateSec
                    if curr_blue < 0:
                        pwm_blue.ChangeDutyCycle(0)
                    else:
                        pwm_blue.ChangeDutyCycle(curr_blue)
                        
                    print("decreasing the blue intensity, current blue intensity is " + str(curr_blue))
                    time.sleep(1)
                
            if curr_green < green_duty:
                while curr_green < green_duty:
                    curr_green = curr_green + rateSec
                    pwm_green.ChangeDutyCycle(curr_green)
                    print("increasing the green intensity, current green intensity is " + str(curr_green))
                    time.sleep(1)
            elif curr_green > green_duty:
                while curr_green > green_duty:
                    curr_green = curr_green - rateSec
                    if curr_green < 0:
                        pwm_green.ChangeDutyCycle(0)
                    else:
                        pwm_green.ChangeDutyCycle(curr_green)
                    print("decreasing the green intensity, current green intensity is " + str(curr_green))
                    time.sleep(1)
                    
            curr_green = green_duty;
            curr_red = red_duty;
            curr_blue = blue_duty;
            pwm_green.ChangeDutyCycle(curr_green)
            pwm_blue.ChangeDutyCycle(curr_blue)
            pwm_red.ChangeDutyCycle(curr_red)
        else:
            print("Running the OFF state")
            while curr_red > 0:
                curr_red = curr_red - rateSec
                if curr_red < 0:
                    pwm_red.ChangeDutyCycle(0)
                else:
                    pwm_red.ChangeDutyCycle(curr_red)
                time.sleep(1)
            
            while curr_green > 0:
                curr_green = curr_green - rateSec
                if curr_green < 0:
                    pwm_green.ChangeDutyCycle(0)
                else:
                    pwm_green.ChangeDutyCycle(curr_green)
                time.sleep(1)
            
            while curr_blue > 0:
                curr_blue = curr_blue - rateSec
                if curr_blue < 0:
                    pwm_blue.ChangeDutyCycle(0)
                else:
                    pwm_blue.ChangeDutyCycle(curr_blue)
                time.sleep(1)            
        
            curr_red = 0
            curr_green = 0
            curr_blue = 0
        print("done")
        return "successfully received the parameter values and altered the intensities"
    
if __name__ == '__main__':
  app.run(host=ip, debug=False)
  zeroconf.close()



