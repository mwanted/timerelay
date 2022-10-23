from paho.mqtt import client as mqtt_client
import time
import logging
import logging.config
import serial

logging.config.fileConfig('logging.conf')
logger = logging.getLogger("mqtt")


connection = {
	"broker": '172.16.2.62',
	"port": 1883,
	"topic": "python/mqtt",
	"client_id": f'python-mqtt-serial',
	# username: 'emqx'
	# password: 'public'
	"serial_port": "COM3",
	"serial_speed": "57600"
}

def on_connect(client, userdata, flags, rc):
	if rc == 0:
		logger.info("Connected to MQTT Broker!")
	else:
		logger.error("Connected to MQTT Broker!")	


def on_message(client, userdata, message):
	try:
		serial_write(message.payload)
	except ValueError as e:
		pass
	logger.debug("Received message '" + str(message.payload) + "' on topic '" + message.topic + "' with QoS " + str(message.qos))

def send_data(msg):
	topic = connection["topic"] + "-data"
	result = mqtt.publish(topic, msg)
	status = result[0]		
	if status == 0:
		logger.debug(f"Send `{msg}` to topic `{topic}`")
	else:
		logger.debug(f"Failed to send message to topic {topic}")
		
def serial_write(chars):
	logger.debug(f"Writing chars '{str(chars)}' to {connection['serial_port']}")
	ser.write(chars)
	ser.write("\r\n".encode('ASCII'))

mqtt = mqtt_client.Client(connection["client_id"])
mqtt.on_connect = on_connect
mqtt.on_message = on_message
mqtt.enable_logger(logger)
mqtt.connect(connection["broker"], connection["port"])
mqtt.loop_start()
mqtt.subscribe(connection["topic"] + "-commands", qos=0)
ser = serial.Serial(connection["serial_port"], connection["serial_speed"])

while True:
	try:
		data = ser.readline().decode('ascii').strip()
		logger.debug(f"Readed chars '{str(data)}' from {connection['serial_port']}")
		if data == "Starting... Done.":
			serial_write(b"mm")
		send_data(data)
	except UnicodeDecodeError:
		pass

mqtt.loop_stop()
