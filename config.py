# -*- coding: utf-8 -*-
"""
File Name：     config
Description :   配置文件内容，未注释行请勿随意修改
date：          2024/8/9 009
"""
import os
import subprocess
import configparser

configparse = configparser.ConfigParser()

username = subprocess.run(['whoami'], capture_output=True, text=True).stdout.strip()


# # Access -> Application -> Add an Application -> SaaS -> OIDC
# client_id = '9afb6ae9523ec07a831e818069c54ee3de7aef50efb2fee73032e5671358b060'
# client_secret = 'dc6b9be8edf08ab5d7cc6239fb4b48eab994b0633ebe2f8b696eae9045d72f62'
# endpoint = 'https://mflage0.cloudflareaccess.com'  # Access -> Application -> Application URL -> 只保留协议+域名的部分，路径不需要
