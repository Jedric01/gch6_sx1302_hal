#!/usr/bin/env python3

import random
from paho.mqtt import client as mqtt_client
import os
import subprocess
import time
from re import findall
from pathlib import Path
import logging

from wget_config import download_config

broker = 'broker.emqx.io'
port = 1883

# todo: read from .env
eui = "0x0016c001f160f149"
topic = "/gateway/control/" + eui

# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'cust1'
password = 'gch6'
QOS = 0

path_repo = Path(__file__).resolve().parent.parent
path_log = str(path_repo) + "/log/"

logging.basicConfig(
    level=logging.INFO,
    filename=path_log + "gch6-mqtt-controller.log",
    filemode='w'
)

pid = None
logf = None

### MQTT HANDLER ###


def on_log(client, userdata, level, buffer):
    logging.info(buffer)


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to MQTT Broker!")
            pass
        else:
            logging.info("Failed to connect, return code %d\n", rc)
            pass

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect(broker, port)
    client.on_log = on_log

    return client


def subscribe(client: mqtt_client):
    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


def on_publish(client, userdata, mid):
    logging.info("In on_publish callback mid= " + str(mid))


def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    logging.info(f"RECEIVED `{payload}` from `{msg.topic}` topic")

    response = parse_payload(payload)
    send_response(client, response)


def parse_payload(payload):
    global pid, logf
    payload = payload.rstrip().lstrip().split(';')
    command = payload[0]
    response = ""

    # Get Status Handlers
    if command == "ping":
        response = "pong"
    elif command == "temp":
        response = check_temp()
    elif command == "uptime":
        response = str(check_uptime())
    elif command == "reboot":
        os.system("shutdown -r now")

    # Packet forwarder handlers
    elif command == "start":
        path_conf = 'conf-cs.json'
        if len(payload) < 3:
            logging.info("Running packet forwarder with default conf-cs.json")
        elif len(payload) == 3:
            logging.info("Fetching config file with wget.")
            path_conf = path_repo + "/packet_forwarder/conf-wget.json"
            download_config(path_conf, payload[1].lstrip().rstrip(), payload[2].lstrip().rstrip())
        
        if pid:
            response = "Packet forwarded already started."
        else:
            pid, logf = run_pkt_fwd(config=path_conf)
            if pid:
                response = "Packet forwarder started successfully."
            else:
                response = "Failed to start packet forwarder."

    elif command == "stop":
        if stop_pkt_fwd(logf) == 0:
            response = "Packet forwarder stopped successfully."
        else:
            response = "No running packet forwarder instance."
            # response = "Error encountered when stopping packet forwarder."

    else:
        # Command not found to be handled by server, else endless loop here
        # logging.info("Command not found")
        # response = "Supported commands are: [ping, temp, uptime, reboot, run_pkt_fwd, stop_pkt_fwd]"
        pass

    return response


def send_response(client, response):
    # explicit delay needed to allow time for backend client publish disconnect(), receive connect()
    time.sleep(0.2)

    if response != "":
        ret = client.publish(topic, response, qos=QOS)
        logging.info("PUBLISHED return =" + str(ret))


#########################

### COMMAND FUNCTIONS ###

def check_temp():
    temp = subprocess.check_output(
        ["vcgencmd", "measure_temp"]).decode("UTF-8")
    return (findall("\d+\.\d+", temp)[0])


def check_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
    return uptime_seconds


def reboot_handler():
    os.system('sudo shutdown -r now')


### PACKET FORWARDER CONTROLS ###

def run_pkt_fwd(config='conf-cs.json', log='pkt_fwd.log'):
    args = ['./lora_pkt_fwd', '-c', config]

    try:
        path_log = str(path_repo) + "/log/"
        path_packet_forwarder = str(path_repo) + "/packet_forwarder/"
        logf = open(path_log + log, 'w')
        pid = subprocess.Popen(
            args, stdout=logf, stderr=logf, cwd=path_packet_forwarder)

        return [pid, logf]

    except OSError as e:
        # encountered some error
        logging.info("I/O error({0}): {1}".format(e.errno, e.strerror))
        return [-1, None]


def stop_pkt_fwd(logf):
    global pid
    # pid.terminate()
    if pid == None:
        return -1
    
    pid = None
    rc = os.WEXITSTATUS(os.system('kill `pgrep lora_pkt_fwd`'))
    if rc == 0:
        # grace time to save exit log buffer
        time.sleep(2)
        if logf:
            logf.close()

    return rc

#########################


if __name__ == '__main__':
    run()
