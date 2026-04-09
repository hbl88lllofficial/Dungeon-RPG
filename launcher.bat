@echo off
REM
cd /d "%~dp0"

where py >nul 2>&1
if %ERRORLEVEL%==0 (
	py main.py
	goto :EOF
)

where python >nul 2>&1
if %ERRORLEVEL%==0 (
	python main.py
	goto :EOF
)

echo Python nao foi encontrado no PATH.
echo Instale o Python e marque "Add Python to PATH" durante a instalacao,
echo ou instale via Microsoft Store e habilite o alias de execucao.
echo Mais info: https://www.python.org/downloads/
pause
