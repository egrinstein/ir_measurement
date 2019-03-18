#!/Users/mtaseska/.envs/PyPlayrec/bin/python

# temporary
import imp

# required
import argparse
import sounddevice as sd
import numpy as np
from matplotlib import pyplot as plt

# module with the main code
import stimulus as stim
imp.reload(stim)


# --- parse command line arguments
parser = argparse.ArgumentParser(description='Setting the parameters for RIR measurement using exponential sine sweep')
#---
parser.add_argument("-f", "--fs", type = int, help=" The sampling rate (make sure it matches that of your audio interface). Default: 44100 Hz.", default = 44100)
#---
parser.add_argument("-dur", "--duration", type = int, help=" The duration of a single sweep. Default: 7 seconds.", default = 7)
#---
parser.add_argument("-r", "--reps", type = int, help = "Number of repetitions of the sinesweep. Default: 2.", default = 2)
#---
parser.add_argument("-fr", "--frange", type =  tuple, help = "Frequency range of the sweep (f_min, f_max). Default: (0.01,20000) Hz.", default = (0.01,20000))
#---
parser.add_argument("-a", "--amplitude", type = float, help = "Amplitude of the sine. Default: 0.7",default = 0.7)
#---
parser.add_argument("-ss", "--startsilence", type = int, help = "Duration of silence at the start of a sweep, in seconds. Default: 1.", default = 1)
#---
parser.add_argument("-es", "--endsilence", type = int, help = "Duration of silence at the end of a sweep, in seconds. Default: 1.", default = 1)
#---
#parser.add_argument('--chin', nargs='+', type=int)
#parser.add_argument('--chou', nargs='+', type=int)

parser.add_argument("-chin", "--inputChannelMap", nargs='+', type=int, help = "Input channel mapping")
parser.add_argument("-chou", "--outputChannelMap", nargs='+', type=int, help = "Output channel mapping")
#---
#nargs='+', type=int

#--- arguments for checking and selecting audio interface
parser.add_argument("-outdev", "--outputdevice", type = int, help = "Output device ID.")
parser.add_argument("-indev", "--inputdevice", type = int, help = "Input device ID.")
parser.add_argument('--listdev', help='List the available devices, indicating the default one',
    action='store_true')
parser.add_argument('--setdev', help='Use this keyword in order to change the default audio interface.',
    action='store_true')
parser.add_argument('--test', help = 'Just for debugging: check the output of deconvolution applied directly to the computer-generated sinesweep')

args = parser.parse_args()
# -------------------------------

if args.listdev == True:

    print(sd.query_devices())
    print("Default input and output device: ", sd.default.device )

elif args.setdev == True:

    if args.inputdevice is not None:
        sd.default.device[0] = args.inputdevice

    if args.outputdevice is not None:
        sd.default.device[1] = args.outputdevice

    sd.check_input_settings()
    sd.check_output_settings()

    print(sd.query_devices())
    print("Default input and output device: ", sd.default.device )
    print("Sucessfully selected audio devices. Ready to record.")

else:

    # sound device parameters, input and output channels

    sd.default.samplerate = args.fs
    sd.default.dtype = 'float32'

    if args.inputChannelMap is not None:
        channels_in = args.inputChannelMap
        print("Input channels:",  channels_in)
    else:
        channels_in= [1]

    if args.outputChannelMap is not None:
        channels_out = args.outputChannelMap
        print("Output channels:",channels_out)
    else:
        channels_out = [1]


    # Set excitation parameters
    type = 'sinesweep'
    fs = args.fs
    duration = args.duration
    amplitude = args.amplitude
    repetitions = args.reps
    silenceAtStart = args.startsilence
    silenceAtEnd = args.endsilence

    # Create a test signal object, and generate the excitation
    testStimulus = stim.stimulus(type,fs);
    testStimulus.generate(fs, duration, amplitude,repetitions,silenceAtStart, silenceAtEnd)

    # Start the recording
    recorded = sd.playrec(testStimulus.signal, samplerate=fs, input_mapping = channels_in,output_mapping = channels_out)
    sd.wait()

    # Get the room impulse response
    RIR = testStimulus.deconvolve(recorded)
    # length after truncation
    lenRIR = 1.2;
    # keep some noncausal part to check for nonlinear distortions
    startId = (duration+silenceAtStart)*fs
    endId = int(np.ceil((duration+silenceAtStart + lenRIR)*fs))
    RIR = RIR[startId:endId,:]

    plt.plot(RIR)
    plt.show()


    #if flag_plt:
    #    rir.analyseRIR(RIRs[:,0],fs)




    #
    #plt.plot(recorded)
    #plt.show()
    #
    # #wavwrite('newrecording.wav',fs,myrecording)
    # #len = testStimulus.signal.shape[0]/fs
    # #taxis = np.arange(0,len,1/fs)
    # #plt.plot(taxis,testStimulus.signal)
    # #plt.show()
