#!/usr/bin/env bash
set -o errexit

python -m pip install --upgrade pip
python -m pip install -r requirements-prod.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py ensure_demo_admin
