# -*- coding: utf-8 -*-
"""
File Name：     passenger_wsgi
Description :
date：          2024/8/9 009
"""
import sys, os

sys.path.append(os.getcwd())
from application import app as application
