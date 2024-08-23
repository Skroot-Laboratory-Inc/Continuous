import tkinter.filedialog

from src.resources.scripts.post_processing.analyzer import PostProcessingAnalyzer

print("Please select the experiment directory you would like to analyze.")
experimentFolderDirectory = tkinter.filedialog.askdirectory()
equilibrationTime = input("Enter Equilibration Time in hours: ")
analyzer = PostProcessingAnalyzer(experimentFolderDirectory, float(equilibrationTime))
analyzer.getScansForReaders()
analyzer.analyzeReaderScans()
analyzer.createSummaryAnalyzed()
print(f"Finished processing. You can find the summary file in {experimentFolderDirectory}/Post Processing/summaryAnalyzed.csv")
