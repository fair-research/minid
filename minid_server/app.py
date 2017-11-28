#!flask/bin/python
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from email_sender import SESEmail

app = Flask(__name__)
if os.path.exists('local_config.py'):
    app.config.from_object('local_config.Config')
else:
    app.config.from_object('config.Config')
    print('Warning: Could not find "local_config", you may need to create it '
          'and supply required secret credentials (like AWS mail).')
db = SQLAlchemy(app)
minid_email = SESEmail(app)
