# SIB350 Class
[[_TOC_]]

## Attributes

The SIB350 class has the following attributes. The values stored in the attributes are communicated to the SIB before a frequency sweep is initiated.

### start_MHz

* getter: Get the start frequency in MHz. 
* setter: Set the start frequency in MHz. 
* valid range: 0 to 350 MHz
* type: int or float

### stop_MHz

* getter: Get the stop frequency in MHz
* setter: Set the stop frequency in MHz
* valid range: 0 to 350 MHz
* type: int or float

### amplitude_mA

* getter: Get the DDS output signal amplitude in mA
* setter: Set the DDS output signal amplitude in mA
* valid range: 0 mA to 31.6 mA
* type: int or float

## num_pts

* getter: Get the number of sweep points
* setter: Set the number of sweep points
* valid range: 1 to (2^32 - 1)
* type: int




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
* Exceptions: SIBConnectionError - Unable to retrieve the number of bytes.
* Description: Returns the number of bytes waiting in the input buffer sent by the SIB.

<hr>

The following methods are used to communicate the configuration data to the SIB.

### write_start_ftw()

* Parameters: None
* Return Arguments: Returns the actual start_FTW written to the DDS that is received from the device.
* Return Type: int
* Exceptions:  None
* Description: Writes the 32-bit start frequency as an FTW to the SIB. The host then waits for the SIB to acknowledge and returns the value written to the DDS.

### write_stop_ftw()

* Parameters: None
* Return Arguments: Returns the actual stop_FTW written to the DDS that is received from the device.
* Return Type: int
* Exceptions:  None
* Description: Writes the 32-bit stop frequency as an FTW to the SIB. The host then waits for the SIB to acknowledge and returns the vlaue written to the DDS.

### write_asf()

* Parameters: None
* Return Arguments: Returns the actual ASF written to the DDS that is received from the device.
* Return Type: int
* Exceptions:  None
* Description: Writes the 14-bit amplitude scale factor to the SIB. The host then waits for the SIB to acknowledge and returns the value written to the DDS.

### write_num_pts()

* Parameters: None
* Return Arguments: Returns the actual number of sweep pionts written to the DDS that is received from the device.
* Return Type: int
* Exceptions:  None
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
* Exceptions: None
* Description: Calling this method performs a handshake operation with the SIB. The host sends a 32-bit value to the SIB along with the handshake command code. The SIB then responds with an OK acknowledgment and sends the same 32-bit value back to the host.

### version()

* Parameters: None
* Return Arguments: Returns the version number of the firmware running on the SIB as XX.YY.ZZ
* Return Type: str
* Exceptions: None
* Description: Requests the firmware version number from the SIB. The version is returned as XX.YY.ZZ where XX is the major version number, YY is the minor version number, and ZZ is the patch number. 

### sleep()

* Parameters: None
* Return Arguments: None
* Exceptions: None
* Description: Puts the SiB into a low-power sleep mode by disabling all of the voltage regulators. This mode is indicated visually by a blinking of the power LED. \
\
While in the low-power sleep mode, the system will still respond to the following commands: set_start_FTW, set_stop_FTW, set_num_sweep_pts, set_amplitude, get_version_number, handshake, and sib_wake. \
\
If the system is in the low-power sleep mode, the self.wake() command must be called before any frequeny sweep can be started.

### wake()

* Parameters: None
* Return Arguments: None
* Exceptions: None
* Description: Wakes the SiB from the low-power sleep mode. Once this command has been sent, the SiB enables all voltage regulators and re-initializes the DDS into the default starting state. This is indicated visually by a steady ON power LED.

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

    * SIBExeption - Received the SEND_DATA acknowledgment code but the number of bytes to receive is not an even number. This value must be an even number because each 12-bit measurement value is transmitted to the HOST in two bytes.
    * SIBACKException - Received the FAIL acknowledgment.
    
* Description: Reads the device acknowledgment after the start sweep command has been sent by the host. The SIB will acknowledge in one of three ways: OK, SEND_DATA, or FAIL. If the OK acknowledgment was received, the sweep is complete. If the SEND_DATA acknowledgment is received, then the method reads the specified number of bytes from the device before returning. If the FAIL acknowledgment is received, then the system raised as SIBACKException which includes the error code. This is a blocking function. Use the data_waiting() method to check for data before calling this method if a non-blocking behavior is desired.



