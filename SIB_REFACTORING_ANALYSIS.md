# SIB Refactoring Analysis

## Overview
This document analyzes the four SIB implementation files and identifies duplicate code that can be refactored into a common base class.

## Files Analyzed
1. `src/app/reader/sib/continuous/continuous_sib.py` - ContinuousSib
2. `src/app/reader/sib/flow_cell/flow_cell_sib.py` - FlowCellSib
3. `src/app/reader/sib/roller_bottle/roller_bottle_sib.py` - RollerBottleSib
4. `src/app/reader/sib/tunair/tunair_sib.py` - TunairSib

---

## Duplicate Code - Class Methods

### 1. **Identical Methods (Can be pulled to base class as-is)**

#### `getYAxisLabel()` (Lines 42-43 in all files)
```python
def getYAxisLabel(self) -> str:
    return ContextFactory().getSibProperties().yAxisLabel
```
**Status:** 100% identical across all 4 files

#### `estimateDuration()` (Lines 75-77 in all files)
```python
def estimateDuration(self) -> float:
    # Assume that the SIB can return 235 points per second or a 100-160 MHz sweep in 26s.
    return self.sib.num_pts / 235
```
**Status:** 100% identical across all 4 files

#### `getCurrentlyScanning()` (Lines 140-141 in all files)
```python
def getCurrentlyScanning(self) -> Subject:
    return self.currentlyScanning
```
**Status:** 100% identical across all 4 files

#### `getCalibrationFilePresent()` (Lines 143-144 in all files)
```python
def getCalibrationFilePresent(self) -> BehaviorSubject:
    return self.calibrationFilePresent
```
**Status:** 100% identical across all 4 files

#### `setNumberOfPoints()` (Lines 151-156 in all files)
```python
def setNumberOfPoints(self) -> bool:
    try:
        self.sib.num_pts = getNumPointsSweep(self.startFreqMHz, self.stopFreqMHz)
        return True
    except:
        return False
```
**Status:** 100% identical across all 4 files

#### `close()` (Lines 158-164 in all files)
```python
def close(self) -> bool:
    try:
        self.PortAllocator.removePort(self.readerNumber)
        self.sib.close()
        return True
    except:
        return False
```
**Status:** 100% identical across all 4 files

#### `reset()` (Lines 166-167 in all files)
```python
def reset(self) -> bool:
    return self.close()
```
**Status:** 100% identical across all 4 files

#### `performHandshake()` (Lines 175-187 in all files)
```python
def performHandshake(self) -> bool:
    data = 500332  # Some random 32-bit value
    try:
        return_val = self.sib.handshake(data)
        if return_val == data:
            self.getFirmwareVersion()
            return True
        else:
            return False
    except sibcontrol.SIBException as e:
        logging.exception("Failed to perform handshake", extra={"id": "Sib"})
        return False
```
**Status:** 100% identical across all 4 files

#### `getFirmwareVersion()` (Lines 188-196 in all files)
```python
def getFirmwareVersion(self) -> str:
    try:
        firmware_version = self.sib.version()
        logging.info(f'The SIB Firmware is version: {firmware_version}', extra={"id": "Sib"})
        return firmware_version
    except sibcontrol.SIBException as e:
        logging.exception("Failed to set firmware version", extra={"id": "Sib"})
        return ''
```
**Status:** 100% identical across all 4 files

#### `resetDDSConfiguration()` (Lines 243-248 in all files)
```python
def resetDDSConfiguration(self):
    logging.info("The DDS did not get configured correctly, performing hard reset.", extra={"id": "Sib"})
    self.sib.reset_sib()
    time.sleep(5)  # The host will need to wait until the SIB re-initializes. I do not know how long this takes.
    self.resetSibConnection()
```
**Status:** 100% identical across all 4 files

#### `resetSibConnection()` (Lines 249-265 in all files)
```python
def resetSibConnection(self):
    logging.info("Problem with serial connection. Closing and then re-opening port.", extra={"id": "Sib"})
    if self.sib.is_open():
        self.reset()
        time.sleep(1.0)
    try:
        port = self.PortAllocator.getPortForReader(self.readerNumber)
        self.initialize(port.device)
        self.setStartFrequency(self.startFreqMHz + self.initialSpikeMhz)
        self.setStopFrequency(self.stopFreqMHz)
        self.checkAndSendConfiguration()
        raise SIBReconnectException
    except SIBReconnectException:
        raise
    except:
        pass
```
**Status:** 100% identical across all 4 files

---

### 2. **Nearly Identical Methods (Minor differences)**

#### `__init__()` - Minor differences in initialization
**Common structure:**
```python
def __init__(self, port, calibrationFileName, readerNumber, portAllocator: PortAllocator):
    self.PortAllocator = portAllocator
    self.readerNumber = readerNumber
    self.calibrationFrequency, self.calibrationVolts = [], []
    self.initialize(port.device)
    self.serialNumber = port.serial_number
    Properties = ContextFactory().getSibProperties()
    self.calibrationStartFreq = Properties.startFrequency
    self.calibrationStopFreq = Properties.stopFrequency
    self.stepSize = Properties.stepSize
    self.initialSpikeMhz = Properties.initialSpikeMhz
    self.calibrationFilename = calibrationFileName
    self.calibrationFilePresent = BehaviorSubject(self.loadCalibrationFile())
    self.currentlyScanning = Subject()
```

**Differences:**
- **Continuous & FlowCell:**
  - `self.stopFreqMHz = None`
  - `self.startFreqMHz = None`
  - No `referenceFreqMHz`

- **RollerBottle & Tunair:**
  - `self.referenceFreqMHz = ReferenceFrequencyConfiguration().getConfig()`
  - `self.stopFreqMHz = Properties.stopFrequency`
  - `self.startFreqMHz = Properties.startFrequency`

#### `loadCalibrationFile()` - Identical logic, different exception handling
**All versions have same core logic:**
```python
def loadCalibrationFile(self):
    try:
        self.calibrationFrequency, self.calibrationVolts = loadCalibrationFile(self.calibrationFilename)
        if len(self.calibrationFrequency) == 0 or len(self.calibrationVolts) == 0:
            return False
        selfResonance = findSelfResonantFrequency(self.calibrationFrequency, self.calibrationVolts, [50, 170], 1.8)
        logging.info(f'Self resonant frequency is {selfResonance} MHz', extra={"id": f"Reader"})
        return True
    except:
        return False
```
**Status:** 100% identical across all 4 files

#### `performCalibration()` - Very similar
**Continuous & FlowCell:**
```python
def performCalibration(self):
    try:
        calibrationSuccessful = self.takeCalibrationScan()
        if calibrationSuccessful:
            self.calibrationFilePresent.on_next(self.loadCalibrationFile())
        return calibrationSuccessful
    except:
        return False
```

**RollerBottle & Tunair:**
```python
def performCalibration(self):
    calibrationSuccessful = self.takeCalibrationScan()
    if calibrationSuccessful:
        self.calibrationFilePresent.on_next(self.loadCalibrationFile())
    return calibrationSuccessful
```
**Difference:** Continuous/FlowCell wrap in try/except

#### `checkAndSendConfiguration()` - Nearly identical
**Continuous, RollerBottle, Tunair:**
```python
def checkAndSendConfiguration(self):
    if self.sib.valid_config():
        self.sib.write_start_ftw()
        self.sib.write_stop_ftw()
        self.sib.write_num_pts()
        self.sib.write_asf()  # Only in Continuous
    else:
        text_notification.setText(
            f"Reader Port configuration is not valid.\nChange the scan frequency or number of points to reset it.")
```

**FlowCell:**
```python
def checkAndSendConfiguration(self):
    if self.sib.valid_config():
        self.sib.write_start_ftw()
        self.sib.write_stop_ftw()
        self.sib.write_num_pts()
        self.sib.write_asf()
    else:
        text_notification.setText(
            f"Reader configuration is not valid. Change the reader frequency or number of points.")
```
**Differences:**
- Continuous calls `write_asf()`, RollerBottle/Tunair don't
- FlowCell has different error message

---

### 3. **Similar Structure but Different Implementation**

#### `initialize()` - Different initialization sequences
**Continuous:**
```python
def initialize(self, port):
    self.port = port
    self.sib = sibcontrol.SIB350(port)
    self.sib.amplitude_mA = 31.6
    self.sib.open()
```

**FlowCell:**
```python
def initialize(self, port):
    self.port = port
    self.sib = sibcontrol.SIB350(port)
    self.sib.amplitude_mA = 31.6
    self.sib.open()
    self.sib.wake()
```

**RollerBottle & Tunair:**
```python
def initialize(self, port):
    self.port = port
    self.sib = sibcontrol.SIB350(port)
    self.sib.amplitude_mA = 31.6
    self.sib.open()
    self.sib.wake()
    self.sib.write_asf()
```

#### `setStartFrequency()` - Different spike handling
**Continuous & FlowCell:**
```python
def setStartFrequency(self, startFreqMHz) -> bool:
    try:
        self.startFreqMHz = startFreqMHz - self.initialSpikeMhz
        self.sib.start_MHz = startFreqMHz - self.initialSpikeMhz
        if self.stopFreqMHz:
            self.setNumberOfPoints()
        return True
    except:
        # Different error messages
        return False
```

**RollerBottle & Tunair:**
```python
def setStartFrequency(self, startFreqMHz) -> bool:
    try:
        self.startFreqMHz = startFreqMHz
        self.sib.start_MHz = startFreqMHz
        if self.stopFreqMHz:
            self.setNumberOfPoints()
        return True
    except:
        # Error messages
        return False
```

#### `setReferenceFrequency()` - Different implementations
**Continuous & FlowCell:**
```python
def setReferenceFrequency(self, peakFrequencyMHz: float):
    pass
```

**RollerBottle & Tunair:**
```python
def setReferenceFrequency(self, peakFrequencyMHz: float):
    self.referenceFreqMHz = peakFrequencyMHz - 10
```

---

### 4. **Completely Different Implementations**

#### `takeScan()` - Each has unique approach
**Continuous & FlowCell:** Basic sweep with spike removal
```python
def takeScan(self, directory: str, currentVolts: float) -> SweepData:
    try:
        allFrequency = calculateFrequencyValues(self.startFreqMHz, self.stopFreqMHz, self.stepSize)
        allVolts = self.performSweepAndWaitForComplete()
        frequency, volts = removeInitialSpike(allFrequency, allVolts, self.initialSpikeMhz, self.stepSize)
        calibratedVolts = self.calibrationComparison(frequency, volts)
        return SweepData(frequency, calibratedVolts)
    except SIBConnectionError:
        self.resetSibConnection()
        raise SIBConnectionError()
    # ... more exception handling
```

**RollerBottle:** Uses VnaSweepOptimizer
```python
def takeScan(self, directory: str, currentVolts: float) -> SweepData:
    try:
        optimizer = VnaSweepOptimizer(currentVolts) if not np.isnan(currentVolts) else VnaSweepOptimizer()
        sweepData = optimizer.performOptimizedSweep(self, self.startFreqMHz, self.stopFreqMHz)
        return sweepData
    except SIBConnectionError:
        # ... exception handling
```

**Tunair:** Uses random sweep
```python
def takeScan(self, directory: str, currentVolts: float) -> SweepData:
    try:
        allFrequency = calculateFrequencyValues(self.startFreqMHz, self.stopFreqMHz, self.stepSize)
        randomizedFrequency, randomizedVolts = self.performRandomSweep(list(allFrequency), directory)
        return SweepData(randomizedFrequency, randomizedVolts)
    except SIBConnectionError:
        # ... exception handling
```

#### `takeCalibrationScan()` - Two different patterns
**Continuous & FlowCell:** Use `performSweepAndWaitForComplete()`
```python
def takeCalibrationScan(self) -> bool:
    try:
        self.currentlyScanning.on_next(True)
        createCalibrationDirectoryIfNotExists(self.calibrationFilename)
        self.sib.start_MHz = self.calibrationStartFreq - self.initialSpikeMhz
        self.sib.stop_MHz = self.calibrationStopFreq
        self.sib.num_pts = getNumPointsSweep(self.calibrationStartFreq - self.initialSpikeMhz, self.calibrationStopFreq)
        allFrequency = calculateFrequencyValues(self.calibrationStartFreq - self.initialSpikeMhz, self.calibrationStopFreq, self.stepSize)
        allVolts = self.performSweepAndWaitForComplete()
        frequency, volts = removeInitialSpike(allFrequency, allVolts, self.initialSpikeMhz, self.stepSize)
        createCalibrationFile(self.calibrationFilename, frequency, volts)
        self.setStartFrequency(ContextFactory().getSibProperties().startFrequency)
        self.setStopFrequency(ContextFactory().getSibProperties().stopFrequency)
        return True
    except ...
    finally:
        self.currentlyScanning.on_next(False)
```

**RollerBottle & Tunair:** Use `prepareSweep()` and `performSweep()`
```python
def takeCalibrationScan(self) -> bool:
    try:
        self.currentlyScanning.on_next(True)
        createCalibrationDirectoryIfNotExists(self.calibrationFilename)
        startFrequency = self.calibrationStartFreq - self.initialSpikeMhz
        stopFrequency = self.calibrationStopFreq
        numPoints = getNumPointsSweep(startFrequency, stopFrequency)
        allFrequency = calculateFrequencyValues(startFrequency, stopFrequency, self.stepSize)
        self.prepareSweep(startFrequency, stopFrequency, numPoints)
        allVolts = self.performSweep()
        frequency, volts = removeInitialSpike(allFrequency, allVolts, self.initialSpikeMhz, self.stepSize)
        createCalibrationFile(self.calibrationFilename, frequency, volts)
        return True
    except ...
    finally:
        self.currentlyScanning.on_next(False)
```

---

## Duplicate Code - Module-level Functions

### Identical Functions (Can be moved to shared module)

#### `createCalibrationFile()` - 100% identical
```python
def createCalibrationFile(outputFileName, frequency, volts):
    with open(outputFileName, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Frequency (MHz)', 'Signal Strength (V)'])
        writer.writerows(zip(frequency, volts))
```

#### `find_nearest()` - 100% identical
```python
def find_nearest(freq, freqList, dBlist):
    pos = bisect_left(freqList, freq)
    if pos == 0:
        return dBlist[0]
    if pos == len(freqList):
        return dBlist[-1]
    before = freqList[pos - 1]
    after = freqList[pos]
    if after - freq < freq - before:
        return dBlist[pos]
    else:
        return dBlist[pos - 1]
```

#### `createCalibrationDirectoryIfNotExists()` - 100% identical
```python
def createCalibrationDirectoryIfNotExists(filename):
    if not os.path.exists(os.path.dirname(os.path.dirname(filename))):
        os.mkdir(os.path.dirname(os.path.dirname(filename)))
    if not os.path.exists(os.path.dirname(filename)):
        os.mkdir(os.path.dirname(filename))
```

#### `convertAdcToVolts()` - 100% identical
```python
def convertAdcToVolts(adcList):
    return [float(adcValue) * (3.3 / 2 ** 10) for adcValue in adcList]
```

#### `findSelfResonantFrequency()` - 100% identical
```python
def findSelfResonantFrequency(frequency, volts, scanRange, threshold):
    inRangeFrequencies, inRangeVolts = truncateByX(scanRange[0], scanRange[1], frequency, volts)
    for index, yval in enumerate(inRangeVolts):
        if yval > threshold:
            return inRangeFrequencies[index]
```

#### `removeInitialSpike()` - 100% identical
```python
def removeInitialSpike(frequency, volts, initialSpikeMhz, stepSize):
    pointsRemoved = int(initialSpikeMhz / stepSize)
    return frequency[pointsRemoved:], volts[pointsRemoved:]
```

### Similar Functions with Differences

#### `loadCalibrationFile()` - Different exception handling
**Continuous:**
```python
def loadCalibrationFile(calibrationFilename) -> (List[str], List[str], List[str]):
    try:
        readings = pandas.read_csv(calibrationFilename)
        calibrationVolts = list(readings['Signal Strength (V)'].values.tolist())
        calibrationFrequency = readings['Frequency (MHz)'].values.tolist()
        return calibrationFrequency, calibrationVolts
    except KeyError or ValueError:
        logging.exception("Column did not exist", extra={"id": calibrationFilename})
    except Exception:
        logging.exception("Failed to load in calibration", extra={"id": calibrationFilename})
```

**FlowCell:**
```python
def loadCalibrationFile(calibrationFilename) -> (List[str], List[str], List[str]):
    try:
        readings = pandas.read_csv(calibrationFilename)
        calibrationVolts = list(readings['Signal Strength (V)'].values.tolist())
        calibrationFrequency = readings['Frequency (MHz)'].values.tolist()
        return calibrationFrequency, calibrationVolts
    except KeyError or ValueError:
        logging.exception("Column did not exist", extra={"id": calibrationFilename})
        return [], []
    except FileNotFoundError:
        logging.exception("No previous calibration found.", extra={"id": calibrationFilename})
        text_notification.setText("No previous calibration found, please calibrate.")
        return [], []
    except Exception:
        logging.exception("Failed to load in calibration", extra={"id": calibrationFilename})
        return [], []
```

**RollerBottle & Tunair:** Same as Continuous (no explicit returns)

#### `calculateFrequencyValues()` - Different return types
**All have same signature but:**
- Continuous & FlowCell: Returns `List[str]`
- RollerBottle & Tunair: Returns `List[float]`

#### `getNumPointsFrequency()` & `getNumPointsSweep()` - Different calculation
**Continuous & FlowCell:**
```python
def getNumPointsFrequency(startFreq, stopFreq):
    return int((stopFreq - startFreq) * 1000 / 10 + 1)

def getNumPointsSweep(startFreq, stopFreq):
    return int((stopFreq - startFreq) * 1000 / 10)
```

**RollerBottle & Tunair:**
```python
def getNumPointsFrequency(startFreq, stopFreq):
    return int((stopFreq - startFreq) * (1 / ContextFactory().getSibProperties().stepSize) + 1)

def getNumPointsSweep(startFreq, stopFreq):
    return int((stopFreq - startFreq) * (1 / ContextFactory().getSibProperties().stepSize))
```

### Unique Functions

**RollerBottle & Tunair only:**
```python
def createReferenceFile(outputFileName, referenceStrength, frequencyStrength):
    if not os.path.exists(os.path.dirname(outputFileName)):
        os.mkdir(os.path.dirname(outputFileName))
    with open(outputFileName, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Reference Strength (V)', 'Frequency Strength (V)'])
        writer.writerows(zip(referenceStrength, frequencyStrength))

def normalizeToReference(volts, referenceVolts):
    return volts / referenceVolts
```

**Continuous & FlowCell only:**
- `performSweepAndWaitForComplete()` - Full sweep implementation
- `calibrationComparison()` - Array-based calibration

**RollerBottle & Tunair only:**
- `prepareSweep()` - Separate sweep preparation
- `performSweep()` - Separate sweep execution
- `calibrationPointComparison()` - Single point calibration

**Tunair only:**
- `performRandomSweep()` - Complex random sampling logic

---

## Summary of Key Differences

| Feature | Continuous | FlowCell | RollerBottle | Tunair |
|---------|-----------|----------|--------------|--------|
| **Scan Method** | Basic sweep | Basic sweep | VNA optimizer | Random sweep |
| **Initial Spike Handling** | Subtracts from start freq | Subtracts from start freq | No adjustment | No adjustment |
| **Reference Frequency** | Not used (pass) | Not used (pass) | Used (peak-10) | Used (peak-10) |
| **Initialize** | No wake() | Calls wake() | Calls wake() + write_asf() | Calls wake() + write_asf() |
| **Start/Stop Init** | None | None | From properties | From properties |
| **Calibration Method** | Array comparison | Array comparison | Point comparison | Point comparison |
| **Sweep Implementation** | performSweepAndWaitForComplete | performSweepAndWaitForComplete | prepareSweep + performSweep | prepareSweep + performSweep |
| **Error Messages** | "Reader Port" | "Reader hardware disconnected" | "Reader Port" | "Reader Port" |
| **Exception Handling** | Basic | Extended (FileNotFoundError) | Basic | Basic |
| **Step Size Calculation** | Hardcoded 1000/10 | Hardcoded 1000/10 | From ContextFactory | From ContextFactory |

---

## Refactoring Recommendations

### Phase 1: Create Base SIB Class
Extract all identical methods to `BaseSib` class:
- `getYAxisLabel()`
- `estimateDuration()`
- `getCurrentlyScanning()`
- `getCalibrationFilePresent()`
- `setNumberOfPoints()`
- `close()`
- `reset()`
- `performHandshake()`
- `getFirmwareVersion()`
- `resetDDSConfiguration()`
- `resetSibConnection()`

### Phase 2: Create Shared Utility Module
Move all identical module-level functions to `sib_utils.py`:
- `createCalibrationFile()`
- `find_nearest()`
- `createCalibrationDirectoryIfNotExists()`
- `convertAdcToVolts()`
- `findSelfResonantFrequency()`
- `removeInitialSpike()`

### Phase 3: Template Method Pattern
Create abstract methods or hooks for varying behavior:
- `_initialize_hardware()` - Hook for wake/write_asf differences
- `_apply_spike_adjustment()` - Hook for spike handling
- `_perform_scan_implementation()` - Abstract method for scan strategy
- `_get_num_points_calculator()` - Strategy for calculation method

### Phase 4: Configuration-Driven Differences
Use configuration or class variables for:
- Error message templates
- Whether to use reference frequency
- Step size calculation method

### Phase 5: Strategy Pattern for Scanning
Create separate strategy classes:
- `BasicScanStrategy` (Continuous/FlowCell)
- `OptimizedScanStrategy` (RollerBottle)
- `RandomScanStrategy` (Tunair)

## Estimated Code Reduction
- **Current:** ~1,400 lines across 4 files
- **After refactoring:** ~700-800 lines total (40-45% reduction)
  - Base class: ~300 lines
  - Shared utils: ~100 lines
  - Each implementation: ~75-100 lines each
