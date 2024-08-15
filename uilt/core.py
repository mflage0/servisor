# -*- coding: utf-8 -*-
"""
File Name：     core
Description :
date：          2024/8/9 009
"""
import os

import requests

import control
import subprocess
from config import servisor_path, venv_path, configparse, username

config_path = os.path.expanduser(f'{servisor_path}/etc/supervisord.conf')
server_host = subprocess.run(['hostname'], capture_output=True, text=True).stdout.strip()
server_host = 'ct8.pl' if 'ct8' in server_host else 'serv00.net'


def is_supervisord_running(config_path):
    """
    检查 supervisord 是否在运行
    :return: 如果正在运行，返回 True；否则返回 False
    """
    try:
        # 运行 `supervisorctl status` 来检查 supervisord 是否在运行
        result = subprocess.run([f'{venv_path}/bin/supervisorctl', '-c', config_path, 'status'], capture_output=True,
                                text=True)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        print("supervisorctl 未安装或路径错误，请确认已安装 supervisor 并配置 PATH")
        return False


def start_supervisord(config_path):
    """
    启动 supervisord 守护进程
    :param config_path: supervisord 配置文件的路径
    """
    try:
        # 使用 subprocess 启动 supervisord
        subprocess.run([f'{venv_path}/bin/supervisord', '--minprocs', '5', '-c', config_path], check=True)
        print("supervisord 启动成功")
        # 检查并输出 supervisord 运行状态
        subprocess.run([f'{venv_path}/bin/supervisorctl', '-c', config_path, 'status'])
    except subprocess.CalledProcessError as e:
        print(f"启动 supervisord 失败: {e}")
    except FileNotFoundError:
        print("supervisord 未安装或路径错误，请确认已安装 supervisor 并配置 PATH")


def servisord():
    if is_supervisord_running(config_path):
        print("supervisord 已在运行")
    else:
        # if control.supervisor_flag:
        print("supervisord 未运行，正在启动...")
        start_supervisord(config_path)


def keep_web():
    try:
        requests.get(f"https://{username}.{server_host}/web", timeout=3)
    except Exception as e:
        ...

def get_param_config(param_name):
    try:
        with open(f'{servisor_path}/supervisor.d/{param_name}.ini', 'r', encoding='utf-8') as f:
            configparse.read_string(f.read())
        section = f'program:{param_name}'
        config_dict = {section: dict(configparse.items(section)) for section in configparse.sections()}
        if section in configparse:
            return config_dict[section]
    except Exception as e:
        return None
