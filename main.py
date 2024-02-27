from netmiko import ConnectHandler
from netmiko import NetmikoAuthenticationException, NetmikoTimeoutException
import tkinter as tk
from tkinter import messagebox, simpledialog
import sys, os, re, csv, logging, configparser, datetime, chardet

# error.logのフォーマット設定
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# textから読む形式になっている ←やってみた
# csvとかでやれたほうが対象が多いときに楽そうだからcsvから対象を読み込むよう改修する
# グローバル変数としてユーザ名とパスワードを保持 defの中でreturnに入れてたらその前のdestroyで全てdestroyされたからいっそグローバルにいれておく
username = ""
password = ""

# 実行ファイルのディレクトリパスを取得
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 設定ファイルのファイルパス
CONFIG_FILE = os.path.join(BASE_DIR, "config.ini")

# エラーログファイルのパス
ERROR_LOG_FILE = os.path.join(BASE_DIR, "error_log.txt")


# ファイルパスを設定ファイルから読み取る関数
def read_file_paths():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    host_list_file = os.path.join(BASE_DIR, config.get("FilePaths", "host_list_file"))
    target_host_file = os.path.join(BASE_DIR, config.get("FilePaths", "target_host_file"))
    command_list_file = os.path.join(BASE_DIR, config.get("FilePaths", "command_list_file"))
    return host_list_file, target_host_file, command_list_file


# フォームの作成と送信ボタンのクリック時の処理
def get_credentials():
    try:
        def submit_form():
            # グローバル変数にユーザ名とパスワードを設定
            global username
            global password
            username = username_entry.get()
            password = password_entry.get()
            root.destroy()  # フォームを閉じる

        def on_closing():
            log_error("ユーザ操作によりログインフォームが閉じられました。プログラムを終了します。")
            messagebox.showerror("エラー", "ユーザ操作によりログインフォームが閉じられました。プログラムを終了します。")
            sys.exit()

        root = tk.Tk()
        root.title("Login Form")
        root.protocol("WM_DELETE_WINDOW", on_closing)

        # ユーザ名のラベルと入力フィールド
        username_label = tk.Label(root, text="Username:")
        username_label.grid(row=0, column=0, padx=10, pady=5)
        username_entry = tk.Entry(root)
        username_entry.grid(row=0, column=1, padx=10, pady=5)

        # パスワードのラベルと入力フィールド
        password_label = tk.Label(root, text="Password:")
        password_label.grid(row=1, column=0, padx=10, pady=5)
        password_entry = tk.Entry(root, show="*")
        password_entry.grid(row=1, column=1, padx=10, pady=5)

        # 送信ボタン
        submit_button = tk.Button(root, text="Submit", command=submit_form)
        submit_button.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

        # tkinterウィンドウのメインループ
        root.mainloop()
    except Exception as e:
        log_error(f"ログイン情報を取得できませんでした: {str(e)}")
        sys.exit()


def detect_encoding(filename):
    with open(filename, "rb") as f:
        result = chardet.detect(f.read())
    return result["encoding"]


# コマンドリストを読み込む
def read_command_list(filename):
    try:
        with open(filename, "r") as f:
            return [line.strip() for line in f]
    except Exception as e:
        error_msg = f"コマンドリストを読み込めませんでした。 {filename}: {str(e)}"
        log_error(error_msg)
        sys.exit()


def login_and_execute_commands(host_name, username, password, command_list):
    device = {
        "device_type": 'juniper',
        'host': host_name,
        'username': username,
        'password': password,
        'session_log': 'netmiko_session_log',
        }

    # 各機器ごとのフォルダを作成する
    device_log_folder = os.path.join(BASE_DIR, "device_logs", host_name)
    os.makedirs(device_log_folder, exist_ok=True)

    # 機器接続
    print(f"Trying connect to {host_name}....")
    try:
        connection = ConnectHandler(**device)
        print(f"Successfully connected to {host_name}.")
    except NetmikoTimeoutException as e:
        error_msg = f"Failed to connect to {host_name}. Error {str(e)}"
        print(f"Failed to connect to {host_name}. Error: Timeout")
        log_error(error_msg)
        user_input = messagebox.askquestion("Connection Failed", f"{host_name} への接続がタイムアウトしました。 \n このまま次のホストへ接続を開始しますか？")
        if user_input == "no":
            messagebox.showerror("中断", "処理を中止し、プログラムを終了します。")
            sys.exit()
        return
    except NetmikoAuthenticationException as e:
        user_input = messagebox.askquestion("認証エラー", f"認証エラーが発生しました。 \n {host_name} と {username}が正しいことを確認してください。 \n パスワードを再入力して再実行しますか？")
        if user_input == "yes":
            new_password = simpledialog.askstring("Password Input", "パスワードを入力してください")
            if new_password:
                device["password"] = new_password
                try:
                    # 新しいパスワードを使用して再接続を試みる
                    connection = ConnectHandler(**device)
                    print(f"Successfully connected to {host_name}.")
                except NetmikoAuthenticationException:
                    error_msg = f"Failed to connect to {host_name}. Error {str(e)}"
                    print(f"Failed to connect to {host_name}. Error: Authentication Error")
                    log_error(error_msg)
                    messagebox.showerror('認証エラー', '認証に失敗しました。 プログラムを終了します。')
                    sys.exit()
    except Exception as e:
        error_msg = f"Failed to connect to {host_name}. Error {str(e)}"
        print(error_msg)
        log_error(error_msg)
        user_input = messagebox.askquestion("Connection Failed", f"{host_name} への接続に失敗しました。 \n このまま次のホストへ接続を開始しますか？")
        if user_input == "no":
            messagebox.showerror("中断", "処理を中止し、プログラムを終了します。")
            sys.exit()
        return
    outputs = []
    print(host_name)
    for command in command_list:
        command_file = re.sub(r'\|.*$', '', command)
        print("retrieving " + str(command_file) + "data. please wait...")
        try:
            output = connection.send_command(command, read_timeout=300)
        except Exception as e:
            error_msg = f"{host_name} 上で {command} の実行に失敗しました。Error: {str(e)}"
            print(error_msg)
            log_error(error_msg)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        command_file = re.sub(r'\|.*$', '', command)  # パイプが入っているとファイル保存時にエラーになるのでパイプ以降を削除
        logfile = f"{host_name}_{timestamp}_{command_file}.txt"
        logfile_path = os.path.join(device_log_folder, logfile)
        with open(logfile_path, 'w') as f:
            f.write(output + "\n\n")


# 接続対象のcsvを読み込む
def read_csv(filename):
    # ファイルのエンコーディングを自動的に判別
    try:
        with open(filename, 'rb') as f:
            rawdata = f.read()
            result = chardet.detect(rawdata)
            encoding = result['encoding']
    except FileNotFoundError:
        messagebox.showerror("エラー", f"{filename}が見つかりません")
        log_error(f"{filename}が見つかりません")
        sys.exit()
    except Exception as e:
        messagebox.showerror("エラー", f"定義されていないエラーが発生しました。{str(e)}")
        log_error(f"定義されていないエラーが発生しました。{str(e)}")
        sys.exit()

    # CSVファイルを読み取り、ホスト名をリストに格納
    hostnames = []
    try:
        with open(filename, 'r', encoding=encoding) as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                for item in row:
                    item = item.strip()
                    if item:
                        if '-' in item:  # ハイフンが含まれている場合は処理を行う
                            parts = item.split('-')
                            if len(parts) == 3: # ハイフンが2個含まれている場合
                                hostname = f"{parts[2]}.{parts[0]}-{parts[1]}.bb.jp.com.bb.com"
                            elif len(parts) == 2: # ハイフンが1個含まれている場合
                                hostname = f"{parts[1]}.{parts[0]}.bb.jp.com.bb.com"
                            else:
                                messagebox.showerror("エラー", f"不正な形式のホストネームが入力されています。: {item}")
                                log_error(f"不正な形式のホストネームが入力されています。: {item}")
                                sys.exit()
                            hostnames.append(hostname)
                        elif re.match(r'^(\d{1,3}\.){3}\d{1,3}$', item):  # IPv4アドレスの場合のみ追加
                            hostnames.append(item)
    except FileNotFoundError:
        messagebox.showerror("エラー", f"{filename}が見つかりません。")
        log_error(f"{filename}が見つかりません。")
        sys.exit()
    except Exception as e:
        messagebox.showerror("エラー", f"定義されていないエラーが発生しました。{str(e)}")
        log_error(f"定義されていないエラーが発生しました。{str(e)}")
        sys.exit()

    return hostnames


def log_error(error_message):
    with open(ERROR_LOG_FILE, 'a+') as error_log:  # 追記モードでファイルを開く存在しない場合は作成
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_log.write(f"{timestamp}: {error_message}\n")
        print(f"Error occurred: {error_message}")  # エラーメッセージを出力する


def main():
    # ユーザ名とパスワードを取得
    get_credentials()
    host_list_file, target_host_file, command_list_file = read_file_paths()
    # filename = r"./host_list.txt"
    filename = host_list_file
    # target_host_file = r"./target_host.csv"
    file_encoding = detect_encoding(filename)
    # command_list_file = r"./command_list.txt"
    command_list = read_command_list(command_list_file)
    host_names = read_csv(target_host_file)
    for host_name in host_names:
        login_and_execute_commands(host_name, username, password, command_list)


if __name__ == "__main__":
    ERROR_LOG_FILE = os.path.join(BASE_DIR, "error.log")
    if not os.path.exists(ERROR_LOG_FILE):
        with open(ERROR_LOG_FILE, 'w') as f:  # ファイルが存在しない場合は新規作成
            pass
    main()
