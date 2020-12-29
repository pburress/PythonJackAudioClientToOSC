#!/usr/bin/env python3

"""MODIFY a JACK client that copies input audio directly to OSC

Example From: https://jackclient-python.readthedocs.io/en/0.5.3/examples.html#pass-through-client

This is somewhat modeled after the "thru_client.c" example of JACK 2:
http://github.com/jackaudio/jack2/blob/master/example-clients/thru_client.c

"""

import sys
import signal
import os
import jack
import threading

######################################################
##### ADD LIBRARIES TO SUPPORT FFT AND OSC
import numpy as np
import time

from pythonosc import udp_client
OSCclient=udp_client.SimpleUDPClient("127.0.0.1",9001)
#######################################################

if sys.version_info < (3, 0):
    # In Python 2.x, event.wait() cannot be interrupted with Ctrl+C.
    # Therefore, we disable the whole KeyboardInterrupt mechanism.
    # This will not close the JACK client properly, but at least we can
    # use Ctrl+C.
    signal.signal(signal.SIGINT, signal.SIG_DFL)
else:
    # If you use Python 3.x, everything is fine.
    pass

argv = iter(sys.argv)
# By default, use script name without extension as client name:
defaultclientname = os.path.splitext(os.path.basename(next(argv)))[0]

############ CHANGED THE NAME OF THE JACK CLIENT ###############
defaultclientname = "JACK AUDIO to Blender OSC Client and through"
####################################################################
clientname = next(argv, defaultclientname)
servername = next(argv, None)

client = jack.Client(clientname, servername=servername)

if client.status.server_started:
    print('JACK server started')
if client.status.name_not_unique:
    print('unique name {0!r} assigned'.format(client.name))

event = threading.Event()

@client.set_process_callback
def process(frames):



    assert len(client.inports) == len(client.outports)
    assert frames == client.blocksize
    for i, o in zip(client.inports, client.outports):
        inbuffer = i.get_buffer()
        ########################### CAPTURE DATA FROM INBUFFER AND TAKE FFT ###########
        data = [np.fromstring(inbuffer,dtype=np.float32) for channel in client.inports]
        mean=abs(np.mean(data[0]))
        try:
             dB = 10*np.log(mean)
             bar=int(50+dB)

             print("-"*bar+"|"," ",bar)
             
        except:
            bar=0    #### prevent error if No AUdio or all 0s input to the log function

        S_Left = abs(np.fft.fft(data[0],1024)[0:1024])
        S_Right = abs(np.fft.fft(data[1],1024)[0:1024])

        ############ SEND FFT AND AVERAGE AMPLITUDE TO OSC MESSAGES ###################

        print(S_Left)

        OSCclient.send_message("/audio/amplitude",bar)
        OSCclient.send_message("/spectrum/left",np.rint(S_Left))
        OSCclient.send_message("/spectrum/right",np.rint(S_Right))
        #time.sleep(0.05)
        ###############################################################################

@client.set_shutdown_callback
def shutdown(status, reason):
    print('JACK shutdown!')
    print('status:', status)
    print('reason:', reason)
    event.set()


# create two port pairs
for number in 1, 2:
    client.inports.register('input_{0}'.format(number))
    client.outports.register('output_{0}'.format(number))

with client:
    # When entering this with-statement, client.activate() is called.
    # This tells the JACK server that we are ready to roll.
    # Our process() callback will start running now.

    # Connect the ports.  You can't do this before the client is activated,
    # because we can't make connections to clients that aren't running.
    # Note the confusing (but necessary) orientation of the driver backend
    # ports: playback ports are "input" to the backend, and capture ports
    # are "output" from it.

    ############### CHANGE DEFUALT FOR MY SOUND CARD PULSE AUDIO IN#######
    ##### First line works but is my Microphone Line In. Second line 
    ##### connects to FireFox, Audio outputs of Audacity, Ardour, 
    ##### LMMS, etc. for my PC / Soundcard system. 
    ##### Microphone connetions can be selecte with QJackCTRL

    #capture = client.get_ports(is_physical=True, is_output=True)
    capture = client.get_ports('Sink-01')
    ######################################################################

    if not capture:
        raise RuntimeError('No physical capture ports')

    for src, dest in zip(capture, client.inports):
        client.connect(src, dest)

    playback = client.get_ports(is_physical=True, is_input=True)
    if not playback:
        raise RuntimeError('No physical playback ports')

    for src, dest in zip(client.outports, playback):
        client.connect(src, dest)

    print('Press Ctrl+C to stop')
    try:
        event.wait()
    except KeyboardInterrupt:
        print('\nInterrupted by user')

