from flask import Flask, request, jsonify
import json
import requests
from pymongo import MongoClient
from canvas_token import *
from six.moves import input  
from zeroconf import ServiceBrowser, Zeroconf
import socket
from time import sleep

#setup a list to hold zeroconf() networks
networks = list()

#get the IP of the Pi. This method will ensure the ip is not "127.0.0.1". Requires Internet..
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8",80))
ip_addr = s.getsockname()[0]
s.close

#Create a listener object to browse for new connections    
class MyListener(object):  
    def remove_service(self, zeroconf, type, name):
        networks.pop()
        print("Flask network removed!")
        #Unfortunately we have no way to run this, so networks removed
        #While operating will not be removed from our network list

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if (str(info.server) == "led.local." or str(info.server) == "custom.local."):
            networks.append([socket.inet_ntoa(info.address), info.port, info.server])
            print("Flask network found! Discovered " + str(info.server) +" on " + socket.inet_ntoa(info.address) + ":" + str(info.port))

#Search for new networks while the server runs
zeroconf = Zeroconf()  
listener = MyListener()  
browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
sleep(1)

# Flask
app = Flask(__name__)
# MongoDB connection
client = MongoClient("localhost", 27017)
db = client.test_keys

@app.route('/custom/add', methods=['GET', 'POST'])
def custom_add():
        #Basic HTTP Auth
        authen = request.authorization
        usr = authen.username
        psw = authen.password
        if db.test_keys.find({usr:psw}).count() > 0:
            result = "Found"
        else:
            return "Bad Login\n", 403, {"Custom" : "Header"}
        #Check if the network exists in the network list
        if (len(networks) == 0):
            return "Network not Found\n", 503, {"Custom" : "Header"}
        elif (len(networks) == 1 and networks[0][2] != "custom.local."):
            return "Network not Found\n", 503, {"Custom" : "Header"}

        if request.method == 'GET':
            #Check both elements of the list, assumed the network exists in one element
            if networks[0][2] == "custom.local.":
                r = requests.get(("http://" + str(networks[0][0]) + ":" + str(networks[0][1]) + "/add"))
            elif networks[1][2] == "custom.local.":
                r = requests.get(("http://" + str(networks[1][0]) + ":" + str(networks[1][1]) + "/add"))
            
            return r.content, 200, {"Content" : "Header"}
        if request.method == 'POST':
          val1 = request.form["val1"]
          val2 = request.form["val2"]
          data_pack = {"val1":val1, "val2":val2}
          if networks[0][2] == "custom.local.":
            r = requests.post(("http://" + str(networks[0][0]) + ":" + str(networks[0][1]) + "/add"), json=data_pack)
          elif networks[1][2] == "custom.local.":
            r = requests.post(("http://" + str(networks[1][0]) + ":" + str(networks[1][1]) + "/add"), json=data_pack)  
          return "Succesfully Posted", 200, {"Content" : "Header"}

@app.route('/custom/weather', methods=['GET', 'POST'])
def custom_weather():
  authen = request.authorization
  usr = authen.username
  psw = authen.password
  if db.test_keys.find({usr:psw}).count() > 0:
    result = "Found"
  else:
    return "Bad Login\n", 403, {"Custom" : "Header"}
  if (len(networks) == 0):
    return "Network not Found\n", 503, {"Custom" : "Header"}
  elif (len(networks) == 1 and networks[0][2] != "custom.local."):
    return "Network not Found\n", 503, {"Custom" : "Header"} 

  ip = '192.168.0.112'
  url = 'http://%s:%s/%s' % (ip, '5000', 'weather')
  if request.method == 'GET':
    if networks[0][2] == "custom.local.":
        r = requests.get(("http://" + str(networks[0][0]) + ":" + str(networks[0][1]) + "/weather"))
    elif networks[1][2] == "custom.local.":
        r = requests.get(("http://" + str(networks[1][0]) + ":" + str(networks[1][1]) + "/weather"))        
    return r.content, 200, {"Content": "Header"}

  if request.method == 'POST':
    location = request.form["location"]
    data_pack = {"location":location}
    if networks[0][2] == "custom.local.":
        url = ("http://" + str(networks[0][0]) + ":" + str(networks[0][1]) + "/weather")
    elif networks[1][2] == "custom.local.":
        url = ("http://" + str(networks[1][0]) + ":" + str(networks[1][1]) + "/weather")
    r = requests.post(url, json=data_pack)
    return "Successfully Posted", 200, {"Content" : "Header"}
 
@app.route('/led', methods=['GET', 'POST'])
def ledstatus():
    authen = request.authorization
    usr = authen.username
    psw = authen.password
    if db.test_keys.find({usr:psw}).count() > 0:
        result = "Found"
    else:
        return "Bad Login\n", 403, {"Content" : "Header"}
    if request.method == 'GET' and len(networks) == 0:
        return "Network not Found\n", 503, {"Content" : "Header"}
    elif request.method == 'GET' and len(networks) == 1 and networks[0][2] != "led.local.":
        return "Network not found\n", 503, {"Content" : "Header"}
    elif request.method == 'GET':
        if networks[0][2] == "led.local.":
            r1 = requests.get(("http://" + str(networks[0][0]) + ":" + str(networks[0][1]) + "/led"))
        elif networks[1][2] == "led.local.":
            r1 = requests.get(("http://" + str(networks[1][0]) + ":" + str(networks[1][1]) + "/led"))
        data = r1.json()
        return json.dumps(data), 200, {"Content" : "Header"}
    if request.method == 'POST':
        green = request.form["green"]
        red = request.form["red"]
        blue = request.form["blue"]
        rate = request.form["rate"]
        state = request.form["state"]
        outti = {"red":red, "green":green, "blue":blue, "rate":rate, "state":state}
        if len(networks) == 0:
            return "Network not Found\n", 503, {"Content" : "Header"}
        elif len(networks) == 1 and networks[0][2] != "led.local.":
            return "Network not Found\n", 503, {"Content" : "Header"}
        if networks[0][2] == "led.local.":
            r = requests.post(("http://" + str(networks[0][0]) + ":" + str(networks[0][1]) + "/led"), json=outti)
        elif networks[1][2] == "led.local.":
            r = requests.post(("http://" + str(networks[1][0]) + ":" + str(networks[1][1]) + "/led"), json=outti)
            
        return "Successfully Posted\n", 200, {"Content" : "Header"}

@app.route('/canvas', methods=['GET'])
def canvas():
  authen = request.authorization
  usr = authen.username
  psw = authen.password
  if db.test_keys.find({usr:psw}).count() > 0:
    result = "Found"
  else:
    return "Bad Login\n", 403, {"Content" : "Header"}  
  api_url = 'https://canvas.vt.edu/api/v1/groups/52701/files?only[]=names'

  # Set up a session
  session = requests.Session()
  session.headers = {'Authorization': 'Bearer %s' % canvas_token}

  r = session.get(api_url)
  r.raise_for_status()
  r = r.json()

  return r, 200, {"Content" : "Header"}

@app.route('/canvas/upload', methods=['POST'])
def upload():
  authen = request.authorization
  usr = authen.username
  psw = authen.password
  if db.test_keys.find({usr:psw}).count() > 0:
    result = "Found"
  else:
    return "Bad Login\n", 403, {"Content":"Header"}
  api_url = 'https://canvas.vt.edu/api/v1/groups/52701/files'
  
  # Set up a session
  session = requests.Session()
  session.headers = {'Authorization': 'Bearer %s' % canvas_token}

  fname = request.form['filename']
  file = request.files['file']
  payload = {}
  payload['name'] = fname
  payload['parent_folder_path'] = '/'
  r = session.post(api_url, data=payload)
  r.raise_for_status()
  r = r.json()

  payload = list(r['upload_params'].items())

  
  payload.append((u'file', file))
  r = requests.post(r['upload_url'], files=payload)
  r.raise_for_status()
  r = r.json()

  return "Successfully Posted", 200, {"Content":"Header"}

@app.route('/canvas/download', methods=['GET'])
def download():
  fname = request.args.get('filename')
  authen = request.authorization
  usr = authen.username
  psw = authen.password
  if db.test_keys.find({usr:psw}).count() > 0:
    result = "Found"
  else:
    return "Bad Login\n", 403, {"Content": "Header"}
  api_url = 'https://canvas.vt.edu/api/v1/groups/52701/files?search_term=%s' % fname

  # Set up a session
  session = requests.Session()
  session.headers = {'Authorization': 'Bearer %s' % canvas_token}

  r = session.get(api_url)
  r.raise_for_status()
  r = r.json()
  #print (r[0]['url']);
  #print (r)
  down_url = r[0]['url']
  r = requests.get(down_url)

  with open('./download-%s' % fname, 'wb') as f:
    f.write(r.content)
  
  return ('Successfully Downloaded\nFilename:%s\n' % fname), 200, {"Content" : "Header"}
 
if __name__ == '__main__':
  app.run(host=ip_addr, debug=False)
  zeroconf.close()
