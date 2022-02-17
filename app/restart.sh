#!/bin/sh

cd /home/admin/RpServer/app
git pull origin main
sudo service nginx restart
source venv/bin/activate
sudo pkill gunicorn
gunicorn --worker-class eventlet -w 1 main:app --daemon