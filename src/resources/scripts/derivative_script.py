import os
import sys
import tkinter.filedialog

try:
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
except KeyError:
    desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
    sys.path = [
        '/usr/lib/python3.10',
        '/usr/lib/python3.10/lib-dynload',
        '/usr/local/lib/python3.10/dist-packages',
        '/usr/lib/python3/dist-packages',
        '.',
        '../../..',
    ]

from src.resources.scripts.derivative.analyzer import DerivativeAnalyzer

print("Please select the experiment directory you would like to analyze.")
experimentFolderDirectory = tkinter.filedialog.askdirectory()
equilibrationTime = input("Enter Equilibration Time in hours: ")
analyzer = DerivativeAnalyzer(experimentFolderDirectory, float(equilibrationTime))
analyzer.loadReaderAnalyzed()
analyzer.calculateDerivative()
analyzer.createDerivativeSummaryAnalyzed()
print(f"Finished processing. You can find the summary file in {experimentFolderDirectory}/Post Processing/derivativeSummaryAnalyzed.csv")
