@echo off
setlocal
cd /d "%~dp0\.."
where py >nul 2>nul && (set "PY=py -3") || (set "PY=python")
if exist reproduced_results rmdir /s /q reproduced_results
mkdir reproduced_results
set PYTHONPATH=src
%PY% -m unittest discover -s tests -v || exit /b 1
%PY% -m awas_sim.cli --episodes 20000 --seed 7 --out reproduced_results || exit /b 1
%PY% scripts\compare_frozen.py reproduced_results || exit /b 1
endlocal
