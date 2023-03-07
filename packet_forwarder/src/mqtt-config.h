#include "stdlib.h"
#include "string.h"
#include "unistd.h"
#include "MQTTClient.h"

// MQTT Definitions
#define ADDRESS     "broker.emqx.io:1883"
#define USERNAME    "user"
#define PASSWORD    "user"
#define CLIENTID    "c-client"
#define QOS         0
#define TOPIC       "emqx/c-test"
#define TIMEOUT     10000L
// #define CAPATH      "/home/fyp-gch6-2/Documents/paho.mqtt.c/emqxsl-ca.crt"

void publish(MQTTClient client, char *topic, char *payload) {
    MQTTClient_message message = MQTTClient_message_initializer;
    message.payload = payload;
    message.payloadlen = strlen(payload);
    message.qos = QOS;
    message.retained = 0;
    MQTTClient_deliveryToken token;
    MQTTClient_publishMessage(client, topic, &message, &token);
    MQTTClient_waitForCompletion(client, token, TIMEOUT);
    printf("Send `%s` to topic `%s` \n", payload, TOPIC);
}

MQTTClient* initialize_mqtt(){
    // initialize MQTT Client
    int rc;
    MQTTClient client;
    MQTTClient_create(&client, ADDRESS, CLIENTID, 0, NULL);
    MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;
    conn_opts.username = USERNAME;
    conn_opts.password = PASSWORD;
    // MQTTClient_SSLOptions ssl_opts = MQTTClient_SSLOptions_initializer;
    // ssl_opts.trustStore = CAPATH;
    // conn_opts.ssl = &ssl_opts;
    
    if ((rc = MQTTClient_connect(client, &conn_opts)) != MQTTCLIENT_SUCCESS) {
        printf("Failed to connect, return code %d\n", rc);
        exit(-1);
    } else {
        printf("Connected to MQTT Broker!\n");
        return &client;
    }
