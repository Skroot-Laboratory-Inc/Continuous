import os
import sys
import tkinter.filedialog

from src.resources.scripts.post_processing.analyzer import PostProcessingAnalyzer

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

print("Please select the experiment directory you would like to analyze.")
experimentFolderDirectory = tkinter.filedialog.askdirectory()
equilibrationTime = input("Enter Equilibration Time in hours: ")
analyzer = PostProcessingAnalyzer(experimentFolderDirectory, float(equilibrationTime))
analyzer.getScansForReaders()
analyzer.analyzeReaderScans()
analyzer.createSummaryAnalyzed()
print(f"Finished processing. You can find the summary file in {experimentFolderDirectory}/Post Processing/summaryAnalyzed.csv")
