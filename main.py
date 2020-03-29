import ntptime
import ujson
import utime
import config
import machine
import gc
import esp32
from machine import UART, I2C, Pin
from letters import characters

from third_party import string
from third_party import rsa
from umqtt.simple import MQTTClient
from ubinascii import b2a_base64

from uPySensors.psma003 import psma003
from uPySensors.bme680 import BME680
import neopixel

np = neopixel.NeoPixel(Pin(27), 25)
device_uart = UART(1, baudrate=9600)
device_i2c = -1

bme_sensor = BME680(device_i2c, config.device_config)
psm_sensor = psma003(device_uart, config.device_config)

def on_message(topic, message):
    print((topic,message))

def b42_urlsafe_encode(payload):
    return string.translate(b2a_base64(payload)[:-1].decode('utf-8'),{ ord('+'):'-', ord('/'):'_' })

def create_jwt(project_id, private_key, algorithm, token_ttl):
    print("Creating JWT...")
    private_key = rsa.PrivateKey(*private_key)

    # Epoch_offset is needed because micropython epoch is 2000-1-1 and unix is 1970-1-1. Adding 946684800 (30 years)
    epoch_offset = 946684800
    claims = {
            # The time that the token was issued at
            'iat': utime.time() + epoch_offset,
            # The time the token expires.
            'exp': utime.time() + epoch_offset + token_ttl,
            # The audience field should always be set to the GCP project id.
            'aud': project_id
    }

    #This only supports RS256 at this time.
    header = { "alg": algorithm, "typ": "JWT" }
    content = b42_urlsafe_encode(ujson.dumps(header).encode('utf-8'))
    content = content + '.' + b42_urlsafe_encode(ujson.dumps(claims).encode('utf-8'))
    signature = b42_urlsafe_encode(rsa.sign(content,private_key,'SHA-256'))
    return content+ '.' + signature #signed JWT

def get_mqtt_client(project_id, cloud_region, registry_id, device_id, jwt):
    """Create our MQTT client. The client_id is a unique string that identifies
    this device. For Google Cloud IoT Core, it must be in the format below."""
    client_id = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(project_id, cloud_region, registry_id, device_id)
    print('Sending message with password {}'.format(jwt))
    client = MQTTClient(client_id.encode('utf-8'),server=config.google_cloud_config['mqtt_bridge_hostname'],port=config.google_cloud_config['mqtt_bridge_port'],user=b'ignored',password=jwt.encode('utf-8'),ssl=True)
    client.set_callback(on_message)
    client.connect()
    client.subscribe('/devices/{}/config'.format(device_id), 1)
    client.subscribe('/devices/{}/commands/#'.format(device_id), 1)
    return client

def write_2leds(letter, color):
    rgb = color
    char_matrix = characters.get(letter)
    led_counter = 0
    for row in char_matrix:
        for led in row:
            if(led):
                np[led_counter] = rgb
            else:
                np[led_counter] = (0, 0, 0)
            led_counter += 1
    np.write()

# sensor connection
write_2leds(".", (0, 0, 5))
bme_sensor.set_gas_heater_profile(320, 120, 0)
psm_sensor.wake_up()

# cloud connection
jwt = create_jwt(config.google_cloud_config['project_id'], config.jwt_config['private_key'], config.jwt_config['algorithm'], config.jwt_config['token_ttl'])
client = get_mqtt_client(config.google_cloud_config['project_id'], config.google_cloud_config['cloud_region'], config.google_cloud_config['registry_id'], config.google_cloud_config['device_id'], jwt)

epoch_offset = 946684800
esp32.wake_on_ext0(pin = Pin(config.device_config["btn"], Pin.IN), level = esp32.WAKEUP_ALL_LOW)

loop = 0
while True:
    if loop < config.app_config["loops"]:
        write_2leds(".", (5, 5, 5))

        timestamp = utime.time() + epoch_offset
        bme_data = bme_sensor.measurements
        psm_data = psm_sensor.measurements[1]
        message = {
            "device_id": config.google_cloud_config['device_id'],
            "timestamp": timestamp,
            "temp": bme_data["temp"],
            "hum": bme_data["hum"],
            "press": bme_data["press"],
            "gas": bme_data["gas"],
            "cpm10": psm_data["cpm10"],
            "cpm25": psm_data["cpm25"],
            "cpm100": psm_data["cpm100"],
            "apm10": psm_data["apm10"],
            "apm25": psm_data["apm25"],
            "apm100": psm_data["apm100"]
        }
        print("Publishing message "+str(ujson.dumps(message)))
        write_2leds(".", (5, 0, 0))
        mqtt_topic = '/devices/{}/{}'.format(config.google_cloud_config['device_id'], 'events')
        client.publish(mqtt_topic.encode('utf-8'), ujson.dumps(message).encode('utf-8'))

        client.check_msg() # Check for new messages on subscription
        write_2leds(" ", (5, 0, 0))
        utime.sleep_ms(config.app_config["delay"])  # Delay for delay seconds.
        loop += 1
        gc.collect()
    else:
        write_2leds(":", (5, 5, 5))
        print("Going to sleep for about %s milliseconds!" % config.app_config["deepsleepms"])
        psm_sensor.power_off()
        bme_sensor.power_off()
        utime.sleep_ms(5000)
        machine.deepsleep(config.app_config["deepsleepms"]) # Deep sleep to 



