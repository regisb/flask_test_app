from flask import Flask

app = Flask(__name__)

# Config options - Make sure you created a 'config.py' file.
app.config.from_object('config')
# app.config.from_envvar('YOURAPPLICATION_SETTINGS')

from app import views, models
