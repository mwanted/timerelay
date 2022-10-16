from bottle import route, run, post, request
import serial
import time
import urllib
import json

def overallStatus(d):
	keys = ["mode","short_time","guard_time","delay_time"]
	a,b = True, False
	for key in keys:
		if key in d.keys():
			a = a & (d[key]["result"] == "success")
			b = b | (d[key]["result"] == "success")
	if a: return 'success'
	if not b: return 'failed'
	return 'partial'

def chat(command):
	data = dict()
	data["result"] = "failed"
	try:
		ser.reset_input_buffer()
		ser.write((command+'\n').encode('ASCII'))
		ser.flush()
		time.sleep(0.1)
		answer = ser.read(size=200).decode('ASCII')
	except serial.serialutil.SerialException as e:
		data["msg"] = str(e)
		return data
	for idx,string in enumerate(answer.splitlines()):
		if string == "":
			continue
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
	rm["msg"] = "channel and time fields must be specified" 
	return rm
	
@route('/api/v1/state')
def getState():
	return json.dumps(chat('sg'))

@route('/api/v1/properties')
def getProps():
	return json.dumps(chat('pg'))

@post('/api/v1/properties')
def setProps():
	rm = dict()
	wrreq = False
	try:
		data = json.loads(request.body.read().decode('utf-8'))
		if "channel" not in data.keys():
			return json.dumps(reportSyntxError(data))
		rm["channel"] = data["channel"]
		for key in data.keys():
			if key == "channel":    continue
			if key == "mode":       rm["mode"]       = chat('ps' + data["channel"] + "m" + str(data["mode"]))
			if key == "short_time": rm["short_time"] = chat('ps' + data["channel"] + "s" + str(data["short_time"]))
			if key == "guard_time": rm["guard_time"] = chat('ps' + data["channel"] + "g" + str(data["guard_time"]))
			if key == "delay_time": rm["delay_time"] = chat('ps' + data["channel"] + "d" + str(data["delay_time"]))
			if key == "write":      wrreq = True
		rm["result"] = overallStatus(rm)
		if wrreq: 
			if rm["result"] == 'success': 
				rm["write"] = chat('pw')
			else: 
				rm["write"] = {"result":"disabled"}
		return json.dumps(rm) 
	except json.JSONDecodeError as e:
		return json.dumps(reportJSONError(e))
		 

@post('/api/v1/state')
def setState():
	try:
		data = json.loads(request.body.read().decode('utf-8'))
		if all(elem in data.keys() for elem in ["channel","time"]):
			return json.dumps(chat('ss' + data["channel"] + str(data["time"])))
		return json.dumps(reportSyntxError(data))
	except json.JSONDecodeError as e:
		return json.dumps(reportJSONError(e))

if __name__ == '__main__':
	try: 
		ser = serial.Serial(
			port='COM3',
			baudrate=57600,
			timeout=1
		)
	except serial.serialutil.SerialException as e:
		print(e)
		exit()
	run(host='localhost', port=8088, debug=True)
	