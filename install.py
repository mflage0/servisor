# -*- coding: utf-8 -*-
"""
File Name：     install
Description :
date：          2024/8/9 009
"""
import os
import sys
import time
import shutil
import subprocess
import threading


def spinner(exp):
    while not done_event.is_set():
        for char in '|/-\\':
            sys.stdout.write(f'\r{char} 正在{exp}...')
            sys.stdout.flush()
            time.sleep(0.5)


def execute_command(command, exp):
    global done_event
    done_event = threading.Event()

    # 启动转圈线程
    spinner_thread = threading.Thread(target=spinner, args=(exp,))
    spinner_thread.start()

    try:
        # 执行子进程
        process = subprocess.run(command, capture_output=True, text=True)
    finally:
        done_event.set()
        spinner_thread.join()

    sys.stdout.write(f'\r{exp}完成!         \n')
    return process


execute_command(['git', 'clone', 'https://github.com/mflage0/servisor.git'], '获取数据')
username = subprocess.run(['whoami'], capture_output=True, text=True).stdout.strip()
with open('servisor/config.py', 'a', encoding='utf-8') as f:
    servisor_path = input(f'请输入Servisor安装目录（/home/{username}/.servisor）:')
    servisor_path = servisor_path if servisor_path else f'/home/{username}/.servisor'
    venv_path = input(f'请输入虚拟环境安装目录（{servisor_path}/.venv）:')
    venv_path = venv_path if venv_path else f'{servisor_path}/.venv'
    python_path = f'{venv_path}/bin/python'
    f.write(f"servisor_path = '{servisor_path}'\n")
    f.write(f"venv_path = '{venv_path}'\n")
    f.write(f"python_path = '{python_path}'\n")

if not username:
    username = input("请输入用户名：")

server_host = subprocess.run(['hostname'], capture_output=True, text=True).stdout.strip()
server_host = 'ct8.pl' if 'ct8' in server_host else 'serv00.net'
host = f"{username}.{server_host}"

answer = input(f"Servisor需要占用{host}，请确认(Y/n)").strip().lower()
if answer == 'y' or answer == 'yes':
    subprocess.run(['devil', 'binexec', 'on'], capture_output=True, text=True)
    execute_command(['python', '-m', 'venv', venv_path], '创建Python环境')
    execute_command(['devil', 'www', 'del', f'{host}', '--remove'], '删除旧的域名环境')
    execute_command(['devil', 'www', 'add', f'{host}', 'python', python_path], '新建Servisor域名...')
    target_dir = f'/home/{username}/domains/{host}/public_python'
    # 递归复制整个目录
    try:
        with open('servisor/config.py', 'a', encoding='utf-8') as f:
            client_id = input('请输入client_id（Access -> Application -> Add an Application -> SaaS -> OIDC）\n')
            client_secret = input('请输入client_secret（Access -> Application -> Add an Application -> SaaS -> OIDC）\n')
            endpoint = input(
                'endpoint（Access -> Application -> Application URL -> 只保留协议+域名的部分，路径不需要例如：https://xxxxx.cloudflareaccess.com）\n')
            f.write(f"client_id = '{client_id}'\n")
            f.write(f"client_secret = '{client_secret}'\n")
            f.write(f"endpoint = '{endpoint}'\n")
        shutil.copytree(f'{os.getcwd()}/servisor/', target_dir, dirs_exist_ok=True)
        print(f"目录 {os.getcwd()}/servisor 已成功复制到 {target_dir}")
    except FileExistsError:
        print(f"目标目录 {target_dir} 已经存在。")
    except Exception as e:
        print(f"发生错误: {e}")
    subprocess.run(['rm', '-rf', f'/home/{username}/domains/{host}/public_python/public/'],
                   capture_output=True,
                   text=True)
    execute_command([python_path, '-m', 'pip', 'install', '-r', f'{target_dir}/requirements.txt'],
                    '安装Supervisor所需依赖')
    subprocess.run(['mkdir', '-p', f'{servisor_path}/etc'], capture_output=True, text=True)
    subprocess.run(['mkdir', '-p', f'{servisor_path}/run'], capture_output=True, text=True)
    subprocess.run(['mkdir', '-p', f'{servisor_path}/log/supervisor'], capture_output=True, text=True)
    subprocess.run(['mkdir', '-p', f'{servisor_path}/supervisor.d'], capture_output=True, text=True)
    with open(f'{servisor_path}/etc/supervisord.conf', 'w', encoding='utf-8') as f:
        f.write(f"""; supervisor config file
[unix_http_server]
; (the path to the socket file)
file  = {servisor_path}/run/supervisor.sock
; sockef file mode (default 0700)
chmod = 0700

[supervisord]
; (main log file;default $CWD/supervisord.log)
logfile     = {servisor_path}/log/supervisord.log
; (supervisord pidfile;default supervisord.pid)
pidfile     = {servisor_path}/run/supervisord.pid
; ('AUTO' child log dir, default $TEMP)
childlogdir = {servisor_path}/log/supervisor

; the below section must remain in the config file for RPC
; (supervisorctl/web interface) to work, additional interfaces may be
; added by defining them in separate rpcinterface: sections
[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
; use a unix:// URL  for a unix socket
serverurl = unix://{servisor_path}/run/supervisor.sock

; The [include] section can just contain the "files" setting.  This
; setting can list multiple files (separated by whitespace or
; newlines).  It can also contain wildcards.  The filenames are
; interpreted as relative to this file.  Included files *cannot*
; include files themselves.
[include]
files  = {servisor_path}/supervisor.d/*.ini
""")
    execute_command(['devil', 'www', 'restart', f'{host}'], '启动守护进程')
    print(f"请前往https://{host}，登陆后查看守护进程运行状态")
    print("Servisor安装完成")
    shutil.rmtree('servisor')
elif answer == 'n' or answer == 'no':
    print(f"你取消了，占用{host}。")
else:
    print("无效的输入，请输入 Y 或 n。")
