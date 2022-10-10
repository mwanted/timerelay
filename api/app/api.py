from bottle import route, run, post, request
import serial
import time
import urllib
import json

ser = serial.Serial(
    port='COM3',
    baudrate=57600,
    timeout=1
)
print(ser.isOpen())

"""
A: guard_time: 2
A: short_time: 10
A: off_delay:  600
A: mode:       2
B: guard_time: 2
B: short_time: 10
B: off_delay:  600
B: mode:       2
"""


def chat(command):
	ser.reset_input_buffer()
	ser.write((command+'\n').encode('ASCII'))
	ser.flush()
	time.sleep(0.5)
	readed = ser.read(size=200)
	answer = readed.decode('ASCII')
	data = dict()
	data["result"] = "failed"
	data["channels"] = dict()
	for idx,string in enumerate(answer.splitlines()):
		if string == '':
			continue  
		if string == command:
			data["command"] = string
		if string == 'OK':
			data["result"] = "success"
		if string[1] == ':':
			if string[0] not in data["channels"].keys():
				data["channels"][string[0]] = dict()
			data["channels"][string[0]][string.split(':')[1].strip()] = string.split(':')[2].strip()
	return data


@route('/api/v1/state')
def getState():
	return chat('sg')

@route('/api/v1/properties')
def getProps():
	return chat('sg')

@post('/api/v1/properties')
def setProps():
	try:
		data = json.loads(request.body.read().decode('utf-8'))
		if "write" in data.keys():
			return chat('pw')
		if "mode" in data.keys():
			return chat('ps' + data["channel"] + "m" + data["mode"])
		if "short_time" in data.keys():
			return chat('ps' + data["channel"] + "s" + data["short_time"])
		if "guard_time" in data.keys():
			return chat('ps' + data["channel"] + "g" + data["guard_time"])
		if "delay_time" in data.keys():
			return chat('ps' + data["channel"] + "d" + data["delay_time"])
		return '{"result":"failed"}'
	except:
		return False
		 

@post('/api/v1/state')
def setState():
	try:
		data = json.loads(request.body.read().decode('utf-8'))
#		command = 'ss' + data["channel"] + data["time"]
		return chat('ss' + data["channel"] + data["time"])
	except:
		return False

run(host='localhost', port=8088, debug=True)