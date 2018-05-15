Email

Faraz Khan: farazk@vt.edu

mongodb, server, zeroconf
server, customAPI,vled.py, zeroconf

Unusual Configuration: N/A

Curl Commands

custom - use example.py
Add    - use example.py
Weather - use example.py

canvas - get: curl -u admin:pass http://<IP_ADDRESS>:5000/canvas/
		 get: curl -u admin:pass http://<IP_ADDRESS>:5000/canvas/download?filename=f.txt
		 post: curl -u admin:pass -F "file=@testing.txt" -F "filename=testing.txt" -X POST http://<IP_ADDRESS>:5000/canvas/upload

led    - get: curl -u admin:pass http://<IP_ADDRESS>:5000/led
		 post: curl -u admin:pass -d "red=0&green=0&blue=50&rate=0.1&state=0" http://<IP_ADDRESS>:5000/led

