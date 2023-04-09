#!/usr/bin/env python3

import random
from paho.mqtt import client as mqtt_client
import os

import subprocess
from subprocess import check_output
import time
from re import findall

import logging

broker = 'broker.emqx.io'
port = 1883
topic = "mygch6/control"

# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'cust1'
password = 'gch6'
logging.basicConfig(level=logging.INFO)
QOS = 0

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
    command = payload.rstrip()
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
    elif command == "run_pkt_fwd":
        if pid:
            response = "Packet forwarded already started."
        else:
            pid, logf = run_pkt_fwd(config='conf.json')
            if pid:
                response = "Packet forwarder started successfully."
            else:
                response = "Failed to start packet forwarder."

    elif command == "stop_pkt_fwd":
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

def run_pkt_fwd(config='conf-cs.json', log='log.txt'):
    args = ['./lora_pkt_fwd', '-c', config]
    usern = os.environ.get('USER')
    path_pf = '/home/' + usern + '/Documents/sx1302_hal/packet_forwarder/'

    try:
        logf = open(path_pf + log, 'w')
        pid = subprocess.Popen(args, stdout=logf, stderr=logf, cwd=path_pf)

        return [pid, logf]

    except OSError as e:
        # encountered some error
        logging.info("I/O error({0}): {1}".format(e.errno, e.strerror))
        return [-1, None]


def stop_pkt_fwd(logf):
    global pid
    # pid.terminate()
    pid = None

    rc = os.WEXITSTATUS(os.system('kill `pgrep lora_pkt_fwd`'))
    if rc == 0:
        time.sleep(2)   # grace time to save graceful exit log
        if logf:
            logf.close()

    return rc

#########################


if __name__ == '__main__':
    run()
