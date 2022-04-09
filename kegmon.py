#region Imports

#TODO: Add temp sensors on pins 8 and 15 for L/R and figure out how I'm doing regular temperature polling

import time
from threading import Event
import RPi.GPIO as GPIO
from flowmeter import *
import paho.mqtt.client as mqtt
import pickle
import os.path

#endregion
#region GPIO + Flowmeter Library Configuration

GPIO_tap0 = 3
GPIO_tap1 = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_tap0, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_tap1, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#Checks for pickled files in the running directory, otherwise makes new flow objects
if((os.path.exists('./keg0.pkl'))):
    flow0 = pickle.load(open('./keg0.pkl', 'rb'))
else:
    flow0 = FlowMeter("american", "left tap","quarter")
if((os.path.exists('./keg1.pkl'))):
    flow1 = pickle.load(open('./keg1.pkl', 'rb'))
else:
    flow1 = FlowMeter("american", "right tap","quarter")

def draw0(channel):
    currentTime = int(time.time() * FlowMeter.MS_IN_A_SECOND)
    if flow0.enabled == True:
        flow0.update(currentTime)
def draw1(channel):
    currentTime = int(time.time() * FlowMeter.MS_IN_A_SECOND)
    if flow1.enabled == True:
        flow1.update(currentTime)

GPIO.add_event_detect(GPIO_tap0, GPIO.RISING, callback=draw0, bouncetime=20)
GPIO.add_event_detect(GPIO_tap1, GPIO.RISING, callback=draw1, bouncetime=20)

#endregion
#region MQTT Configuration

def keg0status():
    client.publish("keg","flow0,"+flow0.getFormattedThisPour().split(" ",1)[0]+","+flow0.getFormattedTotalPour().split(" ",1)[0] + "," + flow0.getFormattedBeerLeft().split(" ",1)[0] + "," + flow0.getPercentLeft()+","+flow0.getKeg().capitalize()+","+flow0.getBeverage())
    pickle.dump(flow0, open('keg0.pkl', 'wb'))

def keg1status():
    client.publish("keg","flow1,"+flow1.getFormattedThisPour().split(" ",1)[0]+","+flow1.getFormattedTotalPour().split(" ",1)[0] + "," + flow1.getFormattedBeerLeft().split(" ",1)[0] + "," + flow1.getPercentLeft()+","+flow1.getKeg().capitalize()+","+flow1.getBeverage())
    pickle.dump(flow1, open('keg1.pkl', 'wb'))

def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    print(msg)
    selector = ""

    if "tap0" in msg:
        if "reset" in msg:
            flow0.clear()
            print("Reset flow0")
            keg0status()
        elif "change" in msg:
            flow0.setBeverage((msg.split("change ",1)[1]))
            print("Changed flow0 to '"+(msg.split("change ",1)[1])+"'")
            keg0status()
        elif "keg" in msg:
            flow0.setKeg((msg.split("keg ",1)[1]))
            print("Changed flow0 to '"+(msg.split("keg ",1)[1])+"'")
            keg0status()
        elif "report" in msg:
            keg0status()
    elif "tap1" in msg:
        if "reset" in msg:
            flow1.clear()
            print("Reset flow1")
            keg1status()
        elif "change" in msg:
            flow1.setBeverage((msg.split("change ",1)[1]))
            print("Changed flow1 to '"+(msg.split("change ",1)[1])+"'")
            keg1status()
        elif "keg" in msg:
            flow1.setKeg((msg.split("keg ",1)[1]))
            print("Changed flow1 to '"+(msg.split("keg ",1)[1])+"'")
            keg1status()
        elif "report" in msg:
            keg1status()

client = mqtt.Client(client_id="kegerator")
client.username_pw_set(username="homeassistant", password="AidaTh7EeP0puChoh6yuJieM5CooChohie6ioghahcoov7aJeekoof6fol0oovoo")
client.connect("192.168.2.2",port=1883)
client.on_message=on_message 

#endregion
#region Main loop

client.loop_start()
client.subscribe("keg")
keg0status()
keg1status()

while True:
    currentTime = int(time.time() * 1000)
    
    if (flow0.thisPour > 0.05 and currentTime - flow0.lastClick > 3000): # 3 seconds of inactivity causes an update
        print("Detected "+ flow0.getFormattedThisPour()+ " of "+ flow0.getBeverage()+" poured. Total volume of "+flow0.getFormattedTotalPour()+" poured. "+flow0.getFormattedBeerLeft() + " or " + flow0.getPercentLeft() +" percent remaining in "+flow0.getKeg().capitalize()+" keg.")
        keg0status()
        flow0.thisPour = 0.0

    if (flow1.thisPour > 0.05 and currentTime - flow1.lastClick > 3000): # 3 seconds of inactivity causes an update
        print("Detected "+ flow1.getFormattedThisPour()+ " of "+ flow1.getBeverage()+" poured. Total volume of "+flow1.getFormattedTotalPour()+" poured. "+flow1.getFormattedBeerLeft() + " or " + flow0.getPercentLeft() +" percent remaining in "+flow1.getKeg().capitalize()+" keg.")
        keg1status()
        flow1.thisPour = 0.0

    # reset flow meter after each pour (2 secs of inactivity)
    if (flow0.thisPour <= 0.23 and currentTime - flow0.lastClick > 2000):
        flow0.thisPour = 0.0
    
    if (flow1.thisPour <= 0.23 and currentTime - flow1.lastClick > 2000):
        flow1.thisPour = 0.0


client.loop_stop()
#endregion
