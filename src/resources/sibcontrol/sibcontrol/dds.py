
class AD9910():
    """
    A class used to represent the AD9910 DDS chip.

    Attributes
    ----------
    min_freq : float
        Minimum frequency in MHz
    max_freq : float
        Maximum frequency in MHz
    min_amp_mA : float
        Minimum signal amplitude in mA
    max_amp_mA : float
        Maximum possible signal amplitude in mA
    max_num_pts : int
        Maximum possible number of points
    sys_clk_freq : int
        The system clock frequency of the DDS in Hz.

    Methods
    -------
    freq_MHz_in_range(freq)
        Checks that a frequency is within valid range.
    amp_mA_in_range(amp)
        Checks that a signal amplitude is within valid range.
    num_pts_in_range(num_pts)
        Checks that a number of frequency points is within valid range.
    hz_to_ftw(freq)
        Converts a frequency in Hz to a 32-bit FTW
    ftw_to_hz(FTW)
        Converts a 32-bit FTW to a frequency in Hz
    ma_to_asf(amplitude)
        Converts a signal amplitude in mA to a 14-bit amplitude scale factor
    asf_to_ma(asf)
        Converts a 14-bit amplitude scale factor to a signal amplitude in mA.
    """

    def __init__(self,
                 min_freq,          # Minimum frequency in MHz
                 max_freq,          # Maximum frequency in MHz
                 min_amplitude,     # Minimum amplitude in mA
                 max_amplitude,     # Maximum amplitude in mA
                 max_num_pts,       # Maximum number of sweep points
                 sys_clk_freq       # DDS system clock frequency in Hz
                 ):
        """
        Parameters
        ----------
        min_freq : float
            Minimum frequency in MHz
        max_freq : float
            Maximum frequency in MHz
        min_amp_mA : float
            Minimum signal amplitude in mA
        max_amp_mA : float
            Maximum possible signal amplitude in mA
        max_num_pts : int
            Maximum possible number of points
        sys_clk_freq : int
            The system clock frequency of the DDS in Hz.
        """

        # Set the minimum and maximum frequencies in MHz
        self.min_freq_MHz = min_freq
        self.max_freq_MHz = max_freq

        # Set the minimum and maximum amplitude in mA
        self.min_amp_mA = min_amplitude
        self.max_amp_mA = max_amplitude

        # Set the minimum and maximum number of sweep points
        self.min_num_pts = 1
        self.max_num_pts = max_num_pts

        # Set the system clock frequency in Hz
        self.clk_freq_Hz = sys_clk_freq


    def freq_MHz_in_range(self,
                          freq
                          ) -> bool:
        """
        Checks that a frequency is within valid range as indicated
        by min_freq and max_freq.

        Parameters
        ----------
        freq : float
            The frequency in MHz to check.

        Raises
        ------
        None

        Returns
        -------
        True if the frequency is within valid range
        False if the frequency is not within valid range
        """
        
        if (freq >= self.min_freq_MHz) and (freq <= self.max_freq_MHz):
            return True
        else:
            return False


    def amp_mA_in_range(self,
                        amp
                        ):
        """
        Checks that a signal amplitude is within valid range as indicated
        by min_amp and max_amp.

        Parameters
        ----------
        amp : float
            The signal amplitude in mA to check.

        Raises
        ------
        None

        Returns
        -------
        True if the amplitude is within valid range
        False if the amplitude is not within valid range
        """

        if (amp >= self.min_amp_mA) and (amp <= self.max_amp_mA):
            return True
        else:
            return False


    def num_pts_in_range(self,
                            num_pts
                            ):
        """
        Checks that a number of sweep points is within valid range as indicated
        by max_num_pts. The minimum number of points is 1.

        Parameters
        ----------
        num_pts : int
            The number of points to check.

        Raises
        ------
        None

        Returns
        -------
        True if the number of points is within valid range
        False if the number of points is not within valid range
        """

        if (num_pts >= self.min_num_pts) and (num_pts <= self.max_num_pts):
            return True
        else:
            return False
        

    def hz_to_ftw(self,
                    freq
                    ) -> int:
        """
        Converts a frequency in Hz to a 32-it FTW.

        Parameters
        ----------
        freq : float
            The frequency in Hz to convert.

        Raises
        ------
        None

        Returns
        -------
        FTW : int
            The 32-bit frequency tuning word.
        """
        FTW = round((2**32) * (freq / self.clk_freq_Hz))
        return int(FTW)


    def ftw_to_hz(self,
                  FTW
                  ):
        """
        Converts a 32-bit FTW to a frequency in Hz.

        Parameters
        ----------
        FTW : int
            The 32-bit FTW to convert.

        Raises
        ------
        None

        Returns
        -------
        freq : float
            The frequency in Hz.
        """

        freq_Hz = (FTW / (2**32)) * self.clk_freq_Hz
        return float(freq_Hz)


    def ma_to_asf(self,
                  amplitude
                  ):
        """
        Converts signal amplitude in mA to a 14-bit amplitude
        scale factor.

        Parameters
        ----------
        amplitude : float
            The signal amplitude in mA.

        Raises
        ------
        None

        Returns
        -------
        ASF : int
            The 14-bit amplitude scale factor.
        """

        ASF = round((2**14 - 1) * (amplitude / self.max_amp_mA))
        return int(ASF)


    def asf_to_ma(self,
                  ASF
                  ):
        """
        Converts a 14-bit amplitude scale factor into a signal
        amplitude in mA.

        Parameters
        ----------
        ASF : int
            The 14-bit amplitude scale factor.

        Raises
        ------
        None

        Returns
        -------
        amplitude : float
            The signal amplitude in mA.
        """

        amplitude = self.max_amp_mA * (ASF / (2**14 - 1))
        return float(amplitude)




