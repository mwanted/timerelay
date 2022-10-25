from paho.mqtt import client as mqtt_client
import time
import logging
import logging.config
import serial
import configparser

configFile = "ser2mqtt.conf"

"""connection = {
	"broker": '172.16.2.62',
	"port": 1883,
	"topic": "python/mqtt",
	"client_id": f'python-mqtt-serial',
	# username: 'emqx'
	# password: 'public'
	"serial_port": "COM3",
	"serial_speed": "57600"
}"""

def on_connect(client, userdata, flags, rc):
	if rc == 0:
		logger.info("Connected to MQTT Broker!")
	else:
		logger.error("Filed to connected to MQTT Broker!")
		exit()	


def on_message(client, userdata, message):
	try:
		serial_write(message.payload)
		logger.debug("Received message '" + str(message.payload) + "' on topic '" + message.topic + "' with QoS " + str(message.qos))
	except ValueError as e:
		logger.error(e)
	

def send_data(msg):
	topic = config["mqtt"]["parenttopic"] + "data"
	result = mqtt.publish(topic, msg)
	status = result[0]		
	if status == 0:
		logger.debug(f"Send `{msg}` to topic `{topic}`")
	else:
		logger.error(f"Failed to send message to topic {topic}")
		
def serial_write(chars):
	logger.debug(f"Writing chars '{str(chars)}' to {config['serial']['port']}")
	ser.write(chars)
	ser.write("\r\n".encode('ASCII'))


if __name__ == "__main__": 
	logging.config.fileConfig(configFile)
	logger = logging.getLogger("ser2mqtt")
	config = configparser.ConfigParser()
	config.read(configFile)
	try:
		assert "parenttopic" in config["mqtt"], "\"parenttopic\" is not defined in section [mqtt]"
		assert "broker" in config["mqtt"], "\"broker\" is not defined in section [mqtt]"
		assert "port" in config["mqtt"], "\"port\" is not defined in section [mqtt]"
		assert "channel" in config["mqtt"], "\"channel\" is not defined in section [mqtt]"
		assert "client_id" in config["mqtt"], "\"client_id\" is not defined in section [mqtt]"
	except Exception as e:
		logger.critical(e)
		exit()

	mqtt = mqtt_client.Client(config["mqtt"]["client_id"])
	mqtt.on_connect = on_connect
	mqtt.on_message = on_message
	mqtt.enable_logger(logger)
	mqtt.connect(config["mqtt"]["broker"], int(config["mqtt"]["port"]))
	mqtt.loop_start()
	mqtt.subscribe(config["mqtt"]["parenttopic"] + "commands", qos=0)
	ser = serial.Serial(config["serial"]["port"], config["serial"]["speed"])

	while True:
		try:
			data = ser.readline().decode('ascii').strip()
			logger.debug(f"Readed chars '{str(data)}' from {config['serial']['port']}")
			if data == "Starting... Done.":
				serial_write(b"mm")
			send_data(data)
		except UnicodeDecodeError:
			pass
	mqtt.loop_stop()
