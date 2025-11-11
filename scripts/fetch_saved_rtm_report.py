import os
import sys
import requests
from requests.auth import HTTPBasicAuth

# -----------------------------
# Usage: fetch_saved_rtm_report.py <jira_base> <jira_user> <jira_token> <project_key> <report_id>
# -----------------------------
if len(sys.argv) < 6:
    print("Usage: fetch_saved_rtm_report.py <jira_base> <jira_user> <jira_token> <project_key> <report_id>")
    sys.exit(1)

jira_base, jira_user, jira_token, project_key, report_id = sys.argv[1:6]

auth = HTTPBasicAuth(jira_user, jira_token)
headers = {"Accept": "application/json"}
report_dir = "report"
os.makedirs(report_dir, exist_ok=True)

pdf_file = os.path.join(report_dir, f"rtm_saved_report_{report_id}.pdf")
html_file = os.path.join(report_dir, f"rtm_saved_report_{report_id}.html")

print(f"[INFO] Starting RTM Saved Report Fetch for project {project_key}")
print(f"[INFO] Report ID: {report_id}")

# -----------------------------
# Construct the file-download URL
# -----------------------------
file_download_url = f"https://rtm-cloud.herokuapp.com/file-download?reportId={report_id}&format=pdf"
print(f"[TRY] Accessing: {file_download_url}")

try:
    resp = requests.get(file_download_url, auth=auth, headers=headers, stream=True)
    if resp.status_code == 200 and "application/pdf" in resp.headers.get("Content-Type", ""):
        with open(pdf_file, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"[OK]  PDF Report downloaded successfully → {pdf_file}")
    else:
        print(f"[FAIL] Unable to download report: HTTP {resp.status_code}")
        print(resp.text[:300])
        sys.exit(1)
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)

# -----------------------------
# Optional: Convert PDF to HTML placeholder (for Confluence upload)
# -----------------------------
try:
    html_content = f"""
    <h2>RTM Test Execution Report</h2>
    <p>Project Key: {project_key}</p>
    <p>Report ID: {report_id}</p>
    <p>Generated from Jira RTM Cloud.</p>
    <p><b>Download PDF:</b> <a href='{file_download_url}' target='_blank'>Click here</a></p>
    """
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[OK]  HTML summary created → {html_file}")
except Exception as e:
    print(f"[WARN] Could not create HTML summary: {e}")

print("[DONE] RTM Saved Report processing completed successfully.")
