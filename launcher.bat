@echo off
echo Ativando ambiente virtual...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Erro ao ativar o ambiente virtual. Verifique se o .venv existe.
    pause
    exit /b 1
)
echo Executando o jogo RPG...
python main.py
pause