import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

DART_API_KEY = os.getenv('DART_API_KEY')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
LOG_FILE = "sent_log.txt"

def load_sent():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, 'r') as f:
        return set(line.strip() for line in f)

def save_sent(rcp_no):
    with open(LOG_FILE, 'a') as f:
        f.write(f"{rcp_no}\n")

def get_dart_reports():
    url = f'https://opendart.fss.or.kr/api/list.json?crtfc_key={DART_API_KEY}&bgn_de=20250101&page_no=1&page_count=100&corp_cls=Y'
    response = requests.get(url)
    if response.status_code != 200:
        print(f"API 에러: {response.status_code}")
        return []
    return response.json().get('list', [])

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    res = requests.post(url, data=data)
    if res.status_code != 200:
        print(f"텔레그램 전송 실패: {res.text}")

def main_loop():
    sent_reports = load_sent()
    print("🔍 공시 모니터링을 시작합니다...")
    while True:
        try:
            reports = get_dart_reports()
            for report in reports:
                if "단일판매" in report['report_nm'] and report['rcept_no'] not in sent_reports:
                    link = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={report['rcept_no']}"
                    msg = (
                        f"📢 <b>{report['corp_name']}</b> 계약 공시\n"
                        f"{report['report_nm']}\n"
                        f"📄 <a href='{link}'>공시 바로가기</a>\n"
                        f"📅 공시일자: {report['rcept_dt']}"
                    )
                    send_telegram_message(msg)
                    sent_reports.add(report['rcept_no'])
                    save_sent(report['rcept_no'])

        except Exception as e:
            print(f"오류 발생: {e}")
        time.sleep(300)

if __name__ == "__main__":
    main_loop()