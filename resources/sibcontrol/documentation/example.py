import sibcontrol
import sys      # for exit()
import time     # for sleep()


# Create a new SIB object and attach it to com port COM3
sib = sibcontrol.SIB350('com7')

# We can now set up the sweep parameters
# Set the start frequency in MHz. Must be between 0 and 350 MHz, inclusive
sib.start_MHz = 0.5         # Start frequency is set to 0.5 MHz

# Set the stop frequency in MHz.  Must be between 0 and 350 MHz, inclusive
sib.stop_MHz = 100          # Stop frequency is set to 100 MHz

# Set the number of frequency points to use in the sweep.
sib.num_pts = 100

# Set the signal amplitude of the synthesizer output, in mA. This value
# must be between 0 mA and 31.6 mA. In general, we should just set this
# at the maximum value and leave it there. There isn't any reason (yet)
# change this value.
sib.amplitude_mA = 31.6     # The synthesizer output amplitude is set to 31.6 mA


print(f'Start Frequency: {sib.start_MHz} MHz')
print(f'Stop Frequency: {sib.stop_MHz} MHz')
print(f'Number of sweep points: {sib.num_pts} MHz')
print(f'Signal amplitude: {sib.amplitude_mA} MHz')




#################################################
# EXAMPLE OF PERFORMING A HANDSHAKE
#################################################
# A handshake simply sends a random number to the SIB and expects
# it to be echoed back.
# NOTE: The system remains in the low-power state while performing this command.
data = 500332       # Some random 32-bit value

print('Beginning Handshake...')

try:
    sib.open()      # Open the serial connection
    return_val = sib.handshake(data)    # Send the number to the SIB and get the return value
except sibcontrol.SIBException as e:
    # Something went wrong
    sys.exit(e)
finally:
    # Close the connection
    sib.close()

if return_val == data:
    print('Handshake successful!')
else:
    print('Handshake failed.')

print('\n\n')






#################################################
# EXAMPLE OF READING THE FIRMWARE VERSION NUMBER
#################################################
# We can also request the version number of the firmware being run
# on the SIB.

print('Getting firmware version...')

try:
    sib.open()      # Open the serial connection
    firmware_version = sib.version()
except sibcontrol.SIBException as e:
    sys.exit(e)
finally:
    sib.close()     # Close the serial connection


print(f'The SIB Firmware is version: {firmware_version}')

print('\n\n')







#################################################
# EXAMPLE OF PERFORMING A SINGLE FREQUENCY SWEEP
#################################################

# Before we can perform the frequency sweep, we must send the configuration
# information to the SIB. It is always a good idea to make sure that all of
# configuration data is valid.
# Valid configuration data has:
#     Start Frequency < Stop Frequency
#     Enough separation between start and stop frequency to support the desired number of points.
if sib.valid_config():
    print('All configuration dat is valid.')

    try:
        sib.open()      # Open the serial connection

        sib.write_start_ftw()       # Send the start frequency ot the SIB
        sib.write_stop_ftw()        # Send the stop frequency to the SIB
        sib.write_num_pts()         # Send the number of points to the SIB
        sib.write_asf()             # Send the signal amplitude to the SIB
    except sibcontrol.SIBException:
        # Any problems will through an SIBException.
        # Close the serial connection
        sib.close()
        sys.exit()
else:
    print('Configuration data is not valid.')
    sys.exit()

# All of the configuration data has been sent to the SIB while it was
# in the low-power mode. We now must set the SIB into the active mode before
# we initiate a frequency sweep. It is possible to wake the SIB before sending
# the configuration data.
try:
    sib.wake()
except sibcontrol.SIBException:
    # If this command fails, it is because the DDS could not be correctly configured.
    sib.close()
    sys.exit()


# We can now start a single frequency sweep. First send the command to 
# start the frequency sweep.
try:
    sib.write_sweep_command()
except sibcontrol.SIBException:
    # If this command fails, it is becaues the system is still in the low-power mode
    sib.close()
    sys.exit()


# The SIB now measures a voltage under different frequency excitations. Internally,
# the results are written to a buffer. When the buffer is full, the SIB will send 
# the entire buffer back to the HOST. We use two different functions to monitor this:
#    sib.data_waiting() - Which checks the serial receive buffer for wating data
#    sib.read_sweep-response() - Which reads the data waiting in the receive buffer,
#                   which may be measured data or it may be the 'sweep complete' signal.

# Flag to break from the while loop
sweep_complete = False

# Create a list to store the 12-bit conversion results
conversion_results = list()

while not sweep_complete:
    # We will loop until the frequency sweep is complete
    if sib.data_waiting() > 0:
        # Data of some kind is waiting in the serial receive buffer

        # We will read the data sent from the SIB. The function returns two different
        # values. The ack_msg a string used to tell if the sweep is complete. It will be
        # either "ok" or "send_data". The second variable is tmp_bytes
        # which is a byte string representing the individual measurements.
        ack_msg, tmp_data = sib.read_sweep_response()

        if ack_msg == 'ok':
            # SIB has send the sweep complete command.
            sweep_complete = True
        elif ack_msg == 'send_data':
            # SIB is sending measurement data. Add it to the conversion results array
            conversion_results.extend(tmp_data)
        else:
            # Received an unexpected command. Something is wrong.
            sib.close()
            sys.exit()

    else:
        # This is where you put code to check if the user would like to stop the sweep
        # or anything else.
        time.sleep(0.01)

# After the sweep is complete, the list CONVERSION_RESULTS holds the 12-bit ADC codes
# that were received from the SIB. These are then ready to be further processed, written
# to a file, etc.
        
# Put the SIB back into the low-power mode
sib.sleep()

# Close the serial connection
sib.close()

print('Test complete.')

print('\n\n')


