import threading, time, queue
import tkinter as tk
from tkinter import messagebox
import requests, platform, psutil, socket, datetime
try:
    import speedtest
    SPEEDTEST_OK = True
except Exception:
    SPEEDTEST_OK = False

# ---- 설정 ----
SERVER = "https://mydomain.com"  # 서버 도메인으로 변경
POLL_INTERVAL_SEC = 5            # 명령 폴링 주기

# ---- 유틸 ----
def send_log(text):
    try:
        requests.post(f"{SERVER}/upload_log", data={"log": text}, timeout=5)
    except Exception:
        pass

def get_system_info():
    return {
        "OS": f"{platform.system()} {platform.release()}",
        "CPU": platform.processor(),
        "RAM": f"{round(psutil.virtual_memory().total/(1024**3),2)} GB",
        "Disk": f"{round(psutil.disk_usage('/').total/(1024**3),2)} GB",
        "IP": socket.gethostbyname(socket.gethostname())
    }

def get_status():
    return {
        "CPU 사용률": f"{psutil.cpu_percent()}%",
        "RAM 사용률": f"{psutil.virtual_memory().percent}%"
    }

def get_uptime():
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.datetime.now() - boot_time
    return str(uptime).split(".")[0]

def run_speedtest():
    if not SPEEDTEST_OK:
        return {"error": "speedtest 모듈이 없어 속도측정을 건너뜁니다."}
    st = speedtest.Speedtest()
    # 서버 선택 및 측정 (차단 방지용 기본 호출)
    st.get_best_server()
    d = st.download()
    u = st.upload()
    return {"Download": f"{round(d/1_000_000,2)} Mbps", "Upload": f"{round(u/1_000_000,2)} Mbps"}

def run_command(cmd):
    cmd = cmd.strip()
    if cmd == "!정보":
        return str(get_system_info())
    elif cmd == "!상태":
        return str(get_status())
    elif cmd == "!가동시간":
        return f"가동시간: {get_uptime()}"
    elif cmd == "!속도측정":
        return str(run_speedtest())
    elif cmd.startswith("!알림창"):
        try:
            parts = cmd.split("|", 2)
            # 예: !알림창|제목|내용
            title = parts[1] if len(parts) > 1 else "알림"
            content = parts[2] if len(parts) > 2 else ""
            messagebox.showinfo(title, content)
            return f"알림창 표시: {title} - {content}"
        except Exception:
            return "알림창 실행 오류"
    else:
        return f"알 수 없는 명령: {cmd}"

# ---- 워커 스레드 ----
class Worker(threading.Thread):
    def __init__(self, evt_stop, ui_queue):
        super().__init__(daemon=True)
        self.evt_stop = evt_stop
        self.ui_queue = ui_queue

    def run(self):
        send_log("[클라이언트] 연결 시작")
        while not self.evt_stop.is_set():
            try:
                r = requests.get(f"{SERVER}/get_command", timeout=5)
                cmd = r.text.strip()
                if cmd:
                    result = run_command(cmd)
                    send_log(result)
                    self.ui_queue.put(f"명령 실행: {cmd}\n결과: {result}")
            except Exception as e:
                self.ui_queue.put(f"서버 통신 오류: {e}")
            finally:
                for _ in range(POLL_INTERVAL_SEC * 10):  # 0.1s * n = POLL_INTERVAL_SEC
                    if self.evt_stop.is_set():
                        break
                    time.sleep(0.1)
        send_log("[클라이언트] 연결 종료")

# ---- GUI ----
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("원격 관리 클라이언트 (사용자 실행형)")
        self.geometry("520x360")
        self.resizable(False, False)

        tk.Label(self, text="서버 주소").pack(anchor="w", padx=12, pady=(12,0))
        self.entry_server = tk.Entry(self)
        self.entry_server.insert(0, SERVER)
        self.entry_server.pack(fill="x", padx=12)

        self.btn_frame = tk.Frame(self)
        self.btn_frame.pack(fill="x", pady=10, padx=12)
        self.btn_start = tk.Button(self.btn_frame, text="연결 시작", command=self.start)
        self.btn_stop = tk.Button(self.btn_frame, text="연결 중지", command=self.stop, state="disabled")
        self.btn_start.pack(side="left")
        self.btn_stop.pack(side="left", padx=8)

        self.text = tk.Text(self, height=14)
        self.text.pack(fill="both", expand=True, padx=12, pady=(0,12))

        self.evt_stop = threading.Event()
        self.worker = None
        self.ui_queue = queue.Queue()
        self.after(200, self.drain_queue)

        # 시작 시 사용자 동의 안내
        self.after(100, self.show_consent)

    def log(self, s):
        self.text.insert("end", s + "\n")
        self.text.see("end")

    def drain_queue(self):
        try:
            while True:
                msg = self.ui_queue.get_nowait()
                self.log(msg)
        except queue.Empty:
            pass
        self.after(200, self.drain_queue)

    def show_consent(self):
        ok = messagebox.askokcancel(
            "동의 필요",
            "이 프로그램은 서버로부터 명령(!정보, !상태, !가동시간, !속도측정, !알림창)을 받아 실행하고, 결과를 서버 로그로 전송합니다.\n계속하시겠습니까?"
        )
        if not ok:
            self.destroy()

    def start(self):
        addr = self.entry_server.get().strip()
        if not addr.startswith("http"):
            messagebox.showerror("오류", "서버 주소는 http/https로 시작해야 합니다.")
            return
        global SERVER
        SERVER = addr
        if self.worker and self.worker.is_alive():
            messagebox.showinfo("안내", "이미 연결 중입니다.")
            return
        self.evt_stop.clear()
        self.worker = Worker(self.evt_stop, self.ui_queue)
        self.worker.start()
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.log(f"연결 시도: {SERVER}")

    def stop(self):
        self.evt_stop.set()
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.log("연결 중지 요청")

    def on_close(self):
        self.stop()
        self.after(300, self.destroy)

def main():
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()

if __name__ == "__main__":
    main()
