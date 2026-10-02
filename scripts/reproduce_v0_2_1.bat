@echo off
setlocal
cd /d "%~dp0\.."
where py >nul 2>nul && (set "PY=py -3") || (set "PY=python")
set OUT=reproduced_results\v0_2_1
if exist "%OUT%" rmdir /s /q "%OUT%"
mkdir "%OUT%"
set PYTHONPATH=src
%PY% -m unittest discover -s tests -v || exit /b 1
%PY% -m awas_sim.cli --episodes 20000 --seed 7 --ablation-set v0_2_1 --out "%OUT%" || exit /b 1
%PY% -m awas_sim.uncertainty --episodes 20000 --seed 7 --bootstrap 1000 --bootstrap-seed 20260928 --out "%OUT%" || exit /b 1
%PY% scripts\mechanism_probe.py --episodes 20000 --seed 7 --out "%OUT%" || exit /b 1
%PY% -m awas_sim.flip --episodes 5000 --seed 71 --bootstrap 400 --bootstrap-seed 20260929 --out "%OUT%" || exit /b 1
%PY% scripts\compare_frozen.py "%OUT%" results\v0_2_1 || exit /b 1
endlocal
