from netmiko import ConnectHandler

def connect_to_device_via_bastion(bastion_host, bastion_username, bastion_password, target_host, target_username, target_password):
    # 踏み台サーバに接続
    bastion_device = {
        "device_type": "linux",
        "host": bastion_host,
        "username": bastion_username,
        "password": bastion_password,
    }
    bastion_connection = ConnectHandler(**bastion_device)

    # 目的のネットワーク機器に接続
    target_device = {
        "device_type": "juniper",
        "host": target_host,
        "username": target_username,
        "password": target_password,
        "sock": bastion_connection,
    }
    target_connection = ConnectHandler(**target_device)

    return target_connection

# 踏み台サーバと目的のネットワーク機器の情報
bastion_host = "bastion.example.com"
bastion_username = "bastion_user"
bastion_password = "bastion_password"
target_host = "srx300.example.com"
target_username = "srx_user"
target_password = "srx_password"

# 踏み台を介して目的のネットワーク機器に接続
try:
    connection = connect_to_device_via_bastion(bastion_host, bastion_username, bastion_password, target_host, target_username, target_password)
    print("Successfully connected to target device via bastion.")
    # ここでコマンドを実行するなどの処理を行う
except Exception as e:
    print(f"Failed to connect: {str(e)}")
