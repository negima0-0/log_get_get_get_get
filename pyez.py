from jnpr.junos import Device
from jnpr.junos.factory import loadyaml
from jnpr.junos.utils.start_shell import StartShell
import re

# デバイスの接続情報を設定
hostname = 'YOUR_DEVICE_IP'
username = 'YOUR_USERNAME'
password = 'YOUR_PASSWORD'

# デバイスに接続
dev = Device(host=hostname, user=username, password=password)
dev.open()

# Start shellを開始
ss = StartShell(dev)
ss.open()

# messagesログとmessages.0.gz ~ messages.9.gzを取得するためのコマンドを実行
output = ""
for i in range(10):
    cmd = f'show log messages.{i}.gz'
    output += ss.run(cmd)
output += ss.run('show log messages')

# ログをファイルに保存
with open('all_messages_logs.txt', 'w') as f:
    f.write(output)

# 接続を閉じる
ss.close()
dev.close()
