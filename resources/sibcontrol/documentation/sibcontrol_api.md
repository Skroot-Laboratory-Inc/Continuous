# SIB350 Class
[[_TOC_]]

## Attributes

The SIB350 class has the following attributes. The values stored in the attributes are communicated to the SIB before a frequency sweep is initiated.

### start_MHz

* getter: Get the start frequency in MHz. 
* setter: Set the start frequency in MHz. 
* valid range: 0 to 350 MHz
* type: int or float
* Exceptions raised by setter:

    - TypeError - The value must be either `int` or `float`
    - ValueError - The value is out of valid range.

### stop_MHz

* getter: Get the stop frequency in MHz
* setter: Set the stop frequency in MHz
* valid range: 0 to 350 MHz
* type: int or float
* Exceptions raised by setter:

    - TypeError - The value must be either `int` or `float`
    - ValueError - The value is out of valid range.

### amplitude_mA

* getter: Get the DDS output signal amplitude in mA
* setter: Set the DDS output signal amplitude in mA
* valid range: 0 mA to 31.6 mA
* type: int or float
* Exceptions raised by setter:

    - TypeError - The value must be either `int` or `float`
    - ValueError - The value is out of valid range.

## num_pts

* getter: Get the number of sweep points
* setter: Set the number of sweep points
* valid range: 1 to (2^32 - 1)
* type: int
* Exceptions raised by setter:

    - TypeError - The value must be either `int`
    - ValueError - The value is out of valid range.




## Methods

The SIB350 class has the following methods. The following methods are used for communication with the SIB.

### __init__(com_port)

* Parameters: str com_port - The COM port that is used to connect to the SIB board.
* Returns: None
* Exceptions: None
* Description: Initializes the SIB350 object with the associated COM port.

### open()

* Parameters: None
* Return: None
* Exceptions: SIBConnectionError - Cannot open device on the specified COM port.
* Description: Opens a serial connection to the device.

### close()

* Parameters: None
* Return: None
* Exceptions: None
* Description: Immediately disconnects from the device.

### data_waiting()

* Parameters: None
* Returns: The number of bytes waiting in the input buffer.
* Return Type: int
* Exceptions: SIBConnectionError - There is a problem with the serial connection.
* Description: Returns the number of bytes waiting in the input buffer sent by the SIB.

### is_open()

* Parameters: None
* Return: Returns state of the serial port
* Return Type: bool
* Exceptions: None
* Description: Returns True if the serial connection is open. Returns False otherwise.

### reset_input_buffer()

* Parameters: None
* Return: None
* Exceptions: None
* Description: Resets the input buffer and discards all data contained therein.

### reset_output_buffer()

* Parameters: None
* Return: None
* Exceptions: None
* Description: Resets the output buffer, aborting the current output, and discards all data contained therein.

<hr>

The following methods are used to communicate the configuration data to the SIB.

### write_start_ftw()

* Parameters: None
* Return Arguments: Returns the actual start_FTW written to the DDS that is received from the device.
* Return Type: int
* Exceptions:  

    - ValueError - The DDS configuration data is not within valid range.
    - SIBError - The host received an unexpected acknowledgment code.

* Description: Writes the 32-bit start frequency as an FTW to the SIB. The host then waits for the SIB to acknowledge and returns the value written to the DDS.

### write_stop_ftw()

* Parameters: None
* Return Arguments: Returns the actual stop_FTW written to the DDS that is received from the device.
* Return Type: int
* Exceptions:  

    - ValueError - The DDS configuration data is not within valid range.
    - SIBError - The host received an unexpected acknowledgment code.

* Description: Writes the 32-bit stop frequency as an FTW to the SIB. The host then waits for the SIB to acknowledge and returns the vlaue written to the DDS.

### write_asf()

* Parameters: None
* Return Arguments: Returns the actual ASF written to the DDS that is received from the device.
* Return Type: int
* Exceptions: SIBError - The host received an unexpected acknowledgment code.
* Description: Writes the 14-bit amplitude scale factor to the SIB. The host then waits for the SIB to acknowledge and returns the value written to the DDS.

### write_num_pts()

* Parameters: None
* Return Arguments: Returns the actual number of sweep pionts written to the DDS that is received from the device.
* Return Type: int
* Exceptions: 

    - ValueError - The DDS configuration data is not within valid range.
    - SIBError - The host received an unexpected acknowledgment code.

* Description: Writes the 32-bit number of frequency sweep points to the SIB. The host then waits for the SIB to acknowledge and returns the value written to the DDS.

### valid_config()

* Parameters: None
* Return Arguments: Returns True if the configuration data stored in the SIB350 object is valid. Returns False if the configuration data stored in the SIB350 object is not valid.
* Return Type: bool
* Exceptions: None
* Description: Calling this function checks that the configuration data stored in the SIB350 object is valid, beyond the simple limits set by the setter functions. This function checks that the following conditions are satisfied:
    * start frequency < stop frequency
    * num_pts < stop_FTW - start_FTW

<hr>

The following methods are used for executing the various functionality of the SIB.

### handshake(data)

* Parameters: int data - A 32-bit number that is sent to the SIB and then echoed back to the host.
* Return Arguments: The 32-bit value received from the SIB. This value should be the same as the 32-bit value sent to the SIB.
* Return Type: int
* Exceptions: 

    - TypeError - The data sent to the SIB must be an integer.
    - ValueError - The handshake data is out of range. The value must be less than (2^32 - 1)
    - SIBError - The host received an unexpected acknowledgment code.

* Description: Calling this method performs a handshake operation with the SIB. The host sends a 32-bit value to the SIB along with the handshake command code. The SIB then responds with an OK acknowledgment and sends the same 32-bit value back to the host.

### version()

* Parameters: None
* Return Arguments: Returns the version number of the firmware running on the SIB as XX.YY.ZZ
* Return Type: str
* Exceptions: SIBError - The host received an unexpected acknowledgment code.
* Description: Requests the firmware version number from the SIB. The version is returned as XX.YY.ZZ where XX is the major version number, YY is the minor version number, and ZZ is the patch number. 

### sleep()

* Parameters: None
* Return Arguments: None
* Exceptions: SIBError - The host received an unexpected acknowledgment code.
* Description: Puts the SiB into a low-power sleep mode by disabling all of the voltage regulators. This mode is indicated visually by a blinking of the power LED. \
\
While in the low-power sleep mode, the system will still respond to the following commands: set_start_FTW, set_stop_FTW, set_num_sweep_pts, set_amplitude, get_version_number, handshake, and sib_wake. \
\
If the system is in the low-power sleep mode, the self.wake() command must be called before any frequeny sweep can be started.

### wake()

* Parameters: None
* Return Arguments: None
* Exceptions: 

    - SIBDDSConfigError - The DDS was not correctly configured after waking up. 
    - SIBError - The host received an unexpected acknowledgment code or an unexpected error code.

* Description: Wakes the SiB from the low-power sleep mode. Once this command has been sent, the SiB enables all voltage regulators and re-initializes the DDS into the default starting state. This is indicated visually by a steady ON power LED.

### reset_sib()

* Parameters: None
* Return Arguments: None
* Exceptions: None
* Description: Sends a command to the SIB to tell it to perform a power-on reset. The system will send the `OK` acknowledgment before resetting.

### write_sweep_command()

* Parameters: None
* Return Arguments: None
* Exceptions: None
* Description: Sends the start sweep command to the SIB. This command must be called to initiate a single frequency sweep. In order to get the resulting data from the SIB the read_sweep_response() method should be used.

### read_sweep_response()

* Parameters: None
* Return Arguments: A tuple containing the acknowlegement message and the measurement data.
* Return Type: tuple[str, int]
* Exceptions: 

    - SIBRegulatorNotReadyError - The voltage regulators are not enabled on the SIB.
    - SIBError - The number of bytes received from the SIB was not an even number. Every measurement is two bytes in size. This exception is also raised if the host receives an unexpected acknowledgment or error code.
    
* Description: Reads the device acknowledgment after the start sweep command has been sent by the host. The SIB will acknowledge in one of three ways: OK, SEND_DATA, or FAIL. If the OK acknowledgment was received, the sweep is complete. If the SEND_DATA acknowledgment is received, then the method reads the specified number of bytes from the device before returning. If the FAIL acknowledgment is received, then the system raised as SIBACKException which includes the error code. This is a blocking function. Use the data_waiting() method to check for data before calling this method if a non-blocking behavior is desired.


## Exceptions

### exception SIBException

Base class for SIB exceptions. All other SIB exceptions are derived from this class.
Derived from the built in Exception class.

### exception SIBConnectionError

There is an error with the connection between the host and the SIB. Either the port is not open or the port is open, but the SIB was unexpectedly reset invalidating the connection with the host.

### exception SIBTimeoutError

Either the read or write function timed out.

### exception SIBError

This exception is raised when the host detects unexpected behavior from the SIB. Generally, this exception will indicate serious problems with the current state of the SIB and the SIB should be reset. For example, this exception will be raised if the host receives an acknowledgment message tht is not `OK` when the SIB function call should only every respond with `OK`.

### exception SIBACKException

Base class for all acknowledgment-related exceptions. These are generally raised when the host receives a `FAIL` acknoweledgement from the SIB.

### exception SIBInvalidCommandError

The SIB received an invalid command from the host.

### exception SIBDDSConfigError

The DDS was not correctly initialized after the host issues the wake command

### exception SIBRegulatorsNotReadyError

The host is trying to start a frequency sweep, but the voltage regulators are not enabled. Generally, this implies that the SIB is in the sleep state and the host must first call the wake command.


## Error Handling and Serial Connection Problems

One issue that has been observed is that the SIB becomes disconnected from the serial port during operation, causing the host to loose the ability to communicate with the SIB. The problem occurs when the host calls `SIB350.open()` upon initialization. When the SIB looses its connection to the serial port, the host still detects the connection as being open (i.e., calls to SIB350.is_open() will retur True), but any calls to `SIB350._write_packet()` or `SIB350._read_packet()` will not be able to write or read any data and will raise a serial.SerialException. In most cases this issue can be rectified by simply closing, then re-opening the serial connection.

To address this, v2.2.0 of `sibcontrol` has been updated so that if the serial connection between the host and SIB has been interrupted, a `SIBConnectionError` exception will be raised. By catching this exception, the host can choose to close then re-open the connection and repeat the offending command.

Almost all commands from the SIB350 class call either `_write_packet()` or `_read_packet()` and must therefore be monitored for a corrupted serial connection. When re-opening the serial connection you must:

* Close the connection
* Sleep for at least 1.0 seconds. Failure to do this seems to cause problems when calling the open() command and the system will not be able to recover.
* Open the connection with a call to open()
* Resend all configuration data to the SIB
* Resend the command that raised the initial exception in the first place. 

For example, consider the following example where the serial connectin was interrupted before calling the `send_sweep_command()` function. For the following example, we will assume that the SIB is connected to the host on COM5, and the host is running Windows.

```python
import sibcontrol
import time

sib = sibcontrol.SIB350('com5')     # Called during host application initialization.

try:
    sib.open()
    sib.write_start_ftw()
    sib.write_stop_ftw()
    sib.write_num_pts()
    sib.write_asf()
except sibcontrol.SIBConnectionError:
    # Handle the exception in whatever way is appropriate.
    # Here I am exiting for sake of example.
    sys.exit('Problem during initialization')
```

Now the call to `write_sweep_command()` raises the SIBConnectionError exception.

```python
try:
    sib.write_sweep_command()
except sibcontrol.SIBConnectionError:
    # Problem with serial connection. Close and then re-open.
    if sib.is_open():
        sib.close()         # Host thinks connection is open, so close it
        time.sleep(1.0)     # Must delay at least 1.0 seconds before trying to re-open connection

    try:
        sib.open()

        # Resend all configuration data
        sib.write_start_ftw()
        sib.write_stop_ftw()
        sib.write_num_pts()
        sib.write_asf()

        # Resend the origintal command that failed
        sib.write_sweep_command()
    except sibcontrol.SIBException:
        # Handle the exception in whatever way is appropriate, however, any exception here indicates
        # a larger problem with the system. 
        # Here I am exiting for sake of example.
        sys.exit('Recovery failed')    
```

The above example can be adapted for any of the function calls that either read or write data to the SIB. While I haven't tested it, it might be a good idea to flush the input and output buffers before continuing.

## Error Handling and DDS Configuration Problems

The other problem that we have been encountering is the failure of the SIB to correctly configure the synthesizer. This occurs during a call to the `wake()` command and results in the `SIBDDSConfigError` exception. The general steps for dealing with this situation are as follows:

* Send the `reset_sib()` command to remotely reset the SIB.
* The host will likely need to sleep for some period of time while the SIB resets and re-initializes. I do not currently have an estimate for how long this takes.
* Close the serial connection
* Sleep for 1.0 seconds
* Open the serial connectoin
* Resend all of the configuration data
* Resend the `wake()` command

```python
# Assuming the same initialization as in the above example...

try:
    sib.wake()
except sibcontrol.SIBConnectionError:
    # Problem with the serial connection. Handle
    # similar to above example.
except sibcontrol.SIBDDSConfigError:
    # The DDS did not get configured correctly.

    # We will reset the SIB remotely, re-establish the serial connection, and then resend
    # all of the configuration data.
    try:
        # Reset the SIB
        sib.reset_sib()
        time.sleep()        # The host will need to wait until the SIB re-initializes. I do not know how long this takes.

        sib.close()
        time.sleep(1.0)

        sib.open()
        sib.write_start_ftw()
        sib.write_stop_ftw()
        sib.write_num_pts()
        sib.write_asf()

    except sibcontrol.SerialException:
        # Any error indicates larger problem. I simply exit as an example
        sys.exit('Problem resetting the SIB')

    # Now retry the wake() command
    try:
        sib.wake()
    except sibcontrol.SIBException:
        # Any SIB exception will cause this example to exit
        sys.exit('Still cannot wake system.')

```