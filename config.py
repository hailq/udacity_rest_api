# Application directory
import os


class Config(object):
    # Enabling the development environment
    DEBUG = False
    TESTING = False
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class ProductionConfig(Config):
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///meetneat.db'


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///meetneat_dev.db'
    DEBUG = True


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///meetneat_test.db'
    TESTING = True


configs = {
    'development': DevelopmentConfig,
    'testing': TestingConfig
}

configuration = configs[os.getenv('UDACITY_ENVIRONMENT', 'development')]
