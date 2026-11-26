#!/bin/bash

#run migrations
python manage.py migrate

# Start gunicorn
gunicorn pickleball.wsgi:application