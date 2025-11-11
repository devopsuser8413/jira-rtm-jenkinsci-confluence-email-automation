import os, smtplib
from email.message import EmailMessage

report_path = "report/rtm_execution_report.html"
sender = os.getenv("REPORT_FROM")
recipients = os.getenv("REPORT_TO").split(",")
smtp_user = os.getenv("SMTP_USER")
smtp_pass = os.getenv("SMTP_PASS")

msg = EmailMessage()
msg["Subject"] = "RTM Test Execution Report"
msg["From"] = sender
msg["To"] = ", ".join(recipients)
msg.set_content("Please find attached the latest RTM Execution Report.")
with open(report_path, "rb") as f:
    msg.add_attachment(f.read(), maintype="text", subtype="html", filename=os.path.basename(report_path))

with smtplib.SMTP("smtp.office365.com", 587) as s:
    s.starttls()
    s.login(smtp_user, smtp_pass)
    s.send_message(msg)
    print("✅ Email sent successfully.")
