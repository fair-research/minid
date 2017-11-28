class Config(object):
    """Don't store your secrets here! Instead, create a file called
    'local_config.py' which will override settings below and isn't
    tracked by git to avoid accidental VC checkins.
    """
    DEBUG = True
    TESTING = True

    SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/minid.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    HOSTNAME = "http://localhost:5000/minid"
    LANDING_PAGE = "http://localhost:5000/minid/landingpage"

    EZID_SERVER = "https://ezid.cdlib.org"
    EZID_SCHEME = "ark:/"
    EZID_SHOULDER = "99999/fk4"
    EZID_USERNAME = "apitest"
    EZID_PASSWORD = "apitest"

    TEST_EZID_SERVER = "https://ezid.cdlib.org"
    TEST_EZID_SCHEME = "ark:/"
    TEST_EZID_SHOULDER = "99999/fk4"
    TEST_EZID_USERNAME = "apitest"
    TEST_EZID_PASSWORD = "apitest"

    AWS_ACCESS_KEY_ID = ""
    AWS_SECRET_ACCESS_KEY = ""
