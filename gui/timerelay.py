#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#

import wx
from paho.mqtt import client as mqtt_client
import logging
import logging.config

connection = {
	"broker": '172.16.2.62',
	"port": 1883,
	"topic": "python/mqtt",
	"client_id": f'python-mqtt-gui',
	# username: 'emqx'
	# password: 'public'
	
	"channel": "A"
}

class mqttEvent(wx.PyEvent):
	"""Simple event to carry arbitrary result data."""
	def __init__(self, data):
		"""Init Result Event."""
		wx.PyEvent.__init__(self)
		self.SetEventType(EVT_MQTT_ID)
		self.data = data

class mqtt:
	def __init__(self,conninfo):
		self.topic_data = conninfo["topic"] + "-data"
		self.topic_commands = conninfo["topic"] + "-commands"
		self.client = mqtt_client.Client(conninfo["client_id"])
		self.client.enable_logger(logger)
		self.client.on_connect = self.on_connect
		self.client.on_message = self.on_message
		self.client.connect(conninfo["broker"], conninfo["port"])
		self.client.loop_start()
		self.client.subscribe(self.topic_data, qos=0)

	def on_connect(self, client, userdata, flags, rc):
		if rc == 0:
			print("Connected to MQTT Broker!")
		else:
			print("Failed to connect, return code %d\n", rc)	

	def on_message(self, client, userdata, message):
		try:
			wx.PostEvent(self.wxObject, mqttEvent(message.payload.decode('ASCII')))
		except ValueError as e:
			print(e)
		print("Received message '" + str(message.payload) + "' on topic '" + message.topic + "' with QoS " + str(message.qos))

	def publish(self,msg):
		result = self.client.publish(self.topic_commands, msg)
		status = result[0]		
		if status == 0:
			print(f"Send `{msg}` to topic `{self.topic_data}`")
		else:
			print(f"Failed to send message to topic {self.topic_data}")

	def __del__(self):
		self.client.loop_stop(force=True)


class MyFrame(wx.Frame):
	def __init__(self, *args, **kwds):
		# begin wxGlade: MyFrame.__init__
		kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
		wx.Frame.__init__(self, *args, **kwds)
		self.SetSize((300, 300))
		self.SetTitle(u"Реле вентилятора")

		self.panel_1 = wx.Panel(self, wx.ID_ANY)

		sizer_1 = wx.BoxSizer(wx.VERTICAL)

		sizer_3 = wx.StaticBoxSizer(wx.StaticBox(self.panel_1, wx.ID_ANY, u"Сейчас"), wx.HORIZONTAL)
		sizer_1.Add(sizer_3, 1, wx.ALL | wx.EXPAND, 4)

		self.currentState = currentState = wx.StaticText(self.panel_1, wx.ID_ANY, u"ВЫКЛ")
		currentState.SetForegroundColour(wx.Colour(255, 0, 0))
		sizer_3.Add(currentState, 0, wx.LEFT | wx.RIGHT, 12)

		label_6 = wx.StaticText(self.panel_1, wx.ID_ANY, u"осталось")
		sizer_3.Add(label_6, 0, 0, 0)

		self.currentSeconds = currentSeconds = wx.StaticText(self.panel_1, wx.ID_ANY, "0")
		sizer_3.Add(currentSeconds, 0, wx.LEFT | wx.RIGHT, 12)

		label_8 = wx.StaticText(self.panel_1, wx.ID_ANY, u"секунд")
		sizer_3.Add(label_8, 0, 0, 0)

		sizer_2 = wx.StaticBoxSizer(wx.StaticBox(self.panel_1, wx.ID_ANY, u"Запустить"), wx.HORIZONTAL)
		sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)

		grid_sizer_2 = wx.FlexGridSizer(2, 4, 0, 0)
		sizer_2.Add(grid_sizer_2, 1, wx.EXPAND, 0)

		label_3 = wx.StaticText(self.panel_1, wx.ID_ANY, u"на")
		label_3.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Segoe UI"))
		grid_sizer_2.Add(label_3, 0, wx.LEFT | wx.RIGHT, 12)

		self.inputSeconds = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.TE_CENTRE)
		self.inputSeconds.SetMinSize((70, 23))
		grid_sizer_2.Add(self.inputSeconds, 0, wx.RIGHT, 12)

		label_4 = wx.StaticText(self.panel_1, wx.ID_ANY, u"секунд")
		label_4.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Segoe UI"))
		grid_sizer_2.Add(label_4, 0, wx.RIGHT, 12)

		self.sendStateSeconds = wx.Button(self.panel_1, wx.ID_ANY, "Go!")
		grid_sizer_2.Add(self.sendStateSeconds, 0, 0, 0)
		self.sendStateSeconds.Bind(wx.EVT_BUTTON, self.onButton)


		label_2 = wx.StaticText(self.panel_1, wx.ID_ANY, u"на")
		label_2.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Segoe UI"))
		grid_sizer_2.Add(label_2, 0, wx.LEFT | wx.RIGHT, 12)

		self.inputMinutes = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.TE_CENTRE)
		self.inputMinutes.SetMinSize((70, 23))
		grid_sizer_2.Add(self.inputMinutes, 0, 0, 0)

		label_5 = wx.StaticText(self.panel_1, wx.ID_ANY, u"минут")
		label_5.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Segoe UI"))
		grid_sizer_2.Add(label_5, 0, 0, 0)

		self.sendStateMinutes = wx.Button(self.panel_1, wx.ID_ANY, "Go!")
		grid_sizer_2.Add(self.sendStateMinutes, 0, 0, 0)
		self.sendStateMinutes.Bind(wx.EVT_BUTTON, self.onButton)

		sizer_5 = wx.StaticBoxSizer(wx.StaticBox(self.panel_1, wx.ID_ANY, u"Настроить"), wx.HORIZONTAL)
		sizer_1.Add(sizer_5, 1, wx.EXPAND, 0)

		grid_sizer_1 = wx.FlexGridSizer(5, 3, 0, 0)
		sizer_5.Add(grid_sizer_1, 1, wx.EXPAND, 0)

		label_10 = wx.StaticText(self.panel_1, wx.ID_ANY, u"Защитное время:")
		grid_sizer_1.Add(label_10, 0, 0, 0)

		self.inputGuardTime = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
		self.inputGuardTime.SetMinSize((70, 23))
		grid_sizer_1.Add(self.inputGuardTime, 0, 0, 0)

		label_11 = wx.StaticText(self.panel_1, wx.ID_ANY, u"секунд")
		grid_sizer_1.Add(label_11, 0, 0, 0)

		label_12 = wx.StaticText(self.panel_1, wx.ID_ANY, u"Короткое время:")
		grid_sizer_1.Add(label_12, 0, 0, 0)

		self.inputShortTime = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
		self.inputShortTime.SetMinSize((70, 23))
		grid_sizer_1.Add(self.inputShortTime, 0, 0, 0)

		label_13 = wx.StaticText(self.panel_1, wx.ID_ANY, u"секунд")
		grid_sizer_1.Add(label_13, 0, 0, 0)

		label_14 = wx.StaticText(self.panel_1, wx.ID_ANY, u"Рабочее время:")
		grid_sizer_1.Add(label_14, 0, 0, 0)

		self.inputDelayTime = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
		self.inputDelayTime.SetMinSize((70, 23))
		grid_sizer_1.Add(self.inputDelayTime, 0, 0, 0)

		label_15 = wx.StaticText(self.panel_1, wx.ID_ANY, u"секунд")
		grid_sizer_1.Add(label_15, 0, 0, 0)

		label_1 = wx.StaticText(self.panel_1, wx.ID_ANY, u"Режим")
		grid_sizer_1.Add(label_1, 0, 0, 0)

		self.currentMode = wx.Button(self.panel_1, wx.ID_ANY, u"Авто")
		self.currentMode.SetMinSize((70, 23))
		self.currentMode.Bind(wx.EVT_BUTTON, self.onModeButton)
		grid_sizer_1.Add(self.currentMode, 0, 0, 0)

		grid_sizer_1.Add((0, 0), 0, 0, 0)

		grid_sizer_1.Add((0, 0), 0, 0, 0)

		self.sendProps = wx.Button(self.panel_1, wx.ID_ANY, u"Отпраить")
		grid_sizer_1.Add(self.sendProps, 0, wx.ALIGN_RIGHT, 0)
		self.sendProps.Bind(wx.EVT_BUTTON, self.onSendButton)

		self.writeProps = wx.Button(self.panel_1, wx.ID_ANY, u"Записать")
		grid_sizer_1.Add(self.writeProps, 0, 0, 0)
		self.writeProps.Bind(wx.EVT_BUTTON, self.onWriteButton)

		self.panel_1.SetSizer(sizer_1)

		self.Layout()
		# end wxGlade
		
	def onModeButton(self, event):
		pmode = [u"Авто",u"Вкл",u"Выкл"]
		btn = event.GetEventObject()
		idx = pmode.index(btn.GetLabel())+1
		if idx >= len(pmode): idx = 0
		btn.SetLabel(pmode[idx])
		
	def onSendButton(self, event):
		pmode = [u"Авто",u"Вкл",u"Выкл"]
		mode = pmode.index(self.currentMode.GetLabel())
		guardTime = self.inputGuardTime.GetValue()
		shortTime = self.inputShortTime.GetValue()
		delayTime = self.inputDelayTime.GetValue()
		self.mqtt.publish("ps" + connection["channel"] + "m" + str(mode))
		self.mqtt.publish("ps" + connection["channel"] + "g" + str(guardTime))
		self.mqtt.publish("ps" + connection["channel"] + "s" + str(shortTime))
		self.mqtt.publish("ps" + connection["channel"] + "d" + str(delayTime))
		self.mqtt.publish("pg")
		
	def onWriteButton(self, event):
		self.mqtt.publish("pw")
		
	def onButton(self, event):
		"""<br/>	Runs the thread<br/>	"""
		btn = event.GetEventObject()
		if btn == self.sendStateSeconds:
			data = int(self.inputSeconds.GetValue())
			self.inputSeconds.SetValue("")
			print(data,"seconds!")
		if btn == self.sendStateMinutes:
			data = int(self.inputMinutes.GetValue())*60
			self.inputMinutes.SetValue("")
			print(data,"seconds!")
		self.mqtt.publish("ss" + connection["channel"] + str(data));

	def onMQTTMessage(self,msg):
		def displayState(self,state):
			self.currentSeconds.SetLabel(state[0])
			if state[1] == "1":
				self.currentState.SetForegroundColour(wx.Colour(0, 255, 0))
				self.currentState.SetLabel(u"ВКЛ")
			else:
				self.currentState.SetForegroundColour(wx.Colour(255, 0, 0))
				self.currentState.SetLabel(u"ВЫКЛ")
			
		def displayProperties(self,props):
			print("props",props)
			pmode = [u"Авто",u"Вкл",u"Выкл"]
			self.inputGuardTime.SetValue(props[0])
			self.inputShortTime.SetValue(props[1])
			self.inputDelayTime.SetValue(props[2])
			self.currentMode.SetLabel(pmode[int(props[3])])
		
		data = msg.data
		if data == "OK": 
			pass
		elif data == "ERROR": 
			logger.debug(f"Receive ERROR message from device`")
		else: 
			parsed = data.split(",")
			if parsed[1] == connection["channel"]:
				if parsed[0] == "P":
					displayProperties(self,parsed[2:])
				if parsed[0] == "S":
					displayState(self,parsed[2:])


class MyApp(wx.App):
	def OnInit(self):
		self.frame = MyFrame(None, wx.ID_ANY, "")
		self.frame.mqtt = mqtt(connection)
		self.frame.mqtt.wxObject = self.frame

		self.frame.Connect(-1, -1, EVT_MQTT_ID, self.frame.onMQTTMessage)

		self.SetTopWindow(self.frame)
		self.frame.Show()
		
		self.frame.mqtt.publish("pg");
		return True

# end of class MyApp

if __name__ == "__main__":
	global EVT_MQTT_ID
	logging.config.fileConfig('logging.conf')
	logger = logging.getLogger("mqtt")

	EVT_MQTT_ID = wx.NewIdRef(count=1)

	app = MyApp(0)
	app.MainLoop()
	app.frame.mqtt.client.loop_stop()
