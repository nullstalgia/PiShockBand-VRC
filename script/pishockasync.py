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
funtype="1"
fundelaymax="10"
fundelaymin="0"
funduration="2"
funintensity="0"
funtarget=""
funtouchpointstate="False"
boolsend='False'
typesend="beep"

# Set an intensity that the script will never send commands above.
max_intensity = 15


# Does not send a 300ms (duration 300) shock at 0 duration unless this is True
agree_to_zero = False

def set_verbose(address, *args):
    piverbose=str({args})
    cleanverbose=''.join((x for x in piverbose if x.isdigit()))
    global verbose
    verbose=int(cleanverbose)

#Pet functions
def set_target(address, *args):
    global funtarget
    global pets
    pitarget=str({args})
    cleantarget=''.join((x for x in pitarget if x.isdigit()))
    arratarget=int(cleantarget)
    if arratarget > 0:
        funtarget=pets[arratarget-1]
        print(f"target set to {funtarget}")
    else:
        funtarget=""
        print(f"no target selected")

def set_pet_type(adress, *args):
    pitype=str({args})
    global funtype
    global typesend
    global verbose
    funtype= ''.join((x for x in pitype if x.isdigit()))
    if funtype == '0':
        typesend="shock"
    if funtype == '1':
        typesend="vibrate"
    if funtype == '2':
        typesend="beep"

    #print(funtype)

def set_pet_intensity(address, *args):
    piintensity=str({args})
    global funintensity
    global verbose
    tempintensity=str(piintensity.strip("{()},")[:4])
    floatintensity=float(tempintensity)
    intensity=floatintensity*100
    funintensity=int(intensity)

    #print(funintensity)

def set_pet_duration(address, *args):
    piduration=str({args})
    global funduration
    global verbose
    cleanduration=str(piduration.strip("{()},")[:4])
    floatduration=float(cleanduration)
    time=floatduration*15
    funduration=int(round(time))
    #print(funduration)
    #print(cleanduration)

def set_pet_state(address:str, *args) -> None:
    global boolsend
    global verbose
    booltest=str({args})
    boolsend= ''.join((x for x in booltest if x.isalpha()))

    #print(boolsend)

#TouchPointFunctions
def set_touchpoint(address, *args):
    global funtouchpoint
    global funtouchpointstate
    pitouchpointstate=str({args})
    cleantouchpointstate=''.join((x for x in pitouchpointstate if x.isalpha()))
    if cleantouchpointstate == "True":
        pitouchpoint=str({address})
        cleantouchpoint=''.join((x for x in pitouchpoint if x.isdigit()))
        touchpointtarget=int(cleantouchpoint)
        funtouchpoint=touchpoints[touchpointtarget]
        funtouchpointstate=cleantouchpointstate
    if cleantouchpointstate == "False":
        funtouchpointstate=cleantouchpointstate

    #print(funtouchpoint)
    #print(funtouchpointstate)

def set_TP_type(adress, *args):
    piTPtype=str({args})
    global funTPtype
    global typeTPsend
    global verbose
    funTPtype= ''.join((x for x in piTPtype if x.isdigit()))
    if funTPtype == '0':
        typeTPsend="shock"
    if funTPtype == '1':
        typeTPsend="vibrate"
    if funTPtype == '2':
        typeTPsend="beep"

    #print(funTPtype)

def set_TP_intensity(address, *args):
    piTPintensity=str({args})
    global funTPintensity
    global verbose
    tempTPintensity=str(piTPintensity.strip("{()},")[:4])
    floatTPintensity=float(tempTPintensity)
    TPintensity=floatTPintensity*100
    funTPintensity=int(TPintensity)

    #print(funTPintensity)

def set_TP_duration(address, *args):
    piTPduration=str({args})
    global funTPduration
    global verbose
    cleanTPduration=str(piTPduration.strip("{()},")[:4])
    floatTPduration=float(cleanTPduration)
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
dispatcher.map("/avatar/parameters/pishock/Target", set_target)
#dispatchers for touchpoint functions
dispatcher.map("/avatar/parameters/pishock/TPType", set_TP_type)
dispatcher.map("/avatar/parameters/pishock/TPIntensity", set_TP_intensity)
dispatcher.map("/avatar/parameters/pishock/TPDuration", set_TP_duration)
dispatcher.map("/avatar/parameters/pishock/Touchpoint_*", set_touchpoint)
#verbose functions
dispatcher.map("/avatar/parameters/pishock/Debug", set_verbose)

async def loop():
    global boolsend
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
    if boolsend == 'True':
        sleeptime=float(funduration)+1.7
        if funtarget == "":
            print("No target selected! Not sending shock...")
        else:
            print(f"sending {typesend} at {funintensity} for {funduration} seconds")
            # Limiting intensity
            if funintensity > max_intensity:
                print(f"Intensity set too high! Bringing down to {max_intensity}")
                funintensity = max_intensity
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

    if funtouchpointstate == 'True':
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

    while True:
        await loop()

    transport.close()


asyncio.run(init_main())
