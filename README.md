# Kegerator Monitor for IST 402RPI
Developed by Chase Matthews
flowmeter.py using code from https://github.com/adafruit/Adafruit_Learning_System_Guides/tree/main/Kegomatic

## So what's it do?
Basically this uses 2 flow sensors to monitor the beer being drawn from the system. This data is used to calculate various elements about the keg's status. Integrates MQTT communication with a HomeAssistant server running NODE-RED to handle entity / dashbaord management on a frontend. The Pi also connects to a touchscreen displaying keg status.