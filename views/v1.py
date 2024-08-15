# -*- coding: utf-8 -*-
"""
File Name：     v1
Description :
date：          2024/8/9 009
"""
import os
import re
import config
import subprocess
from functools import wraps

import control
from config import venv_path, servisor_path, username
from uilt.core import servisord, get_param_config
from flask import Blueprint, redirect, url_for, jsonify, request, session

api_v1 = Blueprint('user', __name__)
config_path = os.path.expanduser(f'{servisor_path}/etc/supervisord.conf')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            # 如果用户没有登录，重定向到登录页面
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@api_v1.before_request
@login_required
def before_request():
    pass


@api_v1.route("/info", methods=['GET'])
def index():
    supervisor_version = subprocess.run(
        [f'{venv_path}/bin/supervisord', '-v'], capture_output=True, text=True).stdout.strip()
    supervisor_param = subprocess.run([f'{venv_path}/bin/supervisorctl', '-c', config_path, 'status'],
                                      capture_output=True, text=True)
    if supervisor_param.returncode in [0, 3]:
        supervisor_status = 'running'
    else:
        supervisor_status = 'stop'
    supervisor_param_config = supervisor_param.stdout.strip().split('\n')

    pattern = r"^(\S+)\s+(RUNNING|STOPPED|STARTING|BACKOFF|STOPPING|EXITED|FATAL|UNKNOWN)"
    relu = {'supervisor_version': supervisor_version, 'supervisor_status': supervisor_status, 'data': []}
    for param_config in supervisor_param_config:
        match = re.match(pattern, param_config)
        if match:
            name = match.group(1)
            status = match.group(2)
            # pid = match.group(3)
            # uptime = match.group(4)
            param_info = get_param_config(name)
            if param_info:
                command = param_info['command']
                directory = param_info['directory']
                relu['data'].append(
                    dict(name=name, status=status, pid=None, uptime=None, command=command, directory=directory))
    return jsonify(relu)
    # return render_template('index.html', data=relu)


@api_v1.route("/stop", methods=['GET'])
def stop():
    # subprocess.run([f'{venv_path}/bin/supervisorctl', '-c', config_path, 'shutdown'], capture_output=True, text=True)
    # control.supervisor_flag = False
    return redirect(url_for('.index'))


@api_v1.route("/restart", methods=['GET'])
def restart():
    control.supervisor_flag = True
    servisord()
    return redirect(url_for('.index'))


@api_v1.route("/setting", methods=['GET', 'PUT'])
def setting():
    with open(f'{config_path}', 'r', encoding='utf-8') as f:
        setting_config_source = f.read()
    if request.method == "GET":
        return setting_config_source
    elif request.method == "PUT":
        data = request.get_json()
        setting_config = data.get('setting_config')
        if setting_config:
            with open(f'{config_path}', 'w', encoding='utf-8') as f:
                f.write(setting_config)
            if subprocess.run(
                    [f'{venv_path}/bin/supervisorctl', '-c', config_path, 'update'],
                    capture_output=True,
                    text=True).returncode == 0:
                return jsonify({"msg": "配置文件重载成功"})
            else:
                with open(f'{config_path}', 'w', encoding='utf-8') as f:
                    f.write(setting_config_source)
                return jsonify({"msg": "配置文件重载失败，已回滚"}), 500


@api_v1.route("/process/<process_name>", methods=['GET', 'PUT', 'POST', 'DELETE'])
def process(process_name):
    process_config = None
    try:
        with open(f'{servisor_path}/supervisor.d/{process_name}.ini', 'r', encoding='utf-8') as f:
            process_config_source = f.read()
    except FileNotFoundError as e:
        process_config_source = None
    if request.method == "GET":
        return process_config_source
    elif request.method == "PUT":
        data = request.get_json()
        process_config = data.get('process_config')
    elif request.method == "POST":
        data = request.get_json()
        command = data.get('command')
        directory = data.get('directory')
        process_config = f"""[program:{process_name}]
command                 = {command}
directory               = {directory}
autorestart             = true
startsecs               = 3
stdout_logfile          = {servisor_path}/log/{process_name}.out.log
stderr_logfile          = {servisor_path}/log/{process_name}.err.log
stdout_logfile_maxbytes = 2MB
stderr_logfile_maxbytes = 2MB
user                    = {username}
priority                = 999
numprocs                = 1"""
    elif request.method == "DELETE":
        os.remove(f'{servisor_path}/supervisor.d/{process_name}.ini')
        if subprocess.run([f'{venv_path}/bin/supervisorctl', '-c', config_path, 'update'],
                          capture_output=True,
                          text=True).returncode == 0:
            return jsonify({"msg": f"{process_name}删除成功"})
        else:
            return jsonify({"msg": f"{process_name}删除失败"}), 500
    if process_config:
        with open(f'{servisor_path}/supervisor.d/{process_name}.ini', 'w', encoding='utf-8') as f:
            f.write(process_config)
        if subprocess.run([f'{venv_path}/bin/supervisorctl', '-c', config_path, 'update'],
                          capture_output=True,
                          text=True).returncode == 0:
            return jsonify({"msg": "配置文件重载成功"})
        else:
            return jsonify({"msg": "请检查配置是否错误或守护进程是否运行成功"}), 500
    else:
        return jsonify({"msg": "内部错误"})


@api_v1.route("/log/<process_name>/<log_type>", methods=['GET'])
def log(process_name, log_type):
    if log_type not in ['err', 'out']:
        return jsonify({"msg": "参数不合法"}), 500
    else:
        with open(f'{servisor_path}/log/{process_name}.{log_type}.log', 'r', encoding='utf-8') as f:
            return f.read()


@api_v1.route("/process", methods=['POST'])
def process_setting():
    data = request.get_json()
    name = data.get('name')
    operate = data.get('operate')
    if not name or not operate:
        return jsonify({"msg": "缺少关键参数"}), 500
    elif operate not in ['start', 'stop', 'restart']:
        return jsonify({"msg": "参数不合法"}), 500
    else:
        if subprocess.run([f'{venv_path}/bin/supervisorctl', '-c', config_path, operate, name],
                          capture_output=True,
                          text=True).returncode == 0:
            return jsonify({"msg": "success"})
        else:
            return jsonify({"msg": "failure"}), 500
