import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))
imagesdir = basedir + '\\app\\static\\images\\products'


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
                                             'sqlite:///app.db')
    UPLOAD_FOLDER = imagesdir
    PAGE_LENGTH = 10


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    WTF_CSRF_ENABLED = False
    WTF_CSRF_METHODS: list = []
    SECRET_KEY = 'you-will-never-guess'
    SERVER_NAME = 'localhost:5000'
    APPLICATION_ROOT = '/'
