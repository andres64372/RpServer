#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/RetroPixel/")

from main import app as application
application.secret_key = 'R1BhE53$yt76$RR1hB5YJM'