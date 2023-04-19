#! /bin/bash

# https://stackoverflow.com/a/4480671/19351429

# add setup.sh to ~/.bashrc, which will run `python mqtt-handler/gch6-mqtt-controller.py`
# bashrc runs everytime bash shell started, hence why if-fi statements below
pwd=$(pwd)

install_dependencies()
{
    pip install -q wget
}
install_dependencies

check_if_line_exists()
{
    grep -qsFx "# GCH6 auto start mqtt-controller" ~/.bashrc
}

add_line_to_profile()
{    
    echo "[GCH6] Adding script to auto start gch6-mqtt-controller on user login."

    printf "%s\n" "" >> ~/.bashrc
    printf "%s\n" ".setup.sh: GCH6 setting up auto start mqtt-controller"                   >> ~/.bashrc
    printf "%s\n" "if ! pgrep -f gch6-mqtt-controller.py ; then"    >> ~/.bashrc
    printf "%s\n" "  echo .bashrc: GCH6 starting mqtt-controller"                           >> ~/.bashrc
    printf "%s\n" "  cd ${pwd}"                                     >> ~/.bashrc
    printf "%s\n" "  nohup python ./mqtt_handler/gch6-mqtt-controller.py >/dev/null 2>&1 &" >> ~/.bashrc
    printf "%s\n" "  cd ~"                                          >> ~/.bashrc
    printf "%s\n" "fi"                                              >> ~/.bashrc
}

setup_eui_topic(){
    # run ./util_chip_id get_eui
    # store to sx1302/mqtt_handler/.env
}

check_if_line_exists || add_line_to_profile

# manual run mqtt-controller
run_mqtt_controller()
{
    # GCH6 auto start mqtt-controller
    if ! pgrep -f gch6-mqtt-controller.py ; then
    echo .bashrc: GCH6 starting mqtt-controller
    cd /home/fyp-gch6-2/Documents/sx1302_hal
    nohup python ./mqtt_handler/gch6-mqtt-controller.py >/dev/null 2>&1 &
    cd ~
    fi
}
run_mqtt_controller