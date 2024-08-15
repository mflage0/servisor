# -*- coding: utf-8 -*-
"""
File Name：     application
Description :
date：          2024/8/9 009
"""
from flask import Flask, url_for, session, redirect, abort
from config import client_id, client_secret, endpoint
from authlib.integrations.flask_client import OAuth
from views.v1 import api_v1, login_required
from threading import Timer
from uilt.core import servisord, keep_web
from flask_cors import *
import subprocess
import uuid
import os

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.urandom(24)  # 确保你的会话数据是安全的

# 注册蓝图
app.register_blueprint(api_v1, url_prefix='/api/v1')

# 初始化OAuth
oauth = OAuth(app)
oauth.register(
    name='cloudflare',
    client_id=client_id,
    client_secret=client_secret,
    server_metadata_url=f'{endpoint}/cdn-cgi/access/sso/oidc/{client_id}/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile groups',
    }
)


# 生成 nonce 的函数
def generate_nonce():
    return str(uuid.uuid4())


@app.route('/login')
def login():
    # 生成一个 nonce 并保存到会话中
    nonce = generate_nonce()
    session['nonce'] = nonce

    # 进行 OAuth 2.0 重定向
    redirect_uri = url_for('authorize', _external=True)
    return oauth.cloudflare.authorize_redirect(redirect_uri, nonce=nonce)


@app.route('/oauth2/callback')
def authorize():
    try:
        # 从会话中获取 nonce
        nonce = session.pop('nonce', None)

        if not nonce:
            raise ValueError("Missing nonce in session. Potential CSRF attack.")

        # 获取访问令牌
        token = oauth.cloudflare.authorize_access_token()

        if token is None:
            raise ValueError("Failed to retrieve access token. Received None.")

        # 使用 nonce 解析 ID 令牌
        user_info = oauth.cloudflare.parse_id_token(token, nonce=nonce)

        if user_info is None:
            raise ValueError("Failed to parse user information from ID token.")

        # 将用户信息保存到会话中
        session['user'] = user_info

        return redirect('/')

    except Exception as e:
        print(f"Authorization error: {str(e)}")
        abort(500, 'An error occurred during the authorization process.')


@app.route('/web')
def protected():
    servisord()
    return "<h1>Servisor By <a href='https://github.com/mflage0'>mflage</a></h1>"


@app.route("/", methods=['GET'])
@login_required
def root():
    servisord()
    return open('static/info.html')


def loop_main(inc):
    t = Timer(inc, loop_main, (inc,))
    servisord()
    keep_web()
    t.start()


if __name__ == "__main__":
    app.run()
    loop_main(300)
