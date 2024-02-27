from netmiko import ConnectHandler
import datetime
import chardet
import re

# textから読む形式になっている
# csvとかでやれたほうが対象が多いときに楽そうだからcsvから対象を読み込むよう改修する
def detect_encoding(filename):
    with open(filename, "rb") as f:
        result = chardet.detect(f.read())
    return result["encoding"]


def read_command_list(filename):
    with open(filename, "r") as f:
        return [line.strip() for line in f]


def login_and_execute_commands(host_name, ip_address, username, password, command_list):
    device = {
        "device_type": 'juniper',
        'ip': ip_address,
        'username': "root",
        'password': "root",
        'session_log': 'netmiko_session_log',
        }
    print(f"connect to {host_name}....")
    connection = ConnectHandler(**device)
    print(f"Successfully connected to {host_name}.")
    outputs = []
    for command in command_list:
        command_file = re.sub(r'\|.*$', '', command)
        print("retrieving " + str(command_file) + "data. please wait...")
        output = connection.send_command(command, read_timeout=300)
        # outputs.append(output) #出力をすべてマージするときはこのコメントアウトを外していい感じにする
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        command_file = re.sub(r'\|.*$', '', command)
        logfile = f"{host_name}_{ip_address}_{timestamp}_{command_file}.txt"
        with open(logfile, 'w') as f:
            # for output in outputs: #出力をすべてマージするときはこのコメントアウトを外していい感じにする
            f.write(output + "\n\n")


def main():
    filename = r"C:\\temp\host_list.txt"
    file_encoding = detect_encoding(filename)
    command_list_file = r"C:\\temp\command_list.txt"
    command_list = read_command_list(command_list_file)
    with open(filename, "r", encoding=file_encoding) as txtfile:
        for line in txtfile:
            row = line.strip().split(',')
            if len(row) != 4:
                print(f"Invaild row in the TXT file: {row}")
                continue
            host_name, ip_address, username, password = row
            login_and_execute_commands(host_name, ip_address, username, password, command_list)


if __name__ == "__main__":
    main()
