import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or 'hard to guess string'
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.googlemail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.getenv("USER_EMAIL")
    MAIL_PASSWORD = os.getenv("USER_PASSWORD")
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <hotel.api.flask@gmail.com>'
    FLASKY_ADMIN = os.getenv("FLASK_ADMIN")
    FLASKY_POSTS_PER_PAGE = 10
    FLASKY_FOLLOWERS_PER_PAGE = 20
    FLASKY_FOLLOWED_PER_PAGE = 20
    FLASKY_COMMENTS_PER_PAGE = 10
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URL") or 'sqlite:///database.db'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL") or "sqlite://"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or "sqlite:///database.db"


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
