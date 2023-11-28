
class Packet:
    """
    A class that represents the packet structure used to communicate between
    the HOST and the device.

    Attributes
    ----------
    command_size : int
        The number of bytes that makes up the command portion of the packet
    payload_size : int
        The number of bytes that makes up the payload portion of the packet
    size : tuple[int, int]
        A tuple containing the command size and the payload size
    command_dict : dictionary
        A dictionary that contains the mapping of the command codes to their
        corresponding human readible command names.
        
    Methods
    -------
    command_from_name(command_name)
        Returns the command_code that should be sent to the device from the
        given command name.
    name_from_command(comand_code)
        Returns the command name that corresponds to the provided command code.
    """

    def __init__(self,
                 command_size: int,     # Size, in bytes, of the command portion of the packet
                 payload_size: int      # Size, in bytes, of the payload portion of the packet
                 ):
        """
        Parameters
        ----------
        command_size : int
            The number of bytes that make up the command portion of the packet.
        payload_size : int
            The number of bytes that make up the payload portion of the packet.
        """
        
        if isinstance(command_size, int):
            self.command_size = command_size
        else:
            raise ValueError('Command size must be an integer.')
        
        if isinstance(payload_size, int):
            self.payload_size = payload_size
        else:
            raise ValueError('Payload size must be an integer.')

        # Dictionary to hold valid commands/names
        self.command_dict = None
    
    
    @property
    def size(self):
        return (self.command_size, self.payload_size)
    

    def command_from_name(self,
                          command_name: str
                          ) -> bytes:
        """
        Returns the command code that should be sent to the device
        that corresponds to the provided human readible command name.

        Parameters
        ----------
        command_name : str
            The human readible command name

        Raises
        ------
        ValueError
            If the command_name cannot be found in the command dictionary.

        Returns
        -------
        command_code : bytes
            The command code that can be sent to the device.
        """

        if not isinstance(command_name, str):
            raise TypeError('Command name must be a string.')
        
        command_code = self.command_dict.get(command_name)
        if not command_code:
            raise ValueError('Command {} is not found.'.format(command_name))
        
        return command_code
    

    def name_from_command(self,
                          command_code: bytes
                          ) -> str:
        """
        Returns the human readible command name that corresponds
        to the given command code.

        Parameters
        ----------
        command_code : bytes
            The command code received from the device

        Raises
        ------
        ValueError
            If the command_code cannot be found in the command dictionary.

        Returns
        -------
        command_msg : str
            The human readible command name corresponding to the command code
        """
        
        if not isinstance(command_code, bytes):
            raise TypeError('Command code must be of type bytes.')
        
        command_msg = self.command_dict.get(command_code)
        if not command_msg:
            raise ValueError('Command {} is not found in the dictionary.'.format(command_code))
        
        return command_msg






   

     

    



