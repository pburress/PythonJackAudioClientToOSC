# PythonJackAudioClientToOSC
JACK AUDIO CLIENT to OSC CLIENT PYTHON SCRIPT.

Script to capture audio from Jack Audio Client and send amplitude and FFT data array to OSC messages

This script is modified from Python Jack Audio Thru Client Example found at: 

https://jackclient-python.readthedocs.io/en/0.5.3/examples.html#pass-through-client 

Instead of passing the audio back out to OutBuffer, audio captured at In Buffer is read into a Numpy Array and then passed to an OSC (Open Sound Control) Client 
to send the data array, in my test case, to Blender Animation Nodes and animate objects based on the audio levels at particular frequency bands.

This code is customized to my OS (Linux Ubuntu Studio), and probably my sound card / mother board setup and just what I was able to get to work. Sharing if anyone can help make improvements. 


