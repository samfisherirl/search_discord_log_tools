@echo off
SET venv_dir=venv
SET python=%venv_dir%\Scripts\python.exe
SET icon=app.ico
SET pyinstaller=%venv_dir%\Scripts\pyinstaller.exe

CALL .\venv\Scripts\activate

"%python%" -m pip install --upgrade setuptools pyinstaller

"%pyinstaller%" --console --onefile --icon="%icon%"  --noconfirm --clean --add-data="venv\Lib\site-packages\sv_ttk;sv_ttk"  --add-data="venv\Lib\site-packages\babel;babel" "discord_search.py"
