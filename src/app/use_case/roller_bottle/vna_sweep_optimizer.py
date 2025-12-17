import logging
from typing import List, Optional, Tuple

import numpy as np
from scipy.signal import savgol_filter

from src.app.helper_methods.custom_exceptions.analysis_exception import SensorNotFoundException, FocusedSweepFailedException
from src.app.helper_methods.data_helpers import findMaxGaussian
from src.app.helper_methods.model.sweep_data import SweepData


class VnaSweepOptimizer:
    """
    Performs VNA sweeps to identify the optimal frequency range around the resonant peak.

    This class takes 30-point sweeps across the entire frequency range and repeats until
    a successful peak is identified. Once a peak is found, it performs a final
    30-point sweep in a narrower range (+/- 5 MHz around the peak) for detailed data.

    This class is independent and does not require an analyzer instance.
    """

    def __init__(self, previousPeak: float = 1.1):
        """Initialize the VNA sweep optimizer."""
        self.max_wide_attempts = 1000  # Maximum number of wide sweep attempts before logging an error
        self.min_wide_attempts = 10  # Minimum number of wide sweep attempts before accepting a peak
        self.max_focused_attempts = 6  # Maximum number of focused sweep attempts before stopping
        self.wide_sweep_points = 50  # Number of points per wide sweep
        self.sweep_points = 200  # Number of points per focused sweep
        self.peak_window_mhz = 10  # +/- MHz around peak for focused sweep
        self.minVoltageThreshold = self._setMinVoltageThreshold(previousPeak)

    def performOptimizedSweep(self, sib_device, start_freq_mhz: float, stop_freq_mhz: float) -> SweepData:
        """
        Perform wide-range sweeps until a successful peak is identified,
        then perform a final focused sweep around the identified peak.

        Args:
            sib_device: The SIB device to perform sweeps with
            start_freq_mhz: Starting frequency in MHz
            stop_freq_mhz: Stopping frequency in MHz

        Returns:
            SweepData from the final focused sweep around the peak

        Raises:
            ScanAnalysisException: If no successful peak is found after max_attempts
        """
        final_sweep_data = None
        while not final_sweep_data:
            peak_frequency = self._performWideSweepUntilPeakFound(
                sib_device,
                start_freq_mhz,
                stop_freq_mhz
            )
            try:
                final_sweep_data = self._performRepeatedFocusedSweeps(
                    sib_device,
                    peak_frequency,
                    start_freq_mhz,
                    stop_freq_mhz
                )
            except FocusedSweepFailedException:
                logging.exception("Error during focused sweeps, restarting wide sweep.")
        return final_sweep_data

    def _setMinVoltageThreshold(self, peakMagnitude: float):
        """
        Set the minimum voltage threshold for peak detection.

        Args:
            peakMagnitude: The previous peak magnitude to base the threshold on
        """
        self.minVoltageThreshold = peakMagnitude - (peakMagnitude - 1) * (1/2)
        return self.minVoltageThreshold

    def _performWideSweepUntilPeakFound(self, sib_device, start_freq_mhz: float, stop_freq_mhz: float) -> float:
        """
        Repeatedly perform wide sweeps until a peak is successfully identified.

        Args:
            sib_device: The SIB device to perform sweeps with
            start_freq_mhz: Starting frequency in MHz
            stop_freq_mhz: Stopping frequency in MHz

        Returns:
            Peak frequency in MHz

        Raises:
            ScanAnalysisException: If no peak is found after max_attempts
        """
        maxMagnitude = 0.0
        for attempt in range(self.max_wide_attempts):
            sweep_data = self._performCalibratedSweep(
                sib_device,
                start_freq_mhz,
                stop_freq_mhz,
                self.wide_sweep_points
            )

            peak_magnitude, peak_frequency = self._findPeakFrequency(sweep_data)
            if peak_magnitude is not None and peak_magnitude > maxMagnitude and attempt > self.min_wide_attempts:
                maxMagnitude = peak_magnitude
            if peak_frequency is not None and peak_magnitude >= self.minVoltageThreshold and attempt > self.min_wide_attempts:
                logging.info(
                    f"Successful sweep on attempt {attempt + 1}. "
                    f"Peak found at {peak_frequency:.2f} MHz",
                    extra={"id": "VnaSweepOptimizer"}
                )
                return sweep_data.getFrequency()[np.argmax(sweep_data.getMagnitude())]
        raise SensorNotFoundException(
            f"Failed to find peak after {self.max_wide_attempts} attempts. Max magnitude seen: {maxMagnitude:.2f}"
        )

    def _performRepeatedFocusedSweeps(self, sib_device, initial_peak_frequency: float, start_freq_mhz: float, stop_freq_mhz: float) -> SweepData:
        """
        Perform repeated focused sweeps until conditions are no longer met,
        then return the sweep with the highest peak strength.

        Continues sweeping while peak_frequency is not None AND peak_magnitude >= self.minVoltageThreshold.

        Args:
            sib_device: The SIB device to perform sweeps with
            initial_peak_frequency: The initial peak frequency to center the sweep around
            start_freq_mhz: Minimum frequency bound (original range)
            stop_freq_mhz: Maximum frequency bound (original range)

        Returns:
            SweepData from the sweep with the highest peak magnitude
        """
        peak_frequency = initial_peak_frequency
        sweep_count = 0
        all_sweep_data = []

        for attempt in range(self.max_focused_attempts):
            sweep_count += 1
            sweep_data = self._performFocusedSweep(
                sib_device,
                peak_frequency,
                start_freq_mhz,
                stop_freq_mhz
            )

            should_continue, new_peak_freq, peak_magnitude = self._shouldContinueSweeping(sweep_data)

            if not should_continue:
                all_sweep_data.append(sweep_data)
                return self._selectHighestPeakSweep(all_sweep_data)

            all_sweep_data.append(sweep_data)

            peak_frequency = new_peak_freq
            logging.info(
                f"Focused sweep {sweep_count} successful (magnitude={peak_magnitude:.3f}). "
                f"Repeating sweep around {peak_frequency:.2f} MHz",
                extra={"id": "VnaSweepOptimizer"}
            )
        return self._selectHighestPeakSweep(all_sweep_data)

    def _selectHighestPeakSweep(self, sweep_data_list: List[SweepData]) -> SweepData:
        """
        Select the sweep with the highest peak magnitude from a list of sweep data.

        Args:
            sweep_data_list: List of SweepData objects from repeated sweeps

        Returns:
            SweepData from the sweep with the highest peak magnitude
        """
        num_sweeps = len(sweep_data_list)

        if num_sweeps == 1:
            return sweep_data_list[0]

        peak_magnitudes = []
        for sweep_data in sweep_data_list:
            peak_magnitude, _ = self._findPeakFrequency(sweep_data)
            peak_magnitudes.append(peak_magnitude if peak_magnitude is not None else 0.0)

        best_index = peak_magnitudes.index(max(peak_magnitudes))
        best_magnitude = peak_magnitudes[best_index]

        logging.info(
            f"Selected sweep {best_index + 1} of {num_sweeps} with highest peak magnitude ({best_magnitude:.3f})",
            extra={"id": "VnaSweepOptimizer"}
        )

        if best_magnitude < self.minVoltageThreshold:
            logging.warning(
                f"Highest peak magnitude ({best_magnitude:.3f}) is below threshold ({self.minVoltageThreshold}).",
                extra={"id": "VnaSweepOptimizer"}
            )
            raise FocusedSweepFailedException()

        return sweep_data_list[best_index]

    def _shouldContinueSweeping(self, sweep_data: SweepData) -> Tuple[bool, Optional[float], Optional[float]]:
        """
        Determine if focused sweeping should continue based on sweep quality.

        Args:
            sweep_data: SweepData from the most recent focused sweep

        Returns:
            Tuple of (should_continue, peak_frequency, peak_magnitude)
            - should_continue: True if peak_frequency is not None AND peak_magnitude >= self.minVoltageThreshold
            - peak_frequency: The identified peak frequency or None
            - peak_magnitude: The peak magnitude value or None
        """
        peak_magnitude, peak_frequency = self._findPeakFrequency(sweep_data)
        should_continue = (
            peak_frequency is not None and
            peak_magnitude is not None and
            peak_magnitude >= self.minVoltageThreshold
        )
        return should_continue, peak_frequency, peak_magnitude

    def _performFocusedSweep(self, sib_device, peak_frequency: float, start_freq_mhz: float, stop_freq_mhz: float) -> SweepData:
        """
        Perform a focused sweep around the identified peak frequency.

        Args:
            sib_device: The SIB device to perform sweeps with
            peak_frequency: The peak frequency to center the sweep around
            start_freq_mhz: Minimum frequency bound (original range)
            stop_freq_mhz: Maximum frequency bound (original range)

        Returns:
            SweepData from the focused sweep
        """
        focused_start, focused_stop = self._calculateFocusedRange(
            peak_frequency,
            start_freq_mhz,
            stop_freq_mhz
        )

        return self._performCalibratedSweep(
            sib_device,
            focused_start,
            focused_stop,
            self.sweep_points
        )

    def _calculateFocusedRange(self, peak_frequency: float, min_freq_mhz: float, max_freq_mhz: float) -> Tuple[float, float]:
        """
        Calculate the focused frequency range around a peak.

        Args:
            peak_frequency: The peak frequency to center around
            min_freq_mhz: Minimum frequency bound
            max_freq_mhz: Maximum frequency bound

        Returns:
            Tuple of (start_frequency, stop_frequency) for focused sweep
        """
        focused_start = peak_frequency - self.peak_window_mhz
        focused_stop = peak_frequency + self.peak_window_mhz
        focused_start = max(focused_start, min_freq_mhz)
        focused_stop = min(focused_stop, max_freq_mhz)
        return focused_start, focused_stop

    def _findPeakFrequency(self, sweep_data: SweepData) -> (Optional[float], Optional[float]):
        """
        Find the peak frequency from sweep data.

        Args:
            sweep_data: SweepData containing frequency and magnitude arrays

        Returns:
            Peak frequency in MHz, or None if peak cannot be determined
        """
        try:
            smoothed_magnitudes = self._smoothData(sweep_data.magnitude)
            peak_magnitude, peak_freq, _ = findMaxGaussian(
                sweep_data.frequency,
                smoothed_magnitudes,
                pointsOnEachSide=None
            )
            return peak_magnitude, peak_freq

        except Exception as e:
            logging.warning(
                f"Failed to find peak frequency: {str(e)}",
                extra={"id": "VnaSweepOptimizer"}
            )
            return None, None

    @staticmethod
    def _smoothData(magnitudes: List[float]) -> np.ndarray:
        """
        Apply smoothing to magnitude data if sufficient points are available.

        Args:
            magnitudes: List of magnitude values

        Returns:
            Smoothed magnitude array (or original if insufficient points)
        """
        magnitudes_array = np.array(magnitudes)

        if len(magnitudes_array) > 101:
            return savgol_filter(magnitudes_array, 101, 2)
        else:
            return magnitudes_array

    def _performCalibratedSweep(self, sib_device, start_freq_mhz: float, stop_freq_mhz: float, num_points: int) -> SweepData:
        """
        Perform a sweep and apply calibration to the results.

        Args:
            sib_device: The SIB device to perform the sweep with
            start_freq_mhz: Starting frequency in MHz
            stop_freq_mhz: Stopping frequency in MHz
            num_points: Number of points to sweep

        Returns:
            SweepData containing calibrated frequency and magnitude arrays
        """
        raw_volts = self._performRawSweep(sib_device, start_freq_mhz, stop_freq_mhz, num_points)
        frequencies = self._calculateFrequencies(start_freq_mhz, stop_freq_mhz, num_points)
        calibrated_volts = self._applyCalibration(sib_device, frequencies, raw_volts)

        return SweepData(frequencies, calibrated_volts)

    @staticmethod
    def _performRawSweep(sib_device, start_freq_mhz: float, stop_freq_mhz: float, num_points: int) -> List[float]:
        """
        Perform a raw VNA sweep and return uncalibrated voltage measurements.

        Args:
            sib_device: The SIB device to perform the sweep with
            start_freq_mhz: Starting frequency in MHz
            stop_freq_mhz: Stopping frequency in MHz
            num_points: Number of points to sweep

        Returns:
            List of raw voltage measurements
        """
        sib_device.prepareSweep(start_freq_mhz, stop_freq_mhz, num_points)
        return sib_device.performSweep()

    @staticmethod
    def _applyCalibration(sib_device, frequencies: List[float], raw_volts: List[float]) -> List[float]:
        """
        Apply calibration correction to raw voltage measurements.

        Args:
            sib_device: The SIB device with calibration data
            frequencies: List of frequency values
            raw_volts: List of raw voltage measurements

        Returns:
            List of calibrated voltage values
        """
        calibrated_volts = []
        for freq, volt in zip(frequencies, raw_volts):
            calibrated_volt = sib_device.calibrationPointComparison(freq, volt)
            calibrated_volts.append(calibrated_volt)
        return calibrated_volts

    @staticmethod
    def _calculateFrequencies(start_freq_mhz: float, stop_freq_mhz: float, num_points: int) -> List[float]:
        """
        Calculate evenly-spaced frequency points across the range.

        Args:
            start_freq_mhz: Starting frequency in MHz
            stop_freq_mhz: Stopping frequency in MHz
            num_points: Number of frequency points

        Returns:
            List of frequency values in MHz
        """
        if num_points <= 1:
            return [start_freq_mhz]

        step = (stop_freq_mhz - start_freq_mhz) / (num_points - 1)
        return [start_freq_mhz + i * step for i in range(num_points)]
