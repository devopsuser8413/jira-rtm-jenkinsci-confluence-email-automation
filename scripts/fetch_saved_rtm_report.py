import os, sys, requests
from requests.auth import HTTPBasicAuth

if len(sys.argv) < 6:
    print("Usage: fetch_saved_rtm_report.py <jira_base> <jira_user> <jira_token> <project_key> <report_id>")
    sys.exit(1)

jira_base, jira_user, jira_token, project_key, report_id = sys.argv[1:6]

auth = HTTPBasicAuth(jira_user, jira_token)
headers = {
    # accept only binary data since RTM returns application/octet-stream
    "Accept": "application/octet-stream"
}

report_dir = "report"
os.makedirs(report_dir, exist_ok=True)
pdf_path = os.path.join(report_dir, f"{project_key}_{report_id}_report.pdf")

download_url = f"https://rtm-cloud.herokuapp.com/file-download?reportId={report_id}&format=pdf"

print(f"[INFO] Attempting RTM Saved Report download for {report_id}")
print(f"[TRY]  {download_url}")

try:
    r = requests.get(download_url, headers=headers, auth=auth, stream=True)
    if r.status_code == 200:
        with open(pdf_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Report downloaded successfully: {pdf_path}")
    else:
        print(f"❌ Failed to download: HTTP {r.status_code}")
        print(r.text)
        sys.exit(1)
except Exception as e:
    print(f"❌ Exception while fetching report: {e}")
    sys.exit(1)
