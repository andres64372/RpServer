#!/bin/sh

source venv/bin/activate
git pull origin main
sudo pkill gunicorn
gunicorn --worker-class eventlet -w 1 main:app --daemon