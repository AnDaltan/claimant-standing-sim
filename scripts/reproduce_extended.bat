@echo off
setlocal
cd /d "%~dp0\.."
where py >nul 2>nul && (set "PY=py -3") || (set "PY=python")
if not exist reproduced_results mkdir reproduced_results
set PYTHONPATH=src
%PY% -m awas_sim.sweep --episodes 3000 --seed 71 --out reproduced_results || exit /b 1
%PY% scripts\compare_frozen.py reproduced_results || exit /b 1
endlocal
