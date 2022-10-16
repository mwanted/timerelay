import os, sys, unittest
import fakeSerial as serial
from boddle import boddle
import json

sys.path.insert(0, os.path.abspath('../app'))

import api

fakeSerial = serial.Serial(0)

class Test1_Chat(unittest.TestCase):
	def setUp(self):
		api.ser = fakeSerial
	def testChat_pw(self):
		self.assertEqual(str(api.chat("pw")), "{'result': 'success', 'command': 'pw'}")
	def testChat_ssa10(self):
		self.assertEqual(str(api.chat("ssa10")), "{'result': 'success', 'command': 'ssa10'}")
	def testChat_ssA10(self):
		self.assertEqual(str(api.chat("ssA10")), "{'result': 'success', 'command': 'ssA10'}")
	def testChat_ssa12(self):
		self.assertEqual(str(api.chat("ssa12")), "{'result': 'failed', 'command': 'ssa12'}")
	def testChat_sg(self):
		self.assertEqual(str(api.chat("sg")), "{'result': 'success', 'command': 'sg', 'channels': {'A': {'off_delay': '0', 'mode': '0', 'count': '0'}, 'B': {'off_delay': '0', 'mode': '0', 'count': '0'}}}")
	def testChat_psAm0(self):
		self.assertEqual(str(api.chat("psAm0")), "{'result': 'success', 'command': 'psAm0'}")
	def testChat_wrongAnswer(self):
		self.assertEqual(str(api.chat("wrong")), "{'result': 'failed', 'command': 'wrong'}")
	def testChat_wrongAnswer2(self):
		self.assertEqual(str(api.chat("wrong2")), "{'result': 'failed', 'command': 'wrong2'}")

class Test2_Utilities(unittest.TestCase):
	def test_overallStatus_success(self):
		d = json.loads('{"channel": "A",\
                 "mode":       {"result": "success", "command": "psAm0"},\
                 "short_time": {"result": "success", "command": "psAs2"},\
                 "guard_time": {"result": "success", "command": "psAg20"},\
                 "delay_time": {"result": "success", "command": "psAd600"}}')
		self.assertEqual(api.overallStatus(d),'success')
		d = json.loads('{"channel": "A",\
                 "mode":       {"result": "success", "command": "psAm0"},\
                 "guard_time": {"result": "success", "command": "psAg20"},\
                 "delay_time": {"result": "success", "command": "psAd600"}}')
		self.assertEqual(api.overallStatus(d),'success')
		d = json.loads('{"channel": "A",\
                 "guard_time": {"result": "success", "command": "psAg20"},\
                 "delay_time": {"result": "success", "command": "psAd600"}}')
		self.assertEqual(api.overallStatus(d),'success')
	def test_overallStatus_failed(self):
		d = json.loads('{"channel": "A",\
                 "mode":       {"result": "failed", "command": "psAm0"},\
                 "short_time": {"result": "failed", "command": "psAs2"},\
                 "guard_time": {"result": "failed", "command": "psAg20"},\
                 "delay_time": {"result": "failed", "command": "psAd600"}}')
		self.assertEqual(api.overallStatus(d),'failed')
		d = json.loads('{"channel": "A",\
                 "mode":       {"result": "failed", "command": "psAm0"},\
                 "delay_time": {"result": "failed", "command": "psAd600"}}')
		self.assertEqual(api.overallStatus(d),'failed')
	def test_overallStatus_partial(self):
		d = json.loads('{"channel": "A",\
                 "mode":       {"result": "success", "command": "psAm0"},\
                 "short_time": {"result": "failed", "command": "psAs2"},\
                 "guard_time": {"result": "success", "command": "psAg20"},\
                 "delay_time": {"result": "success", "command": "psAd600"}}')
		self.assertEqual(api.overallStatus(d),'partial')
		d = json.loads('{"channel": "A",\
                 "mode":       {"result": "success", "command": "psAm0"},\
                 "short_time": {"result": "failed", "command": "psAs2"},\
                 "guard_time": {"result": "failed", "command": "psAg20"},\
                 "delay_time": {"result": "success", "command": "psAd600"}}')
		self.assertEqual(api.overallStatus(d),'partial')


class Test3_Api(unittest.TestCase):
	def setUp(self):
		api.ser = fakeSerial
	def testStateGet(self):
		with boddle():
			self.assertEqual(api.getState(), '{"result": "success", "command": "sg", "channels": {"A": {"off_delay": "0", "mode": "0", "count": "0"}, "B": {"off_delay": "0", "mode": "0", "count": "0"}}}')
	def testStateSet(self):
		with boddle(params={'wrong':'parameter'}):
			self.assertEqual(api.setState(), '{"result": "failed", "msg": "Expecting value", "pos": 0, "doc": "wrong=parameter"}')
		with boddle(method='POST',body=json.dumps({"channel":"A"})):
			self.assertEqual(api.setState(), '{"result": "failed", "msg": "channel and time fields must be specified"}')
		with boddle(method='POST',body=json.dumps({"channel":"A","time":"10"})):
			self.assertEqual(api.setState(), '{"result": "success", "command": "ssA10"}')
	def testPropertiesGet(self):
		with boddle():
			self.assertEqual(api.getProps(), '{"result": "success", "command": "pg", "channels": {"A": {"guard_time": "2", "short_time": "10", "off_delay": "600", "mode": "2"}, "B": {"guard_time": "2", "short_time": "10", "off_delay": "600", "mode": "2"}}}')
	def testPropertiesSet(self):
		with boddle():
			self.assertEqual(api.setProps(), '{"result": "failed", "msg": "Expecting value", "pos": 0, "doc": ""}')
		with boddle(method='POST',body=json.dumps({"channel":"A"})):
			self.assertEqual(api.setProps(), '{"channel": "A", "result": "success"}')
		with boddle(method='POST',body=json.dumps({"channel":"A","write":""})):
			self.assertEqual(api.setProps(), '{"channel": "A", "result": "success", "write": {"result": "success", "command": "pw"}}')
		with boddle(method='POST',body=json.dumps({"channel":"A","mode":"0"})):
			self.assertEqual(api.setProps(), '{"channel": "A", "mode": {"result": "success", "command": "psAm0"}, "result": "success"}')
		with boddle(method='POST',body=json.dumps({"channel":"A","mode":"0","short_time":"2","guard_time":"20","delay_time":"600"})):
			self.assertEqual(api.setProps(), '{"channel": "A", "mode": {"result": "success", "command": "psAm0"}, "short_time": {"result": "success", "command": "psAs2"}, "guard_time": {"result": "success", "command": "psAg20"}, "delay_time": {"result": "success", "command": "psAd600"}, "result": "success"}')
		with boddle(method='POST',body=json.dumps({"channel":"A","mode":"1","short_time":"2","guard_time":"20","delay_time":"600"})):
			self.assertEqual(api.setProps(), '{"channel": "A", "mode": {"result": "failed", "command": "psAm1"}, "short_time": {"result": "success", "command": "psAs2"}, "guard_time": {"result": "success", "command": "psAg20"}, "delay_time": {"result": "success", "command": "psAd600"}, "result": "partial"}')
		with boddle(method='POST',body=json.dumps({"channel":"A","write":"","mode":"1","short_time":"2","guard_time":"20","delay_time":"600"})):
			self.assertEqual(api.setProps(), '{"channel": "A", "mode": {"result": "failed", "command": "psAm1"}, "short_time": {"result": "success", "command": "psAs2"}, "guard_time": {"result": "success", "command": "psAg20"}, "delay_time": {"result": "success", "command": "psAd600"}, "result": "partial", "write": {"result": "disabled"}}')


if __name__ == "__main__":
	unittest.main()