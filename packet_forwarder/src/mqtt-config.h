#include "stdlib.h"
#include "string.h"
#include "unistd.h"
#include "MQTTClient.h"

// MQTT Definitions
#define ADDRESS     "broker.emqx.io:1883"
#define CLIENTID    "c-client"
#define QOS         0
#define TOPIC       "emqx/c-test"
#define TIMEOUT     10000L

int initialize_mqtt_client(MQTTClient* client){
    MQTTClient_create(client, ADDRESS, CLIENTID, 0, NULL);
    MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;
    
    int rc;
    if ((rc = MQTTClient_connect(*client, &conn_opts)) != MQTTCLIENT_SUCCESS) {
        printf("Failed to connect, return code %d\n", rc);
        return -1;
    } else {
        printf("Connected to MQTT Broker!\n");
        return 0;
    }
}

void publish_mqtt(MQTTClient client, char *topic, char *payload) {
    MQTTClient_message message = MQTTClient_message_initializer;
    message.payload = payload;
    message.payloadlen = strlen(payload);
    message.qos = QOS;
    message.retained = 0;
    MQTTClient_deliveryToken token;

    int rc;
    if ((rc = MQTTClient_publishMessage(client, topic, &message, &token)) != MQTTCLIENT_SUCCESS){
        printf("Failed to publish message, return code %d\n", rc);
    }

    rc = MQTTClient_waitForCompletion(client, token, TIMEOUT);
    printf("Sent `%s` to topic `%s` \n", payload, TOPIC);
}

void disconnect_mqtt(MQTTClient* client){
    // diconnect mqtt client, only runs if ./lora_pkt_fwd.main exits gracefully
    int rc;
    if ((rc = MQTTClient_disconnect(*client, 10000)) != MQTTCLIENT_SUCCESS){
    	printf("Failed to disconnect MQTT, return code %d\n", rc);
    } else{
        printf("MQTT disconnected gracefully.\n");
    }
    MQTTClient_destroy(client);
}