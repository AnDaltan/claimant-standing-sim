@echo off
setlocal
cd /d "%~dp0\.."
where py >nul 2>nul && (set "PY=py -3") || (set "PY=python")
if not exist reproduced_results mkdir reproduced_results
set PYTHONPATH=src
%PY% -m awas_sim.sensitivity --seeds 12 --episodes 4000 --out reproduced_results || exit /b 1
%PY% -m awas_sim.reach --episodes 10000 --seed 97 --out reproduced_results || exit /b 1
%PY% scripts\compare_frozen.py reproduced_results || exit /b 1
endlocal
