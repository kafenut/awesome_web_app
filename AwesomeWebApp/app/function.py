#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from config import ALLOWED_EXTENDSIONS

def valid_profile(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENDSIONS


