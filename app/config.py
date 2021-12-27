from os import environ, path

from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

FLASK_APP = "app"
SECRET_KEY = environ.get("SECRET_KEY")
SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS = False

if environ.get("MODE") == "development":
    FLASK_ENV = "development"
elif environ.get("MODE") == "production":
    FLASK_ENV = "production"
elif environ.get("MODE") == "heroku":
    FLASK_ENV = "production"
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL").replace("postgres://", "postgresql://", 1)
