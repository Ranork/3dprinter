#!/bin/bash

lxterminal -e "./starter-screen"
lxterminal -e "./starter-web"
sleep 5
lxterminal -e "./starter-API"
sleep 5
chromium-browser --incognito --kiosk http://127.0.0.1:8000/
