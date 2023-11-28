import serial
from .packet import Packet


class NCommException(IOError):
    '''Base exception class for the communication related exceptions.'''

class NCommConnectionError(NCommException):
    '''Exception raised when system tries to read/write and port is not open.'''

class NCommTimeout(NCommException):
    '''Exception raised for read and write timeouts.'''


class NCommUSBCDC:
    """
    A class used to represent the NComm communication protocol.

    Attributes
    ----------
    com_port : str
        The COM port used to connect to the device
    command_packet : Packet
        Packet object to hold the command names and command codes
        that are sent to the device.
    ack_packet : Packet
        Packet object to hold the ACK names and the ACK codes
        that are received from the device.

    Methods
    -------
    connect()
        Opens a connection to the device on com_port
    disconnect()
        Closes the connection to the device on com_port
    write_packet(command_name, data)
        Writes a single command packet to the device with
        data as the payload.
    read_packet()
        Reads a single acknowledgment packet from the device.
    read_data(num_bytes)
        Reads num_bytes of data from the device.
    in_waiting()
        Returns the number of bytes waiting in the serial read
        buffer.
    """

    def __init__(self,
                 com_port: str,
                 read_timeout: float = None,
                 write_timeout: float = None
                 ):
        """
        Parameters
        ----------
        com_port : str
            The COM port used to communicate with the device
        read_timeout : float
            The number of seconds before a read operation times
            out (default is 10 seconds).
        write_timeout : float
            The number of seconds before a write operation times
            out (default is 10 seconds).
        """
        
        if not isinstance(com_port, str):
            raise TypeError('COM Port must be entered as a string.')
        else:
            self._ser = serial.Serial()
            self._ser.port = com_port
            self.com_port = com_port

        # Set the read timeout
        if read_timeout is None:
            self._ser.timeout = 10          # Defaults to 10 seconds
        else:
            try:
                read_timeout = float(read_timeout)
            except ValueError:
                raise ValueError('Read timeout must be a number.')
            else:
                self._ser.timeout = read_timeout

        # Set the write timeout
        if write_timeout is None:
            self._ser.write_timeout = 10    # Defaults to 10 seconds
        else:
            try:
                write_timeout = float(write_timeout)
            except ValueError:
                raise ValueError('Write timeout must be a number.')
            else:
                self._ser.write_timeout = write_timeout

        self._ser.timeout = 10          # Read timeout in seconds
        self._ser.write_timeout = 10    # Write timeout in seconds

        # The Packet object to hold the host-to-device commands.
        self.command_packet = None

        # The Packet object to hold the device-to-host commands
        self.ack_packet = None
    

    def connect(self):
        """
        Opens a serial connection to the device on COM port.

        Parameters
        ----------
        None

        Raises
        ------
        NCommException
            If the command packet or ACK packet is not initialized
        NCommConnectionError
            If the device is unable to be opened on COM port.

        Returns
        -------
        None
        """

        if self.command_packet is None:
            raise NCommException('Host packet has not been initialized. Cannot connect to device.')
        
        if self.ack_packet is None:
            raise NCommException('Host packet has not been initialized. Cannot connect to device.')
        
        # Only try to open the port if it is not already open
        if not self._ser.is_open:
            try:
                self._ser.open()
            except serial.SerialException:
                raise NCommConnectionError('Could not open port {}.'.format(self._ser.port)) from None
    

    def disconnect(self):
        """
        Closes the serial connection with the device.

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        None
        """

        self._ser.close()

    
    def write_packet(self,
                     command_name: str,
                     data: int
                     ):
        """
        Writes a single command packet to the device with the value
        stored in DATA as the payload.

        Parameteres
        -----------
        command_name : str
            The human-readible name given to the command to write
        data : int
            The payload to include with the command packet.

        Raises
        ------
        NCommConnectionError
            If the serial connection is not open.
        NCommTimeout
            If the write operation times out.

        Returns
        -------
        None
        """

        # Ensure that the device is connected
        if not self._ser.is_open:
            raise NCommConnectionError('Device not connected. Cannot write packet.')
        
        # Get the packet size
        command_size, payload_size = self.command_packet.size
        packet_size = command_size + payload_size

        # Format the payload
        payload = int(data).to_bytes(payload_size, 'big')

        # Get the desired command code
        command_code = self.command_packet.command_from_name(command_name)

        # Write packet and check that the correct number of bytes has been written
        try:
            self._ser.write(bytes(command_code + payload))
        except serial.SerialTimeoutException:
            raise NCommTimeout('Write operation timed out.') from None
        


    def read_packet(self):
        """
        Reads a single acknowledgment packet from the device. The packet
        is then parsed into the acknowledgment message and the payload.

        Parameters
        ----------
        None

        Raises
        ------
        NCommConnectionError
            If serial connection is not open.
        NCommTimeout
            If the read operation times out.

        Returns
        -------
        tuple(ack_msg, rx_payload)
       
        ack_msg : str
            The human readible identifier of the acknowledgment code
        rx_payload : int
            The payload received from the device.
        """

        # Ensure that the device is connected
        if not self._ser.is_open:
            raise NCommConnectionError('Device not connected. Cannot read packet.')
        
        # Get the packet size
        command_size, payload_size = self.ack_packet.size
        packet_size = command_size + payload_size

        # Wait for the packet from the device
        raw_packet = self._ser.read(packet_size)

        # Check for read timeout
        if len(raw_packet) != packet_size:
            raise NCommTimeout('Read operation timed out.')
        
        # Extract the ACK name from the received ACK code
        rx_code = raw_packet[:command_size]
        rx_payload = raw_packet[payload_size:]

        # Get the ACK message
        ack_msg = self.ack_packet.name_from_command(rx_code)

        return (ack_msg, int.from_bytes(rx_payload, 'big'))


    def read_data(self,
                  num_bytes: int    # Number of bytes to receive
                  ) -> bytes:
        """
        Reads data from the device. This function should only be called
        after a SEND_DATA acknowledgment. Otherwise, the method read_packet
        should be used.

        Parameters
        ----------
        num_bytes : int
            The number of bytes to receive

        Raises
        ------
        NCommConnectionError
            If the serial connection is not open.
        NCommTimeout
            If the write operation times out.

        Returns
        -------
        rx_data : bytes
            The array containing the received data as bytes
        """
        # Ensure that the device is connected
        if not self._ser.is_open:
            raise NCommConnectionError('Device not connected. Cannot read data.')
        
        # Wait for the specified number of bytes
        rx_data = self._ser.read(num_bytes)

        # Check for read timeout
        if len(rx_data) != num_bytes:
            raise NCommTimeout('Read operation timed out when reading data.')
        
        return rx_data
    

    def in_waiting(self) -> int:
        """
        Returns the number of bytes waiting in the serial read buffer.

        Parameters
        ----------
        None

        Raises
        ------
        NCommConnectionError
            If the system is unable to read the number of available bytes

        Returns
        -------
        bytes_waiting : int
            The number of bytes waiting to be read. A value of 0 indicates
            that there is no data waiting to be read.
        """

        try:
            bytes_waiting = self._ser.in_waiting
        except serial.SerialException:
            raise NCommConnectionError('Unable to get the number of bytes in the serial buffer.') from None
        else:
            return bytes_waiting




