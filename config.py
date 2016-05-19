import os
basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'wakalive'

#sql
SQLALCHEMY_DATABASE_PATH = os.path.join(basedir, 'app.db')
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + SQLALCHEMY_DATABASE_PATH
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True

#lecloud
LECLOUD_USERID=
LECLOUD_SECRETKEY=''

#leancloud
LEANCLOUD_APPID = ''
LEANCLOUD_APPKEY = ''
