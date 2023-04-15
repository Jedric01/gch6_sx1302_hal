#! /bin/bash

echo GCH6 killing mqtt-controller
kill `pgrep -f gch6-mqtt-controller`
