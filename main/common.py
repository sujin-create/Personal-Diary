
from main import *
from flask import Blueprint,send_from_directory
from string import digits, ascii_uppercase, ascii_lowercase
import random

def login_required(f):
    @wraps(f)
    def decorated_fuction(*args, **kwargs):
        if session.get("id") is None or session.get("id")=="":
            return redirect(url_for("member.login",next_url = request.url))
        return f(*args,**kwargs)
    return decorated_fuction


def file_ch(filename):
    return "." in filename and filename.rsplit(".",1)[1] in ALLOWED_EXTENSIONS
# 가장 마지막 .1개만을 가지고 그 기준으로 파일명의 확장자 체크하기 위해 생성 

def generator(length=8):
    char = ascii_lowercase+ ascii_uppercase+digits
    return "".join(random.sample(char, length))
