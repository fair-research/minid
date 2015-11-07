from app import app, db
from api import *
from models import *


def create_db():
    db.create_all()

if __name__ == '__main__':
    app.run()
