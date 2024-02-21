# Overview

This package contains the complete API for interfacing with the 350 Mhz Skroot Sensor Interface Board (SIB350) via USB.

The package can be installed with: `pip instal sibcontrol`

# Documentation

For API documentation and usage, see files in the `sibcontrol/documentation` directory.

# Software Requirements

This package was developed using the following software versions:

* Python v3.11.2
* pySerial v3.5 -- The `sibcontrol` package requires `pySerial`. If it is not alredy installed, it will be automatically installed when the `sibcontrol` package is installed.

# Revision History

### Version 2.1.x

On 02/20/2024 the following changes were made:

* Added a function to print a human-readible message for each error code received by the SIB during a FAIL acknowledgment
* Updated the version to v2.1.2

On 02/20/2024 the following changes were made:

* Updated the WAKE command function to check for an error return. It now throws an SIBACKException in the event if the ACK is FAIL.
* Updated documentation.
* Updated the version to v2.1.1

On 02/15/2024 the following changes were made:

* Added a system reset command to the list of host commands
* Updated the command_list and the sibcontrol_api documentation to include the new command.
* Updated the `example.py` script to demonstrate that the SIB must be put into the active state before a frequency sweep can be performed.
* Updated the version number to 2.1.0

### Version 2.0.x

On 11/14/2023 the following changes were made:

* The documentation was updated to include a description of the communication protocol.
* All valid commands and acknowledgements have been described in the documentation.


On 10/27/2023 the following changes were made:

* Major version change was caused by updates to the read_sweep_response(). It used to return the ADC results as a byte, where each 12-bit ADC code was spread over 2 bytes. Now, the 12-bit ADC code is returned as an integer. No combining is necessary because it is performed inside of the class.
* Added two new commands: `system_wake` and `system_sleep` to the class. Also added two new methods `wake()` and `sleep()` to the class for sending these commands to the SIB.
* Updated all SIB350 methods to responds more accurately to the types of acknowledgmeent codes that are possible.
* Updated all SIB350 methods to return the payload received from the device for all relevent commands.
* Updated documentation
* Bumped version to v2.0.0

### Version 1.0.x

On 10/17/2023 the following changes were made:

* Fixed error when calculating amplitude scale factor from mA.
* Bumped version to 1.0.3.

On 10/15/2023 the following changes were made:

* Updated the \_\_init\_\_.py files, in both sibcontrol and ncomm, to clean up how the packages are imported.
* Added the MIT open source license file to the `ncomm` subpackage. This license does not apply to the general `sibcontrol` package.
* Added the `pyproject.toml` file to enable installation of the package using `pip`
* Bumped version to 1.0.2.

On 9/26/2023 the following changes were made:

* Made ncomm a sub-package
* Bumped version to 1.0.1

On 9/26/2023 the following changes were made:

* Version 1.0.0 was released.


