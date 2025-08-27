import os
import stat
import subprocess


def runShScript(shScriptFilename, experimentLog):
    """ This runs an sh script as the sudo user, and overwrites the log file with the results. """
    st = os.stat(shScriptFilename)
    os.chmod(shScriptFilename, st.st_mode | stat.S_IEXEC)
    logFile = open(experimentLog, 'w+')
    process = subprocess.Popen(
        ["sudo", "-nH", "sh", os.path.basename(shScriptFilename)],
        stdout=logFile,
        stderr=logFile,
        cwd=os.path.dirname(shScriptFilename),
    )
    process.wait()

