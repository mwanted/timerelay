from bottle import route, run, post, request
import serial
import time
import urllib
import json


try: 
	ser = serial.Serial(
		port='COM3',
		baudrate=57600,
		timeout=1
	)
except serial.serialutil.SerialException as e:
	print(e)
	exit()
	
def chat(command):
	try:
		ser.reset_input_buffer()
		ser.write((command+'\n').encode('ASCII'))
		ser.flush()
		time.sleep(0.1)
		answer = ser.read(size=200).decode('ASCII')
	except serial.serialutil.SerialTimeoutException as e:
		print(e)
		exit()
	data = dict()
	data["result"] = "failed"
	for idx,string in enumerate(answer.splitlines()):
		if string == command:
			data["command"] = string
		if string == 'OK':
			data["result"] = "success"
		if string[1] == ':':
			if "channels" not in data: data["channels"] = dict()
			if string[0] not in data["channels"].keys():
				data["channels"][string[0]] = dict()
			data["channels"][string[0]][string.split(':')[1].strip()] = string.split(':')[2].strip()
	return data

def reportJSONError(e):
	rm = dict()
	rm["result"] = "failed"
	rm["msg"] = e.msg 
	rm["pos"] = e.pos 
	rm["doc"] = e.doc
	return rm

def reportSyntxError(e):
	rm = dict()
	rm["result"] = "failed"
	rm["msg"] = "channel field must be specified" 
	return rm
	
@route('/api/v1/state')
def getState():
	return chat('sg')

@route('/api/v1/properties')
def getProps():
	return chat('pg')

@post('/api/v1/properties')
def setProps():
	rm = dict()
	try:
		data = json.loads(request.body.read().decode('utf-8'))
		if "channel" not in data.keys():
			return reportSyntxError(data)
		rm["channel"] = data["channel"]
		for key in data.keys():
			if key == "channel":    continue
			if key == "mode":       rm["mode"]       = chat('ps' + data["channel"] + "m" + str(data["mode"]))
			if key == "short_time": rm["short_time"] = chat('ps' + data["channel"] + "s" + str(data["short_time"]))
			if key == "guard_time": rm["guard_time"] = chat('ps' + data["channel"] + "g" + str(data["guard_time"]))
			if key == "delay_time": rm["delay_time"] = chat('ps' + data["channel"] + "d" + str(data["delay_time"]))
			if key == "write":      rm["write"]      = chat('pw')
		rm["result"] = "success"
		return rm 
	except json.JSONDecodeError as e:
		return reportJSONError(e)
		 

@post('/api/v1/state')
def setState():
	try:
		data = json.loads(request.body.read().decode('utf-8'))
		if "channel" not in data.keys():
			return reportSyntxError(data)
		return chat('ss' + data["channel"] + str(data["time"]))
	except json.JSONDecodeError as e:
		return reportJSONError(e)

run(host='localhost', port=8088, debug=True)