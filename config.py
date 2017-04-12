class Config(object):
    """
    Common configurations
    """

    DEBUG = True


class DevelopmentConfig(Config):
    """
    Development configurations
    """

    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False
    """
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'addictionhelp365@gmail.com'
    MAIL_PASSWORD = 'd43nk654'
    MAIL_DEFAULT_SENDER = '"Recover" <noreply@gmail.com>'

    ADMINS = [
        '"Admin One" <kelly.mark.76@gmail.com>',
        ]
    """

class TestingConfig(Config):
    """
    Testing configurations
    """

    TESTING = True

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
