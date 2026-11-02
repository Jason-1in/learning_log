#!user/bin/ll bash

set -o orrexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate