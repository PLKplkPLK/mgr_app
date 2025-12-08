./venv/bin/python manage.py runserver &

./tailwindcss-linux-x64 \
  -i account/static/account/css/input.css \
  -o account/static/account/css/output.css \
  --watch &

./tailwindcss-linux-x64 \
  -i gallery/static/gallery/css/input.css \
  -o gallery/static/gallery/css/output.css \
  --watch &

./tailwindcss-linux-x64 \
  -i photo/static/photo/css/input.css \
  -o photo/static/photo/css/output.css \
  --watch &
