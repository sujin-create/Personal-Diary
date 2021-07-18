
from flask import Flask, request,render_template,abort,redirect,url_for
from flask_pymongo import PyMongo
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import time
import math
from flask import flash, session
from jinja2.utils import environmentfunction
from functools import wraps
import os

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/myweb"
app.config["SECRET_KEY"] = "sujin"
app.config["PERMANET_SESSION_LIFETIME"] = timedelta(minutes=0.00000001)#30m제한
mongo = PyMongo(app)

BOARD_IMAGE_PATH = "C:\\images"
ALLOWED_EXTENSIONS = set(["txt","pdf","png","jpg","jpeg","gif"])

app.config["BOARD_IMAGE_PATH"]=BOARD_IMAGE_PATH
app.config["ALLOWED_EXTENSIONS"]=15*1024*1024


from .common import login_required
from .common import file_ch, generator #=> summernote사용하려고 했으나 jquery관련 문제로 보류
from .filter import format_datetime
from . import board
from . import member

app.register_blueprint(board.blueprint)
app.register_blueprint(member.blueprint)

