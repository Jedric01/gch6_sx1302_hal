#! /bin/bash

# https://stackoverflow.com/a/4480671/19351429

# add setup.sh to ~/.bashrc, which will run `python mqtt-handler/gch6-mqtt-controller.py`
# bashrc runs everytime bash shell started, hence why if-fi statements below
pwd=$(pwd)

check_if_line_exists()
{
    grep -qsFx "# GCH6 auto start mqtt-controller" ~/.bashrc
}

add_line_to_profile()
{    
    echo "[GCH6] Adding script to auto start gch6-mqtt-controller on user login."

    printf "%s\n" "" >> ~/.bashrc
    printf "%s\n" "# GCH6 auto start mqtt-controller"               >> ~/.bashrc
    printf "%s\n" "if ! pgrep -f gch6-mqtt-controller.py ; then"    >> ~/.bashrc
    printf "%s\n" "  echo GCH6 starting mqtt-controller"            >> ~/.bashrc
    printf "%s\n" "  cd ${pwd}"                                     >> ~/.bashrc
    printf "%s\n" "  nohup python ./mqtt_handler/gch6-mqtt-controller.py >/dev/null 2>&1 &" >> ~/.bashrc
    printf "%s\n" "  cd ~"                                          >> ~/.bashrc
    printf "%s\n" "fi"                                              >> ~/.bashrc
}

check_if_line_exists || add_line_to_profile

# manual run mqtt-controller
echo GCH6 starting mqtt-controller
nohup python ${pwd}/mqtt_handler/gch6-mqtt-controller.py >/dev/null 2>&1 &