import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.getenv("SECRET_KEY", "default-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

class Production(Config):
    DEBUG = False

class Staging(Config):
    DEVELOPMENT = True
    DEBUG = True

class Development(Config):
    DEVELOPMENT = True
    DEBUG = True

