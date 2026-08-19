@echo off
rem Starts the uhta crew console (launch pipelines, runs & artifacts,
rem canon bible) and opens it in the browser. Ctrl+C in this window stops it.
cd /d "%~dp0"
python run_console.py
