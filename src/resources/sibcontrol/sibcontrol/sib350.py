from .ncomm import ncomm as ncomm
from .dds import AD9910
from .sibutils import (
    SIBConnectionError,
    SIBTimeoutError,
    SIBError,
    SIBDDSConfigError,
    SIBRegulatorsNotReadyError
)





class SIB350:
    """
    This class is used to represent the SIB350 System which
    utilizes the AD9910 DDS chip.

    Attributes
    ----------
    dds : AD9910
        Object to hold the limits and conversion methods for the DDS.
    start_MHz : float
        The start frequency in MHz
    stop_MHz : float
        The stop frequency in MHz
    amplitude_mA : float
        The DDS signam amplitude in mA
    num_pts : int
        The number of frequency points to include in the sweep.

    Methods
    -------
    open()
        Opens a serial connection to the device
    close()
        Closes the serial connection to the device
    data_waiting()
        Returns the number of bytes waiting in the read buffer
    is_open()
        Indicates if the serial port is open or not.
    reset_input_buffer()
        Clears the input buffer, discarding all data in the buffer.
    reset_output_buffer()
        Clears the output buffer, aborting the current output, discarding
        all data in the buffer.
    write_start_ftw()
        Writes the start frequency as an FTW to the device.
    write_stop_ftw()
        Writes the stop frequency as an FTW to the device.
    write_asf()
        Write the amplitude scale factor to the device.
    write_num_pts()
        Writes the number of points to the device.
    valid_config()
        Checks the configuration data stored in the SIB350 object and
        returns True if it is valid.
    handshake(data)
        Performs a handshake with the device sending DATA as the payload.
    version()
        Gets the firmware version number from the device.
    write_sweep_command()
        Starts a frequency sweep on the device
    read_sweep_response()
        After a frequency sweep has been started, this method is used
        to monitor the response from the device and to receive measurement
        data.
    """

    cmd_size = 4                # Size, in bytes, of the command portion of the command and ack packet
    payload_size = 4            # Size, in bytes, of the payload portion of the command and ack packet

   
    def __init__(self,
                 com_port: str
                 ):
        """
        Parameters
        ----------
        com_port : str
            The COM port used to connect to the device.
        """
        
        # Initialize the NComm structure
        self._comms = ncomm.NCommUSBCDC(com_port)
        self._comms.command_packet = ncomm.Packet(SIB350.cmd_size, SIB350.payload_size)
        self._comms.command_packet.command_dict = {'send_start_ftw' : b'!C01',
                                    'send_stop_ftw' : b'!C02',
                                    'send_num_pts' : b'!C03',
                                    'send_asf' : b'!C04',
                                    'get_version' : b'!C70',
                                    'start_test' : b'!C80',
                                    'stop_test' : b'!C81',
                                    'handshake' : b'!C91',
                                    'system_sleep' : b'!C92',
                                    'system_wake' : b'!C93',
                                    'reset' : b'!CRR'}
        
        self._comms.ack_packet = ncomm.Packet(SIB350.cmd_size, SIB350.payload_size)
        self._comms.ack_packet.command_dict = {b'!AA0' : 'ok',
                                    b'!ASD' : 'send_data',
                                    b'!AFF' : 'fail'}
        
        # Dictionary containing the error codes and meanings
        self._error_dict = {0x21454141 : 'invalid_command',
                       0x21454242 : 'dds_config_errr',
                       0x21454341 : 'regulators_not_ready'}
        
        # The start and stop frequencies are stored as 32-bit FTW
        self._start_FTW = 94.8
        self._stop_FTW = 145.0

        # The amplitude is stored as a 14-bit ASF
        self._asf = 31.6

        # The number of points used in the frequency sweep
        self._num_pts = 5021

        # Initialize the specific DDS configuration used by the sib
        self.dds = AD9910(min_freq = 0,                 # in MHz
                          max_freq = 350,               # in MHz
                          min_amplitude = 0,            # in mA
                          max_amplitude = 31.6,         # in mA
                          max_num_pts = 2**32 - 1,      # 32-bit value
                          sys_clk_freq = 1_000_000_000)



    @property
    def start_MHz(self):
        '''The start frequency in MHz.'''
        freq_Hz = self.dds.ftw_to_hz(self._start_FTW)
        return (freq_Hz / 1_000_000)


    @start_MHz.setter
    def start_MHz(self, freq_MHz):

        if not isinstance(freq_MHz, (int, float)):
            raise TypeError('Start frequency must be a number.')
        
        if self.dds.freq_MHz_in_range(freq_MHz):
            freq_hz = freq_MHz * 1_000_000
            self._start_FTW = self.dds.hz_to_ftw(freq_hz)
        else:
            raise ValueError('Start frequency is out of range.')
    

    @property
    def stop_MHz(self):
        '''The stop frequency in MHz.'''
        freq_Hz = self.dds.ftw_to_hz(self._stop_FTW)
        return (freq_Hz / 1_000_000)
    

    @stop_MHz.setter
    def stop_MHz(self, freq_MHz):

        if not isinstance(freq_MHz, (int, float)):
            raise TypeError('Stop frequency must be a number.')
        
        if self.dds.freq_MHz_in_range(freq_MHz):
            freq_Hz = freq_MHz * 1_000_000
            self._stop_FTW = self.dds.hz_to_ftw(freq_Hz)
        else:
            raise ValueError('Stop frequency is out of range.')
        
        
    @property
    def amplitude_mA(self):
        '''The full-scale current amplitude in mA.'''
        return self.dds.asf_to_ma(self._asf)
    

    @amplitude_mA.setter
    def amplitude_mA(self, amp_mA):

        if not isinstance(amp_mA, (int, float)):
            raise TypeError('Amplitude must be a number.')
        
        if self.dds.amp_mA_in_range(amp_mA):
            self._asf = self.dds.ma_to_asf(amp_mA)
        else:
            raise ValueError('Amplitude is out of range.')
    

    @property
    def num_pts(self):
        '''The number of points to use in the frequency sweep.'''
        return self._num_pts
    

    @num_pts.setter
    def num_pts(self, num_pts):

        if not isinstance(num_pts, int):
            raise TypeError('Number of points must be an integer.')
        
        if self.dds.num_pts_in_range(num_pts):
            self._num_pts = num_pts
        else:
            raise ValueError('Amplitude is out of range.')



    '''
    *********************************************************
    Private functions used to communicate with the MCU via the serial port.
    *********************************************************
    '''
    def _write_packet(self,
                      command_name: str,
                      data: int
                      ):
        # Wrapper for the NComm write_packet function with SIB
        # exceptions.

        try:
            self._comms.write_packet(command_name, data)
        except ncomm.NCommConnectionError:
            raise SIBConnectionError('Problem with connection to port {}. Cannot write packet.'.format(self._comms.com_port))
        except ncomm.NCommTimeout:
            raise SIBTimeoutError('Write operation timed out. Timeout is {}'.format(self._comms._ser.write_timeout)) from None


    def _read_packet(self):
        # Wrapper for the NComm read packet function with SIB
        # exceptions.
        
        try:
            msg, payload = self._comms.read_packet()
        except ncomm.NCommConnectionError:
            raise SIBConnectionError('Problem with connection to port {}. Cannot read packet.'.format(self._comms.com_port))
        except ncomm.NCommTimeout:
            raise SIBTimeoutError('Read operation timed out. Timeout is {}'.format(self._comms._ser.timeout)) from None
        
        return(msg, payload)
    

    def _read_data(self, num_bytes):
        '''Wrapper for the NComm read data function with
        SIB excpetions. Since this function is only called
        when reading impedance data, it converts the received
        data split across two bytes into one 12-bit integer
        '''
        
        try:
            data_as_bytes = self._comms.read_data(num_bytes)
        except ncomm.NCommConnectionError:
            raise SIBConnectionError('Problem with connection to port {}. Cannot read data.'.format(self._comms.com_port))
        except ncomm.NCommTimeout:
            raise SIBTimeoutError('Read data timed out. Timeout is {}'.format(self._comms._ser.timeout)) from None
        
        # The data is 12-it and split across two different bytes.
        # Reassemble the data and convert each value to a 12-bit
        # ADC output code as an integer.
        data = list()
        for i in range(0, len(data_as_bytes), 2):
            data.append(int().from_bytes(data_as_bytes[i:i+2], 'big'))

        return data




    '''
    *********************************************************
    Public functions used to communicate with the MCU via the serial port.
    *********************************************************
    '''
    def valid_config(self) -> bool:
        """
        Checks that the configuration data stored in the object is valid.

        The data is valid if:
            Start frequency < Stop frequency
            num_pots < (stop_freq - start_freq)

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        bool
            True if the configuration data is valid
            False if the configuration data is not valid      
        """

        # Check that start is less than stop
        if self._start_FTW >= self._stop_FTW:
            return False
        
        # Check that num_pts can be supported
        max_num_pts = self._stop_FTW - self._start_FTW
        if self._num_pts > max_num_pts:
            return False
        
        # All configuration data is valid
        return True
    

    def open(self):
        """
        Opens a serial connection to the device on com_port.

        Parameters
        ----------
        None

        Raises
        ------
        SIBConnectionError
            Cannot open device on COM port.

        Returns
        -------
        None        
        """

        try:
            self._comms.connect()
        except ncomm.NCommConnectionError:
            raise SIBConnectionError('Could not open port {}.'.format(self._comms.com_port))
        
        return
    

    def close(self):
        '''Closes the connection to the device.'''
        self._comms.disconnect()
        return
    

    def data_waiting(self):
        """
        Returns the number of bytes waiting in the serial read buffer.

        Parameters
        ----------
        None

        Raises
        ------
        SIBConnectionError
            There is a problem with the serial connection. It must be reset.

        Returns
        -------
        num_bytes : int
            The number of bytes waiting to be read.        
        """

        try:
            num_bytes = self._comms.in_waiting()
        except ncomm.NCommConnectionError as e:
            raise SIBConnectionError(e)
        
        return num_bytes
    

    def is_open(self) -> bool:
        """
        Returns the state of the serial connection.

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        is_open : bool
            True - The serial port is open
            False - The serial port is not open
        """

        return self._comms.is_open()
    

    def reset_input_buffer(self):
        """
        Clears the input buffer, discarding all data in the buffer.

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

        self._comms.reset_input_buffer()


    def reset_output_buffer(self):
        """
        Clears the output buffer, aborting the current output, discarding
        all data in the buffer.

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

        self._comms.reset_output_buffer()


    def write_start_ftw(self) -> int:
        """
        Writes the start frequency as an FTW to the device. The method
        then waits for the device acknowledgment. The value that was written
        to the DDS is then returned.

        Parameters
        ----------
        None

        Raises
        ------
        ValueError
            The DDS configuration data is not valid.
        SIBError
            Host received an unexpected acknowledgment code
        SIBConnectionError
            There is a problem with the serial connection. It must be reset.

        Returns
        -------
        ack_payload : int
          The SIB responds with the value written to the DDS.     
        """

        if not self.valid_config():
            raise ValueError('DDS configuration data is not valid.')
        
        # Write command
        self._write_packet('send_start_ftw', self._start_FTW)

        # Read ACK. This command can on responds with OK.
        ack_msg, ack_payload = self._read_packet()

        # Command can only respond with OK
        if ack_msg != 'ok':
            raise SIBError('Unexpeced acknowledgment received: {}'.format(ack_msg))
        
        return ack_payload
    

    def write_stop_ftw(self) -> int:
        """
        Writes the stop frequency as an FTW to the device. The method
        then waits for the device acknowledgment. The value that was written
        to the DDS is then returned.

        Parameters
        ----------
        None

        Raises
        ------
        ValueError
            The DDS configuration data is not valid.
        SIBError
            Host received an unexpected acknowledgment code
        SIBConnectionError
            There is a problem with the serial connection. It must be reset.

        Returns
        -------
        ack_payload : int
          The SIB responds with the value written to the DDS.    
        """

        if not self.valid_config():
            raise ValueError('DDS configuration data is not valid.')

        # Write command
        self._write_packet('send_stop_ftw', self._stop_FTW)

        # Read ACK. This command can only respond with OK
        ack_msg, ack_payload = self._read_packet()

        # Command can only respond with OK
        if ack_msg != 'ok':
            raise SIBError('Unexpeced acknowledgment received: {}'.format(ack_msg))
        
        return ack_payload
    

    def write_asf(self) -> int:
        """
        Writes the amplitude scale factor to the device. The method
        then waits for the device acknowledgment. The value that was written
        to the DDS is then returned.

        Parameters
        ----------
        None

        Raises
        ------
        SIBError
            Host received an unexpected acknowledgment code
        SIBConnectionError
            There is a problem with the serial connection. It must be reset.

        Returns
        -------
        ack_payload : int
          The SIB responds with the value written to the DDS.         
        """

        # Write command
        self._write_packet('send_asf', self._asf)

        # Read ACK. This command can only respond with OK.
        ack_msg, ack_payload = self._read_packet()

        # Command can only respond with OK
        if ack_msg != 'ok':
            raise SIBError('Unexpeced acknowledgment received: {}'.format(ack_msg))
        
        return ack_payload
    

    def write_num_pts(self) -> int:
        """
        Writes the number of frequency points to the device. The method
        then waits for the device acknowledgment. The value that was written
        to the DDS is then returned.

        Parameters
        ----------
        None

        Raises
        ------
        ValueError
            The DDS configuration data is not valid.
        SIBError
            Host received an unexpected acknowledgment code
        SIBConnectionError
            There is a problem with the serial connection. It must be reset.

        Returns
        -------
        ack_payload : int
          The SIB responds with the value written to the DDS.       
        """

        if not self.valid_config():
            raise ValueError('DDS configuration data is not valid.')
        
        # Write command
        self._write_packet('send_num_pts', self._num_pts)

        # Read ACK. This command can only respond with OK
        ack_msg, ack_payload = self._read_packet()

        # Command can only respond with OK
        if ack_msg != 'ok':
            raise SIBError('Unexpeced acknowledgment received: {}'.format(ack_msg))
        
        return ack_payload
    

    def handshake(self,
                  data: int
                  ) -> int:
        """
        Performs a handshake operation with the device. The host sends
        the value of DATA as the payload. The device responds with an
        OK acknowledgment and echos the value in DATA as the payload.

        Parameters
        ----------
        data : int
            The value to send to the device as the payload. Data must
            be able to fit in payload_size bytes.

        Raises
        ------
        TypeError
            The data is not of type int
        ValueError
            The data is out of range. Must be less than (2^32 - 1) 
        SIBError
            Host received an unexpected acknowledgment code
        SIBConnectionError
            There is a problem with the serial connection. It must be reset.

        Returns
        -------
        ack_payload : int
            This is the value received from the device. 
        """

        if not isinstance(data, int):
            raise TypeError('Handshake data must be an integer.')
        
        if (data < 0) or (data >= 2**32):
            raise ValueError('Handshake data is out of range.')
        
        # Send handshake command
        self._write_packet('handshake', data)

        # Read acknowledgment. This command can only respond with OK.
        ack_msg, ack_payload = self._read_packet()

        # Command can only respond with OK
        if ack_msg != 'ok':
            raise SIBError('Unexpeced acknowledgment received: {}'.format(ack_msg))
        
        return ack_payload
        

    def version(self) -> str:
        """
        Requests the firmware version number from the device.

        Parameters
        ----------
        None

        Raises
        ------
        SIBError
            Host received an unexpected acknowledgment code
        SIBConnectionError
            There is a problem with the serial connection. It must be reset.

        Returns
        -------
        version_num : str
            The version number of the firmware.        
        """

        # Write get version command
        self._write_packet('get_version', 0)    # Payload is don't care

        # Read ACK. This command can only respond with OK
        ack_msg, ack_payload = self._read_packet()

        # Command can only respond with OK
        if ack_msg != 'ok':
            raise SIBError('Unexpeced acknowledgment received: {}'.format(ack_msg))

        # Read packet returns the payload as an integer. Convert back to bytes
        version_num = ack_payload.to_bytes(4, 'big')

        # ACK version_num is formatted as follows:
        #   ack_payload[0] is unused
        #   Major version number is stored in ack_payload[1]
        #   Minor version number is stored in ack_payload[2]
        #   Patch version number is stored in ack_payload[3]
        return f'{version_num[1]}.{version_num[2]}.{version_num[3]}'
        

    def sleep(self):
        """
        Puts the SiB into a low-power sleep mode by disabling all of the
        voltage regulators. This mode is indicated visually by a blinking
        of the power LED.

        While in the low-power sleep mode, the system will still respond to
        the following commands: set_start_FTW, set_stop_FTW, set_num_sweep_pts,
        set_amplitude, get_version_number, handshake, and sib_wake.

        If the system is in the low-power sleep mode, the self.wake() command must
        be called before any frequeny sweep can be started.

        Parameters
        ----------
        None

        Raises
        ------
        SIBError
            Host received an unexpected acknowledgment code
        SIBConnectionError
            There is a problem with the serial connection. It must be reset.

        Returns
        -------
        None      
        """

        # Write the system sleep command
        self._write_packet('system_sleep', 0)   # Payload is don't care

        # Read the ACK. This command can only respond with OK and payload is don't care
        ack_msg, _ = self._read_packet()

        # Command can only respond with OK
        if ack_msg != 'ok':
            raise SIBError('Unexpeced acknowledgment received: {}'.format(ack_msg))
    

    def wake(self):
        """
        Wakes the SiB from the low-power sleep mode. Once this command has been
        sent, the SiB enables all voltage regulators and re-initializes the DDS
        into the default starting state. This is indicated visually by a steady
        ON power LED.

        Parameters
        ----------
        None

        Raises
        ------
        SIBDDSConfigError
            The DDS wasn't configured correctly while waking up.
        SIBError
            Host received an unexpected acknowledgment code or unexpected error code
        SIBConnectionError
            There is a problem with the serial connection. It must be reset.

        Returns
        -------
        None      
        """

        # Write the system_wake command
        self._write_packet('system_wake', 0)    # The payload is don't care

        # Read the ACK. This command can only respond with OK
        ack_msg, ack_payload = self._read_packet()

        if ack_msg == 'ok':
            return
        elif ack_msg == 'fail':
            if (self._error_dict.get(ack_payload) == 'dds_config_error'):
                # The DDS registers were not configured
                raise SIBDDSConfigError('DDS did not properly configure during wakeup.')
            else:
                # Unexpected error code received
                raise SIBError('ERROR: Unexpected error code received: {}'.format(ack_payload))
        else:
            raise SIBError('Unexpected acknowledgement received: {}'.format(ack_msg))



    def reset_sib(self):
        """
        Sends a command to the SIB to perform a full system reset.

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
        # Write the system reset command
        self._write_packet('reset', 0)      # The payload is don't care

        # Read the ACK. This command can only respond with OK
        self._read_packet()
            
    
    '''
    *********************************************************
    Public functions used to conduct frequency sweeps with the SIB.
    *********************************************************
    '''
    def write_sweep_command(self):
        """
        Writes the sweep command to the device. Nothing else take place.
        The user must call self.read_sweep_response() for future state.

        Parameters
        ----------
        None

        Raises
        ------
        SIBConnectionError
            There is a problem with the serial connection. It must be reset.

        Returns
        -------
        None      
        """

        # Write command
        self._write_packet('start_test', 0) # Payload is don't care
        return
    

    def read_sweep_response(self):
        """
        Reads the device acknowledgment after the start test command
        has been written. The device will acknowledge in one of three
        ways: OK, SEND_DATA, or FAIL.

        If the OK acknowledgment was received, then the sweep is complete.

        If the SEND_DATA acknowledgment was received, then the method
        reads the specified number of bytes from the device before returning.

        If the FAIL acknowledgment was received, then the system throws an
        exception with the received error code.

        Parameters
        ----------
        None

        Raises
        ------
        SIBRegulatorsNotReadyError
            The voltage regulators are not enabled on the SIB.
        SIBError
            The number of bytes to receive is not an even number.
            Host received an unexpected acknowledgment code or error code.
        SIBConnectionError
            There is a problem with the serial connection. It must be reset.

        Returns
        -------
        tuple[str, int]
            ack_msg : str
                The human readible message received from the device
            data : int
                The 12-bit ADC output codes received from the device as integers.   
        """

        # This command can result in OK, SEND_DATA, or FAIL
        ack_msg, ack_payload = self._read_packet()

        if ack_msg == 'ok':
            # Sweep is complete
            data = None
        elif ack_msg == 'send_data':
            # The ack_payload contains the number of bytes to receive
            # which should be an even value
            if (ack_payload % 2) != 0:
                raise SIBError('Number of received bytes should be an even value: {}'.format(ack_payload))
            else:
                data = self._read_data(ack_payload)
        elif ack_msg == 'fail':
            # Decode the error code
            if (self._error_dict.get(ack_payload) == 'regulators_not_ready'):
                raise SIBRegulatorsNotReadyError
            else:
                raise SIBError('Unexpected error code received: {}'.format(ack_payload))
        else:
            raise SIBError('Unexpected acknowledgment received: {}'.format(ack_msg))
        
        return (ack_msg, data)
    






