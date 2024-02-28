from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 最大同時処理数
MAX_CONCURRENT_TASKS = 5

# ロックオブジェクト
lock = threading.Lock()

def login_and_execute_commands_wrapper(host_name, username, password, command_list):
    with lock:
        print(f"Starting processing for host: {host_name}")
    login_and_execute_commands(host_name, username, password, command_list)
    with lock:
        print(f"Finished processing for host: {host_name}")

def main():
    # ユーザ名とパスワードを取得
    get_credentials()
    target_host_file, command_list_file = read_file_paths()
    command_list = read_command_list(command_list_file)
    host_names = read_csv(target_host_file)

    # 並列処理の開始
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_TASKS) as executor:
        futures = []
        for host_name in host_names:
            # 各ホストごとに並列処理を実行
            future = executor.submit(login_and_execute_commands_wrapper, host_name, username, password, command_list)
            futures.append(future)
        
        # 各タスクが完了するまで待機
        for future in as_completed(futures):
            pass

    messagebox.showinfo("処理完了", "処理が完了しました。プログラムを終了します。")
    sys.exit()

if __name__ == "__main__":
    ERROR_LOG_FILE = os.path.join(BASE_DIR, "error.log")
    if not os.path.exists(ERROR_LOG_FILE):
        with open(ERROR_LOG_FILE, 'w') as f:  # ファイルが存在しない場合は新規作成
            pass
    main()
