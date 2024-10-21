# Skroot Desktop Application
This application is designed to be used in conjuction with a Skroot SIB to take scans, analyze them and plot them for the user's visualization.
## Technical Requirements
- Running on a linux or windows machine
- Currently runs on the Tkinter framework
- Requires the `sibcontrol` package included in the project to be installed to pip
- If running on linux, downloaded all of the modules in:
  - `src/resources/scripts/requirements.txt`
- If running on Windows, downloaded all of the modules in:
  - `src/resources/scripts/win-requirements.txt`
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

# Git Management
## Main Branches
- `master-R&D` is the master branch for the R&D track.
- `master` is the master branch for the Manufacturing track.

### Applying changes from one branch to both R&D and Manufacturing
1. Create the change based off of either `master` or `master-R&D`
   2. For this example will create them off of `master`
3. Merge the changes into `master`
3. git checkout -b `branch_name` `origin/master-R&D`
   4. Creates a branch called `branch_name` based off of `origin/master-R&D`
4. git cherry-pick `origin/master`
   5. Grabs the last commit from `origin/master` and applied it to `branch_name`
5. Merge `branch_name` into `master-R&D`