class DevConfig:
    SECRET_KEY = 'thisisakey'
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_DATABASE_URI = "sqlite:///cems.db"
    SQLALCHEMY_DATABASE_URI = "mysql://root:GAEtan1234?@localhost:3306/cems"

class ProdConfig:
    SECRET_KEY = '62c1e134f6e207e83acebdb62b67a12aeba4467e87835057a8da42c9aeef9938'
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "mysql://gaetan:GAEtan1234?@176.58.124.50:3306/cems"