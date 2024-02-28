import threading  # マルチスレッド処理を利用するために追加

def parallel_login_and_execute_commands(host_names, username, password, command_list):
    threads = []
    total_hosts = len(host_names)
    processed_hosts = 0

    for host_name in host_names:
        thread = threading.Thread(target=login_and_execute_commands, args=(host_name, username, password, command_list, processed_hosts, total_hosts))
        threads.append(thread)
        thread.start()

    # すべてのスレッドの終了を待つ
    for thread in threads:
        thread.join()

def login_and_execute_commands(host_name, username, password, command_list, processed_hosts, total_hosts):
    # 処理の進捗状況を表示
    print(f"Processing host {processed_hosts}/{total_hosts}: {host_name}...")

    device_info = {
        "device_type": 'juniper',
        'host': host_name,
        'username': username,
        'password': password,
        'session_log': 'netmiko_session_log',
    }

    connection = establish_ssh_connection(device_info)
    
    # コマンドの実行
    for index, command in enumerate(command_list, start=1):
        print(f"Executing command {index}/{len(command_list)}: {command}...")
        try:
            output = connection.send_command(command, read_timeout=300)
            print(f"Command {index}/{len(command_list)}: {command} executed successfully.")
        except Exception as e:
            print(f"Failed to execute command {index}/{len(command_list)}: {command}. Error: {str(e)}")
    
    # 接続を閉じる
    connection.disconnect()

    # 処理の進捗状況を表示
    print(f"Host {processed_hosts}/{total_hosts}: {host_name} processed successfully.")

def main():
    # ユーザ名とパスワードを取得
    get_credentials()
    target_host_file, command_list_file = read_file_paths()
    command_list = read_command_list(command_list_file)
    host_names = read_csv(target_host_file)

    # 進行状況を表示するためのカウンター
    total_hosts = len(host_names)
    processed_hosts = 0

    parallel_login_and_execute_commands(host_names, username, password, command_list)

    messagebox.showinfo("処理完了", "処理が完了しました。プログラムを終了します。")
    sys.exit()

if __name__ == "__main__":
    ERROR_LOG_FILE = os.path.join(BASE_DIR, "error.log")
    if not os.path.exists(ERROR_LOG_FILE):
        with open(ERROR_LOG_FILE, 'w'):  # ファイルが存在しない場合は新規作成
            pass
    main()
