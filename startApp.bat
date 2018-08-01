@ECHO OFF
TITLE WINDOWS_MONITOR APP
set mypath=%cd%
IF EXIST %mypath%\venv\ (
goto :allok
) ELSE (
echo INSTALLING PYTHON VIRTUAL ENV, PLEASE WAIT ...
goto :installvenv
)
:installvenv
set venvPath=%mypath%\venv\Scripts
set venvinstallCommand="cd /d %mypath% & python -m venv venv & cd /d %venvPath% & activate & cd /d %mypath% & python -m pip install --upgrade pip & pip install -r requirements.txt & cls & python -m bin.main.MainApp"
cmd /k %venvinstallCommand%
:allok
set venvPath=%mypath%\venv\Scripts
set venvCommand="cd /d %venvPath% & activate & cd /d %mypath% & python -m bin.main.MainApp"
cmd /k %venvCommand%