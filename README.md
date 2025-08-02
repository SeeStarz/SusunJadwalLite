# SUSUN JADWAL (Lite, I guess)

Made this because <https://susunjadwal.cs.ui.ac.id> is outdated at the time of writing.  
Update 2025-08-03: They borked it again bruh.

## Requirements
Highlighted in [Run Options](#run-options).  
Also, `git`. Unless if you want to download the repository zip and unzip it manually.
You can skip the clone step if you decide to do that.

## Setup

- Clone this repository: `git clone https://github.com/SeeStarz/SusunJadwalLite.git`
- Download the latest schedule from <https://academic.ui.ac.id/main/Schedule/> and save it as `jadwal.html` replacing the built in one (optional)
- Edit `main.py` as instructed by the `TODO:` comments at the top of the file
- [Ensure you are in the project root](#am-i-in-the-correct-directory)
- [Run the script](#run-options)

## Run Options

### Docker
Probably the most reproducible way to run this. Pretty overkill though.
- Ensure docker is installed (my version is 28.3.3)
- Run `docker build -t susun-jadwal-lite:latest . && docker run susun-jadwal-lite`

### Python virtual environment
A pretty standard way, I suppose.
- Ensure python3 is installed (my version is 3.13.5)
- Ensure pip is installed (my version is 25.1.1)
- Create virtual environment `python3 -m venv pyvenv`
- Activate virtual environment 
  - Windows Powershell: `.\pyvenv\Scripts\Activate.ps1`
  - Windows CMD: `.\pyvenv\Scripts\activate.bat`
  - Linux/MacOS: `source pyvenv/bin/activate`
  - Fish shell (my beloved): `source pyvenv/bin/activate.fish`
- Install dependencies `pip install -r requirements.txt`
- Run `python3 main.py`

### Just simply python
You can do this if you're using a similar python version as I am and have the dependencies installed.
- Ensure python3 is installed (my version is 3.13.5)
- Ensure bs4 module is installed (maybe others? idk, check requirements.txt)
- Run `python3 main.py`

## Troubleshoot
### Am I in the correct directory?
- Are you opening from a file manager? (e.g. windows file explorer, macOS finder, linux dolphin) If so, make sure `jadwal.html` and `main.py` is there along with other misc files.
- Are you in a terminal/shell? Try running `dir` or `ls` and make sure it shows `jadwal.html` and `main.py` along with other misc files.
- Tip: you can open windows cmd/powershell in the currect directory by clicking the path display and typing `cmd` or `powershell`

### Other problems?
Open up an issue or hit me up on line (mfahrim7) or discord (SeeStarz)
