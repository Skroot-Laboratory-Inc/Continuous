# Introduction

This document describes the general philosophy behind the communication structure between the host computer and the SIB350 board.

[[_TOC_]]


# Host-to-SIB Commands

The following is a list of all of the valid commands that the host can send to the SIB.

## Send the Start Frequency Tuning Word

* Command Name: `send_start_ftw`
* Command Code: `!C01`
* Command Payload: The 32-bit frequency tuning word for the start frequency.
* Expected Acknowledgment: `OK` with the value written to the DDS as the payload.
* Description: Sends the frequency tuning word representing the start frequency to the SIB.

## Send the Stop Frequency Tuning Word

* Command Name: `send_sstop_ftw`
* Command Code: `!C02`
* Command Payload: The 32-bit frequency tuning word for the stop frequency.
* Expected Acknowledgment: `OK` with the value written to the DDS as the payload.
* Description: Sends the frequency tuning word representing the stop frequeny to the SIB.

## Send the Number of Sweep Points

* Command Name: `send_num_pts`
* Command Code: `!C03`
* Command Payload: The 32-bit value representing the number of frequency sweep points to use.
* Expected Acknowledgment: `OK` with the number of sweep points as the payload.
* Description: Sends the number of frequency sweep points to use in the frequency sweep. The number of points are evenly spaced between start_FTW and stop_FTW, inclusive.

### Send the Amplitude Scale Factor

* Command Name: `send_asf`
* Command Code: `!C04`
* Command Payload: The 14-bit amplitude scale factor.
* Expected Acknowledgment: `OK` with the value of ASF written to the DDS as the payload.
* Description: Sets the amplitude of the output of the DDS between 0 mA and 31.6 mA.

### Get the Firmware Version Number

* Command Name: `get_version`
* Command Code: `!C70`
* Command Payload: None - Should be all 0
* Expected Acknowledgment: `OK` with the version number containing in bytes <1>, <2>, and <3> of the payload.
* Description: Requests the version number of the firmware currently running on the SIB.


## Start a Frequency Sweep

* Command Name: `start_test`
* Command Code: `!C80`
* Command Payload: None - Should be all 0
* Expected Acknowledgment:
* Description:

## Stop a Frequency Sweep

* Command Name: `stop_test`
* Command Code: `!C81`
* Command Payload: None - Should be 0
* Expected Acknowledgment:
* Description:

## Handshake

* Command Name: `handshake`
* Command Code: `!C91`
* Command Payload: A 32-bit number.
* Expected Acknowledgment:
* Description:

## Place System into Low-Power Mode

* Command Name: `system_sleep`
* Command Code: `!C92`
* Command Payload: None - Should be 0
* Expected Acknowledgment:
* Description:

## Wake System from Low-Power Mode

* Command Name: `system_wake`
* Command Code: `!C93`
* Command Payload: None - Should b 0
* Expected Acknowledgment:
* Description:


