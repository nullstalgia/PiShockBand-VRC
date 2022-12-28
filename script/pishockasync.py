#!/usr/bin/python3
# Original Script by noideaman
# Fixed, edited, and added on to by nullstalgia

from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from configparser import ConfigParser
import requests
import asyncio
import json

config=ConfigParser()
config.read('pishock.cfg')

APIKEY=config['API']['APITOKEN']
USERNAME=config['API']['USERNAME']
NAME=config['API']['APPNAME']
pets=config['PETS']['PETS'].split()
touchpoints=config['TOUCHPOINTS']['TOUCHPOINTS'].split()

ip = "127.0.0.1"
port = 9101

verbose=0
funtype=1
fundelaymax=10
fundelaymin=0
funduration=2
funintensity=0
funtarget=""
funtouchpointstate=False
shocksend=False
typesend="vibrate"
quickshocksend = False

# Set an intensity (1-100) that the script will never send commands above.
max_intensity = 15

# Set a duration (1-99) in seconds that the script will never send commands above.
max_duration = 5

# Does not send a 300ms (duration 300) shock at 0 duration unless this is True
agree_to_zero = True

def set_verbose(address, *args):
    piverbose=str({args})
    cleanverbose=''.join((x for x in piverbose if x.isdigit()))
    global verbose
    verbose=int(cleanverbose)

#Pet functions
def set_target(address, *args):
    global funtarget
    global pets
    array_target=args[0]
    if array_target > 0:
        funtarget=pets[array_target-1]
        print(f"target set to {funtarget}")
    else:
        funtarget=""
        print(f"no target selected")

def set_pet_type(adress, *args):
    global funtype
    global typesend
    global verbose
    funtype=args[0]
    if funtype == 0:
        typesend="shock"
    elif funtype == 1:
        typesend="vibrate"
    elif funtype == 2:
        typesend="beep"

    #print(funtype)

def set_pet_intensity(address, *args):
    global funintensity
    global verbose
    floatintensity=args[0]
    intensity=floatintensity*100
    funintensity=int(intensity)

    #print(funintensity)

def set_pet_duration(address, *args):
    global funduration
    global verbose
    floatduration=args[0]
    time=floatduration*15
    funduration=int(round(time))
    #print(funduration)
    #print(cleanduration)

def set_pet_state(address:str, *args) -> None:
    global shocksend
    global verbose
    global quickshocksend
    print(address)
    if address.endswith("Quick"):
        quickshocksend = args[0]
    else:
        shocksend = args[0]

    #print(shocksend)

#TouchPointFunctions
def set_touchpoint(address, *args):
    global funtouchpoint
    global funtouchpointstate
    cleantouchpointstate=args[0]
    if cleantouchpointstate == True:
        touchpointtarget=args[0]
        funtouchpoint=touchpoints[touchpointtarget]
        funtouchpointstate=cleantouchpointstate
    if cleantouchpointstate == False:
        funtouchpointstate=cleantouchpointstate

    #print(funtouchpoint)
    #print(funtouchpointstate)

def set_TP_type(adress, *args):
    global funTPtype
    global typeTPsend
    global verbose
    funTPtype=args[0]
    if funTPtype == 0:
        typeTPsend="shock"
    if funTPtype == 1:
        typeTPsend="vibrate"
    if funTPtype == 2:
        typeTPsend="beep"

    #print(funTPtype)

def set_TP_intensity(address, *args):
    global funTPintensity
    global verbose
    floatTPintensity=args[0]
    TPintensity=floatTPintensity*100
    funTPintensity=int(TPintensity)

    #print(funTPintensity)

def set_TP_duration(address, *args):
    global funTPduration
    global verbose
    floatTPduration=args[0]
    TPtime=floatTPduration*15
    funTPduration=int(TPtime)

    #print(cleanTPduration)
    #print(funTPduration)

dispatcher = Dispatcher()
#dispatchers for pet functions
dispatcher.map("/avatar/parameters/pishock/Type", set_pet_type)
dispatcher.map("/avatar/parameters/pishock/Intensity", set_pet_intensity)
dispatcher.map("/avatar/parameters/pishock/Duration", set_pet_duration)
dispatcher.map("/avatar/parameters/pishock/Shock", set_pet_state)
dispatcher.map("/avatar/parameters/pishock/ShockQuick", set_pet_state)
dispatcher.map("/avatar/parameters/pishock/Target", set_target)
#dispatchers for touchpoint functions
dispatcher.map("/avatar/parameters/pishock/TPType", set_TP_type)
dispatcher.map("/avatar/parameters/pishock/TPIntensity", set_TP_intensity)
dispatcher.map("/avatar/parameters/pishock/TPDuration", set_TP_duration)
dispatcher.map("/avatar/parameters/pishock/Touchpoint_*", set_touchpoint)
#verbose functions
dispatcher.map("/avatar/parameters/pishock/Debug", set_verbose)

async def loop():
    global shocksend
    global verbose
    global funtype
    global funduration
    global funintensity
    global USERNAME
    global NAME
    global SHARECODE
    global APIKEY
    global typesend
    global funtarget
    global funtouchpoint
    global typeTPsend
    global funTPtype
    global funTPduration
    global funTPintensity
    await asyncio.sleep(0.1)
    if shocksend == True:
        sleeptime=float(funduration)+1.7
        if funtarget == "":
            print("No target selected! Not sending shock...")
        else:
            print(f"sending {typesend} at {funintensity} for {funduration} seconds")
            # Limiting intensity
            if funintensity > max_intensity:
                print(f"Intensity set too high! Bringing down to {max_intensity}")
                funintensity = max_intensity
            # Limiting duration
            if funduration > max_duration:
                print(f"Duration set too high! Bringing down to {max_duration}")
                funduration = max_duration
            # Setting duration to 300ms if set to 0%
            sent_duration = funduration
            if agree_to_zero and funduration == 0:
                sent_duration = 300
            
            datajson = str({"Username":USERNAME,"Name":NAME,"Code":funtarget,"Intensity":funintensity,"Duration":sent_duration,"Apikey":APIKEY,"Op":funtype})
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            sendrequest=requests.post('https://do.pishock.com/api/apioperate', data=datajson, headers=headers)

        print(f"waiting {sleeptime} before next command")
        #print(sendrequest)
        #print (sendrequest.text)

        await asyncio.sleep(sleeptime)

    if quickshocksend == True:
        sleeptime=float(funduration)+1.7
        if funtarget == "":
            print("No target selected! Not sending shock...")
        else:
            # Converting duration to milliseconds
            sent_duration = funduration*100
            # To make sure we never accidentally send a 99 second shock, or one too high
            if sent_duration < 100:
                sent_duration = 101
            elif sent_duration >= 1500:
                sent_duration = 1499
            print(f"sending {typesend} at {funintensity} for {sent_duration} ms")
            # Limiting intensity
            if funintensity > max_intensity:
                print(f"Intensity set too high! Bringing down to {max_intensity}")
                funintensity = max_intensity
            
            datajson = str({"Username":USERNAME,"Name":NAME,"Code":funtarget,"Intensity":funintensity,"Duration":sent_duration,"Apikey":APIKEY,"Op":funtype})
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            sendrequest=requests.post('https://do.pishock.com/api/apioperate', data=datajson, headers=headers)

        print(f"waiting {sleeptime} before next command")
        #print(sendrequest)
        #print (sendrequest.text)

        await asyncio.sleep(sleeptime)


    if funtouchpointstate == True:
        sleeptime=funTPduration+1.7
        print(f"touch point sending {typeTPsend} at {funTPintensity} for {funTPduration} seconds")
        # Limiting intensity
        if funTPintensity > max_intensity:
                print(f"Intensity set too high! Bringing down to {max_intensity}")
                funTPintensity = max_intensity
        # Setting duration to 300ms if set to 0%
        sent_duration = funTPduration
        if agree_to_zero and funTPduration == 0:
            sent_duration = 300
        datajson = str({"Username":USERNAME,"Name":NAME,"Code":funtouchpoint,"Intensity":funTPintensity,"Duration":sent_duration,"Apikey":APIKEY,"Op":funTPtype})
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        sendrequest=requests.post('https://do.pishock.com/api/apioperate', data=datajson, headers=headers)

        print(f"waiting {sleeptime} before next command")
        #print(sendrequest)
        #print (sendrequest.text)

        await asyncio.sleep(sleeptime)


async def init_main():
    server = AsyncIOOSCUDPServer((ip, port), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()
    print("PiShock OSC Client started!")
    print(f"Socket opened on port {port}")
    print("WARNING: Target, intensity, duration, and type are set to defaults.")
    while True:
        await loop()

    transport.close()


asyncio.run(init_main())
