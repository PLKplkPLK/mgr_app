start cmd /k "title django & .venv\Scripts\python.exe .\manage.py runserver 0.0.0.0:8000"
start cmd /k "title ml & ..\mgr_ml_server\.venv\Scripts\python.exe -m speciesnet.scripts.run_server --port=8008 --extra_fields=country"
