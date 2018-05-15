"""
This script will be used to demonstrate your custom API.

You should be using python requests.

At least two POST requests should be demonstrated.
At least two GET requests should be demonstrated.

Print all HTTP Client Request Headers and Bodies
Print HTTP Server Response Headers and Bodies

If you are doing some kind of file uploading/downloading and it can be verified by a file,
the initial request and response should be printed but the subsequent requests and responses do not need to be printed.

Your API can be as basic or as complicated as you want it to be 
as long as none of your APIs replicate functionality already defined in the assignment.

Remember to also create a "custom.pdf" API Documentation. 
Use the Canvas/LED API documentation as a template/example for how you should format your API documentation.
"""

import requests
import time
from requests.auth import HTTPBasicAuth

ip = input('Enter Server IP Address: ')

#POST location for weather, in this case paris
r = requests.post('http://%s:5000/custom/weather' % ip, auth=('faraz', '7141'), data={'location':'paris'})
print('POST REQUEST - Weather')
print(r)
print('')

time.sleep(2)
print('GET REQUEST - Weather')
time.sleep(1)
#GET Weather request, from specfied POST location, default=NYC
r = requests.get('http://%s:5000/custom/weather' % ip, auth=('admin', 'pass'))
print (r.text)
print('')
time.sleep(2)

#POST request for add, post 2 values that need to be added
print('POST REQUEST - Add')
r = requests.post('http://%s:5000/custom/add' % ip, auth=('admin', 'pass'), data={'val1':'69.5', 'val2':'88.3'})
print(r)
print('')
time.sleep(2)

#GET add request, from specified POST values
print('GET REQUEST - Add')
r = requests.get('http://%s:5000/custom/add' % ip, auth=('admin', 'pass'))
print(r.text)

time.sleep(1)

print('EXAMPLES FINISHED')




