#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#app config
DEBUG=True
SQLALCHEMY_DATABASE_URI='mysql+pymysql://test_user_1:test_user_1@localhost:3306/awesome_web_app?charset=utf8'
SQLALCHEMY_ECHO=False
SQLALCHEMY_TRACK_MODIFICATIONS=True

import os
UPLOAD_FOLDER='./app/static/img/avatar/'
ALLOWED_EXTENDSIONS=set(['jpg','png','jpeg'])
MAX_CONTENT_LENGTH=16*1024*1024

#login_config
SECRET_KEY='youwillneverguess'  #also mysql root password

#page
BLOGS_PER_PAGE=5