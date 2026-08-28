import json, os, requests, smtplib
from email.mime.text import MIMEText

def send_telegram(message):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": message[:4000]})

def send_email(subject, body):
    addr = os.environ["GMAIL_ADDRESS"]
    pwd = os.environ["GMAIL_APP_PASSWORD"]
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = addr
    msg["To"] = addr
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(addr, pwd)
        server.send_message(msg)

def main():
    if not os.path.exists("data/latest_findings.json"):
        return
    findings = json.load(open("data/latest_findings.json"))
    if not findings:
        return

    text = "🔔 New Psychology Job Alerts\n\n"
    for f in findings:
        text += f"📍 {f['source']} ({f['district']})\n{f['url']}\n"
        for m in f["matches"]:
            text += f"- {m}\n"
        text += "\n"

    send_telegram(text)
    send_email("New Psychology Job Alerts", text)
    os.remove("data/latest_findings.json")

if __name__ == "__main__":
    main()
