## Functions of main_shared

- setupApp/guidedSetup: Creates the menubar and generates the guided setup form
- createRoot: Sets the closing function and fullscreens the app, registers create_circle
  - onClosing: destroys the app
- mainLoop: Loops through the readers, *Should be its own file!*
  - checkIfScanTookTooLong, waitUntilNextScan
- awsCheckSoftwareUpdates: checks if a software update is required
- downloadSoftwareUpdate: Downloads the available update
- awsUploadPdfFile: Uploads the pdf
- awsUploadLogFile: Uploads the log
- plotSummary, createSummaryAnalyzed: self explanatory
- copyFilesToDebuggingFolder/AnalysisFolder, resetRun
- showFrame: raises a frame to the toplevel

### Proposed solution

- Create a main_setup.py
  - guidedSetup, setupApp, createRoot, onClosing
- Create an end_experiment.py
  - copyFilesToDebuggingFolder, copyFilesToAnalysisFolder, resetRun
- Create a main_aws_service.py
  - awsCheckSoftwareUpdates, downloadSoftwareUpdate, awsUploadPdfFile, awsUploadLogFile
- Create a main_thread_manager.py
  - mainLoop, checkIfScanTookTooLong, waitUntilNextScan
