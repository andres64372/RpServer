#!/bin/sh

<<<<<<< HEAD
cd /home/admin/RpServer/app
=======
sudo service nginx restart
cd /home/admin/RpServer/app 
>>>>>>> 56728ef1984845af77b66fa6a9c8288cab5397cd
source venv/bin/activate
git pull origin main
sudo pkill gunicorn
gunicorn --worker-class eventlet -w 1 main:app --daemon
