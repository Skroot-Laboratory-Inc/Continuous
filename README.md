# Skroot Desktop Application
This application is designed to be used in conjuction with a Skroot SIB to take scans, analyze them and plot them for the user's visualization.
## Technical Requirements
- Running on a linux or windows machine
- Currently runs on the Tkinter framework
- If running on linux, downloaded all of the modules in:
  - `src/resources/scripts/requirements.txt`
- If running on Windows, modules required TBD
## Running the application
Run the `src/app/main.py` file
- The current working directory, no matter what file the code is in will be `src/app`
## Project Structure
The project runs on three main folders, app, test and resources
### App
These files are the files executed at runtime to run the application
### Test
These files are where automated testing suites are utilized for code quality.
### Resources
These files are static files used throughout the codebase, and by developers for accelerated development.