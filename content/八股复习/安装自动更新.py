#!/usr/bin/env python3
"""安装或卸载当前用户的 macOS 每分钟更新任务；无需管理员权限。"""
import argparse
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys

base = Path(__file__).resolve().parent
label = 'com.eason.java-review-daily'
agent = Path.home() / 'Library/LaunchAgents' / (label + '.plist')
domain = 'gui/' + str(os.getuid())
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--uninstall', action='store_true')
args = parser.parse_args()
def set_paused(paused):
    config_path = base / '配置.json'
    config = json.loads(config_path.read_text(encoding='utf-8'))
    config['paused'] = paused
    temp = config_path.with_name(config_path.name + '.tmp')
    temp.write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(config_path)

if args.uninstall:
    set_paused(True)
    subprocess.run(['launchctl', 'bootout', domain + '/' + label], check=False)
    agent.unlink(missing_ok=True)
    print('已停止自动更新；复习内容和进度保留。')
else:
    data = {
        'Label': label,
        'ProgramArguments': [sys.executable, str(base / '更新复习.py')],
        'WorkingDirectory': str(base),
        'RunAtLoad': True,
        'StartInterval': 60,
        'ProcessType': 'Background',
        'StandardOutPath': str(base / '自动更新.log'),
        'StandardErrorPath': str(base / '自动更新错误.log'),
    }
    agent.parent.mkdir(parents=True, exist_ok=True)
    if agent.exists() and agent.read_bytes() != plistlib.dumps(data):
        raise SystemExit('存在不同配置的同名任务，保留原配置：' + str(agent))
    agent.write_bytes(plistlib.dumps(data))
    status = subprocess.run(['launchctl', 'print', domain + '/' + label], capture_output=True)
    if status.returncode:
        subprocess.run(['launchctl', 'bootstrap', domain, str(agent)], check=True)
    set_paused(False)
    subprocess.run(['launchctl', 'kickstart', domain + '/' + label], check=True)
    print('已启用每分钟更新：' + str(agent))
