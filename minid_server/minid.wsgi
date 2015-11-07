#!/usr/bin/python
import sys
import os
import logging

logging.basicConfig(stream=sys.stderr)

#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from app import app as application
from app import  db
from api import *
from models import *

