@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

REM  uv is used here largely because it makes installation of Python easy.
REM  At least, it is easier than installing Python manually.

REM  Checks for existence of uv
TYPE %USERPROFILE%\.local\bin\uv.exe >nul 2>nul

REM  If it doesn't exist, let's install uv
REM  Installation is very simple (just run a command), but we do need to adjust
REM  the execution policy to install it. We revert it back afterwards.
REM  Note that the for statement here simply gets the current execution policy.
 
IF %ERRORLEVEL% NEQ 0 (
  FOR /F "tokens=* USEBACKQ" %%F IN (`powershell -c "Get-ExecutionPolicy -Scope CurrentUser"`) DO (SET CURSCOPE=%%F)
  powershell -c "Set-ExecutionPolicy Bypass -scope CurrentUser"
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  powershell -c "Set-ExecutionPolicy !CURSCOPE! -scope CurrentUser"
)

REM  Simple check to see if uv has already installed a virtual environment.
REM  uv does not work without it.
DIR ".venv" >nul 2>nul

IF %ERRORLEVEL% NEQ 0 (
  %USERPROFILE%\.local\bin\uv venv --python 3.10
)

REM  From here, everything is relatively standard stuff, except we use uv.
%USERPROFILE%\.local\bin\uv pip install -r requirements.txt

%USERPROFILE%\.local\bin\uv run main.py
PAUSE