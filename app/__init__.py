from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
import os
from . import le

#initiate the app
app = Flask(__name__)
app.config.from_object('config')

#initiate the sqlalchemy
db = SQLAlchemy(app)

#initiate the LoginManager
login_manager = LoginManager(app)

#initiate the Lecloud
lecloud = le.WakaLive(app.config['LECLOUD_USERID'],app.config['LECLOUD_SECRETKEY'])

from app import views,models
if not os.path.exists(app.config['SQLALCHEMY_DATABASE_PATH']):
    db.create_all()
