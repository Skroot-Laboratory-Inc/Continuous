# Introduction

This document describes the general philosophy behind the communication structure between the host computer and the SIB350 board.

[[_TOC_]]

# Overview of Operation

Upon initialization, the SIB starts out in the low-power mode. In this mode, all voltage regulators are disabled and the DDS is powered off. This is done so that if the SIB cannot successfully initialize the DDS, it can send the associated error back to the HOST. The voltage regulators are enabled, and the DDS is configured, after the host sends the `SYSTEM WAKE` command. If the HOST attempts to initiate a frequency sweep while the system is in the low-power mode, then the SIB will respond with `FAIL`, and the error LED will be illuminated. 

In the event that the system responds with a `FAIL` acknowledgment, the payload will contain the corresponding error code. Additional information of the meaning of each error code can be found below. In addition, the system will illuminate the error LED, which will remain illuminated until the HOST issues the next command. At this point, the system will turn the error LED off.

# Communication Protocol

The system utilizes a simple receive/acknowledgment communication protocol. For every command sent by the HOST, the system will send an acknowledgment packet. The HOST should not send another command until after receiving the correct acknowledgment from the SIB. All communication is initiated by the HOST. The SIB will never perform any actions without direct command fro the HOST.

All commands and acknowledgments are 8-bytes in length and are sent MSB first. The The top 4 bytes contain the command/acknowledgment code. The bottom 4 bytes contain the payload, which is always a 32-bit integer.

The following is a list of all valid commands, their expected payloads, and a short description. It is the Command Code that is sent to the SIB in the command packet.

### Send Start Frequency Tuning Word

* Command Code: `!C01` (0x21433031)
* Command Payload: The 32-bit frequency tuning word for the start frequency.
* Expected Acknowledgment: `OK`. The payload will contain the value of start FTW written to the DDS.
* Possible Error Acknowledgment: None
* Description: Sends the frequency tuning word representing the start frequency to the SIB.

### Send the Stop Frequency Tuning Word

* Command Code: `!C02` (0x21433032)
* Command Payload: The 32-bit frequency tuning word for the stop frequency.
* Expected Acknowledgment: `OK`. The payload will contain the value of stop FTW written to the DDS.
* Possible Error Acknowledgment: None
* Description: Sends the frequency tuning word representing the stop frequeny to the SIB.

### Send the Number of Sweep Points

* Command Code: `!C03` (0x21433033)
* Command Payload: The 32-bit value representing the number of frequency sweep points to use.
* Expected Acknowledgment: `OK`. The payload will contain the number of points written to the SIB.
* Possible Error Acknowledgment: None
* Description: Sends the number of frequency sweep points to use in the frequency sweep. The number of points are evenly spaced between start_FTW and stop_FTW, inclusive.

### Send the Amplitude Scale Factor

* Command Code: `!C04` (0x21433034)
* Command Payload: The 14-bit amplitude scale factor.
* Expected Acknowledgment: `OK`. The payload will contain the ASF written to the DDS.
* Possible Error Acknowledgment: None
* Description: Sets the amplitude of the output of the DDS between 0 mA and 31.6 mA. in general, this value should always be set to the maximum value of 31.6 mA.

### Get the Firmware Version Number

* Command Code: `!C70` (0x21433730)
* Command Payload: None - Should be all 0
* Expected Acknowledgment: `OK`. The payload will contain the version number of the firmware running on the SIB. The payload is contained in bytes [3:0] of the acknowledgment packet.

    * Byte[3] = 0x00
    * Byte[2] = Major version number
    * Byte[1] = Minor version number
    * Byte[0] = Patch version number

* Possible Error Acknowledgment: None
* Description: Requests the version number of the firmware currently running on the SIB.


### Start a Frequency Sweep

* Command Code: `!C80` (0x21433830)
* Command Payload: None - Should be all 0
* Expected Acknowledgment: `SEND DATA` or `OK`. If `SEND DATA` is received, the payload contains the number of bytes of data that will immediately follow. If `OK` is received, the payload will contain the total number of bytes sent to the HOST during the frequency sweep.
* Possible Error Acknowledgment: If the system is still in the low-power mode when a frequency sweep is initiated the system will respond with `FAIL`.
* Description: Initiates a frequency sweep.

### Handshake

* Command Code: `!C91` (0x21433931)
* Command Payload: A 32-bit number.
* Expected Acknowledgment: `OK`. The payload will contain the oritinal 32-bt number sent by the HOST.
* Possible Error Acknowledgment: None
* Description: Performs a simple handshake with the SIB.

### Place System into Low-Power Mode

* Command Code: `!C92` (0x21433932)
* Command Payload: None - Should be 0
* Expected Acknowledgment: `OK`. The payload is don't care and should be all 0.
* Possible Error Acknowledgment: None
* Description: This command disables all of the voltage regulators on the SIB350 board and sets all MCU GPIO pins to LOW. This mode is indicated visually by a slow flashing power LED. \
\
While in the low-power mode, the system will still respond to the following commands: `set_start_FTW`, `set_stop_FTW`, `set_num_sweep_pts`, `set_amplitude`, `get_version_number`, `handshake`, and `system_wake`. \
\
The SIB350 must receive the `system_wake` command before it is able to perform a frequency sweep.

### Wake System from Low-Power Mode

* Command Code: `!C93` (0x21433933)
* Command Payload: None - Should be 0
* Expected Acknowledgment: `OK`. The payload is don't care and should be all 0.
* Possible Error Acknowledgment: If the DDS fails to initialize, then the system will respond with `FAIL`.
* Description: Wakes the SIB from the low-power sleep mode by enabling all of the voltage regulators and initializing the DDS with the default setup. This is indicated visually by a steady ON power LED. Please allow 10 ms for all supply voltages to stabilize before initiating a frequency sweep.

### Remotely Reset the System

* Command Code: `!CRR` (0x21435252)
* Command Payload: None - Should be 0
* Expected Acknowledgment: `OK`. The playload is don't care and should be all 0.
* Possible Error Acknowledgment: None
* Description: This command will fully reset the SIB350 board.


## Acknowledgment Packet Structure

The acknowledgment packet is 8-bytes in size. Byte [7] is the most significant byte, which is sent first to the SIB.

* Bytes [7:4] contain the 4-byte acknowledgment code
* Bytes [3:0] ontain the acknowledgment payload

The SIB will send one of the following acknowledgement codes:

### OK

* Acknowledgment Code: `!AA0` (0x21414130)
* Acknowledgment Payload: A 32-bit value that is dependant upon the command that was just executed.
* Description: Indicates a successful execution of the command received from the HOST.

### SEND DATA

* Acknowledgment Code: `!ASD` (0x21415344)
* Acknowledgment Payload: A 32-bit value that represents the number of bytes of data that will follow. The very next transmission from the SIB will be the indicated number of bytes of data.
* Description: Allows the SIB to tell the HOST that it will be sending data. The SIB should always be sending an even number of bytes. This is because each measurement is 10-bits in size and so is split btween two consecutive bytes. The first byte contains bits [9:8] of the measrement data and the second byte contains bites [7:0] of the measurement data.

### ERROR

* Acknowledgment Code: `!AFF` (0x21414646)
* Acknowledgment Payload: A 32-bit error code that indicates the type of error that occurred.
* Description: Indicates that an error occurred during the execution of the command received from the HOST. The payload will contain the error code describing the type of error that occurred.

A list error codes with their meaning is included below:

* 0x21454141 (`!EAA`) - Invalid command received by the SIB
* 0x21454242 (`!EBB`) - Error configuring the DDS. This can be either the registers were not successfully configured, or the PLL did not lock within the allotted time.
* 0x21454341 (`!ECA`) - The volage regulators are not enalbed and the HOST has tried to initiate a frequency sweep. This most likely means that the system is still in the low-power mode.
