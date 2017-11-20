#encoding: utf-8

import os

DEBUG = True

SECRET_KEY = os.urandom(24)

HOSTNAME = '119.29.203.44'
PORT = '3306'
DATABASE = 'db_design'
USERNAME = 'sph'
PASSWORD = 'StrongPosHao'
DB_URI = 'mysql+mysqldb://{}:{}@{}:{}/{}?charset=utf8'.format(USERNAME,PASSWORD,HOSTNAME,PORT,DATABASE)

SQLALCHEMY_DATABASE_URI = DB_URI

SQLALCHEMY_TRACK_MODIFICATIONS = False