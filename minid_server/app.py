#!flask/bin/python
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from email_sender import SESEmail

app = Flask(__name__)
app.config.from_object('config.BaseConfig')
db = SQLAlchemy(app)
minid_email = SESEmail(app)

print("Running")
