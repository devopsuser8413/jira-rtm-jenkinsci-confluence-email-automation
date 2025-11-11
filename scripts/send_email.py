import os
import sys
import smtplib
import ssl
from email.message import EmailMessage

# =======================================================
# 🧩 CLI Arguments from Jenkins
# =======================================================
if len(sys.argv) < 3:
    print("Usage: send_email.py <jira_issue_key> <environment>")
    sys.exit(1)

jira_issue_key = sys.argv[1]
environment = sys.argv[2]

# =======================================================
# 📦 Environment Variables (set in Jenkins)
# =======================================================
REPORT_HTML = "report/rtm_execution_report.html"
REPORT_PDF = "report/rtm_execution_report.pdf"

SENDER = os.getenv("REPORT_FROM")               # Gmail sender
RECIPIENTS = [r.strip() for r in os.getenv("REPORT_TO", "").split(",") if r.strip()]
SMTP_USER = os.getenv("SMTP_USER")              # Gmail username
SMTP_PASS = os.getenv("SMTP_PASS")              # Gmail App Password

CONFLUENCE_BASE = os.getenv("CONFLUENCE_BASE")
CONFLUENCE_SPACE = os.getenv("CONFLUENCE_SPACE")
CONFLUENCE_TITLE = os.getenv("CONFLUENCE_TITLE")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# =======================================================
# ✉️ Compose HTML Email
# =======================================================
msg = EmailMessage()
msg["Subject"] = f"RTM Test Execution Report: {jira_issue_key} ({environment})"
msg["From"] = SENDER
msg["To"] = ", ".join(RECIPIENTS)

confluence_link = f"{CONFLUENCE_BASE}/pages/viewpage.action?spaceKey={CONFLUENCE_SPACE}&title={CONFLUENCE_TITLE}"

html_body = f"""
<html>
  <body style="font-family: Arial, sans-serif;">
    <p>Hello Team,</p>
    <p>
      The <b>RTM Test Execution Report</b> for
      <b>{jira_issue_key}</b> in environment <b>{environment}</b>
      has been generated successfully.
    </p>
    <p>
      📘 View it on Confluence:
      <a href="{confluence_link}" target="_blank">{CONFLUENCE_TITLE}</a>
    </p>
    <p>The HTML and PDF reports are also attached for reference.</p>
    <br>
    <p>Regards,<br><b>Jenkins RTM Automation Bot 🤖</b></p>
  </body>
</html>
"""

msg.set_content("Please view the HTML version of this email for full details.")
msg.add_alternative(html_body, subtype="html")

# =======================================================
# 📎 Attach RTM Reports
# =======================================================
attachments = [REPORT_HTML, REPORT_PDF]
for path in attachments:
    if os.path.exists(path):
        with open(path, "rb") as f:
            maintype, subtype = ("text", "html") if path.endswith(".html") else ("application", "pdf")
            msg.add_attachment(
                f.read(),
                maintype=maintype,
                subtype=subtype,
                filename=os.path.basename(path),
            )
        print(f"📎 Attached: {path}")
    else:
        print(f"⚠️ Missing attachment: {path}")

# =======================================================
# 🚀 Send Email via Gmail SMTP
# =======================================================
print(f"📧 Sending report email for {jira_issue_key} ({environment})...")
context = ssl.create_default_context()

try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.set_debuglevel(1)
        server.starttls(context=context)
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
    print("✅ Email sent successfully to:", ", ".join(RECIPIENTS))

except smtplib.SMTPAuthenticationError:
    print("❌ Authentication failed. Ensure Gmail App Password is correct.")
except Exception as e:
    print(f"❌ Email sending failed: {e}")
