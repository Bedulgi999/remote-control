from flask import Flask, render_template, request, redirect, url_for
import datetime, platform, socket, psutil

app = Flask(__name__)

LOG_FILE = "logs.txt"

def write_log(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {message}\n")

def get_system_info():
    info = {}
    info["OS"] = f"{platform.system()} {platform.release()} ({platform.version()})"
    info["CPU"] = platform.processor()
    info["Machine"] = platform.machine()
    info["Hostname"] = socket.gethostname()
    info["IP"] = socket.gethostbyname(socket.gethostname())
    info["RAM"] = f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB"
    info["Disk"] = f"{round(psutil.disk_usage('/').total / (1024**3), 2)} GB"
    return info

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run_program():
    # 여기서는 '컴퓨터 정보 조회' 기능 실행
    sys_info = get_system_info()
    write_log("=== 컴퓨터 정보 조회 ===")
    for k, v in sys_info.items():
        write_log(f"{k}: {v}")
    return redirect(url_for("log_page"))

@app.route("/log")
def log_page():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = f.readlines()
    except FileNotFoundError:
        logs = ["아직 로그가 없습니다."]
    return render_template("log_page.html", logs=logs)

if __name__ == "__main__":
    app.run(debug=True)
