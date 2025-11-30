@echo off
setlocal
REM Simple launcher for the Streamlit app on Windows (Command Prompt).

REM Move to project root (folder above this scripts directory)
pushd %~dp0..

REM Load .env if present
if exist .env (
  for /f "usebackq tokens=1,* delims==" %%a in (`findstr /r "^[A-Za-z0-9_][A-Za-z0-9_]*=" ".env"`) do set %%a=%%b
)

REM Create venv if missing
if not exist .venv (
  python -m venv .venv
)

REM Activate venv
call .venv\Scripts\activate

REM Install requirements (safe to re-run)
pip install --upgrade pip
pip install -r requirements.txt

REM Run Streamlit
streamlit run app.py
popd
endlocal
