# 1. Install libraries
```
sudo apt update
sudo apt install git
cd ~/Documents/
git clone https://github.com/Lora-net/sx1302_hal.git
cd sx1302_hal
make clean all
make all
cp tools/reset_lgw.sh util_chip_id/
cp tools/reset_lgw.sh packet_forwarder/
```

# 2. Register gateway on TTN
```
# get sx1302 EUI
cd ~/Documents/sx1302_hal/util_chip_id/
./chip_id 
```


# 3. Configure conf file
1. Download global_conf.json from TTN  
2. Find appropriate frequency conf.json file on ./sx1302_hal/packet_fowarder
    * https://lora-alliance.org/resource_hub/rp2-101-lorawan-regional-parameters-2/
3. Adjust "gateway_conf" object on local conf to match TTN global_conf
    * "gateway_ID": copy from global_conf
    * "server_address": copy from global_conf
    * "port": set to 1700 if connecting to TTN, matching "servers"
    * "servers": append global_conf["servers"] at end of local gateway_conf


# 4. Run
```
cd ~/sx1302_hal/packet_forwarder/
./lora_pkt_fwd -c YOUR_CONF_FILE
```

# Links
* https://www.waveshare.com/wiki/SX1302_LoRaWAN_Gateway_HAT
* https://lora-alliance.org/resource_hub/rp2-101-lorawan-regional-parameters-2/
* https://www.thethingsnetwork.org/docs/lorawan/frequency-plans/
