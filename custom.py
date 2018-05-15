#example Flask web service code

from flask import Flask, request
import requests
import socket
from zeroconf import ServiceBrowser, ServiceInfo, ServiceStateChange, Zeroconf

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
local_ip = s.getsockname()[0]


## ZEROCONF SETUP

desc = {'path': '/custom'}
info = ServiceInfo("_http._tcp.local.",
			"custom._http._tcp.local.",
			socket.inet_aton(local_ip), 5000, 0, 0,
			desc, "custom.local.")

zeroconf = Zeroconf()
print ('Pi is registered as a service')
zeroconf.register_service(info)

## ZEROCONF SETUP

location = 'New York'
sum = 0
app = Flask(__name__)

@app.route('/add', methods=['GET', 'POST'])
def add():
	global sum
	if request.method == 'POST':
		data_rec = request.json
		val1 = data_rec['val1']
		val2 = data_rec['val2']
		sum = float(val1) + float(val2)
		return ('\nHTTP <200> OK\n')

	if request.method == 'GET':
		return ('%s%s%s' % ('Sum: ', str(sum), '\n'))

@app.route('/weather', methods=['GET', 'POST'])
def weather():
	global location
	url = 'http://wttr.in/%s' % location
	if request.method == 'GET':
		r = requests.get(url)
		return (r.content)
	if request.method == 'POST':
		loc_rec = request.json
		location = loc_rec['location']
		return ('HTTP <200> OK\n')
if __name__ == "__main__":
    app.run(host=local_ip, debug=False)
    zeroconf.close()
