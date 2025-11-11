import os
import sys
import requests
from requests.auth import HTTPBasicAuth

if len(sys.argv) < 6:
    print("Usage: fetch_saved_rtm_report.py <jira_base> <jira_user> <jira_token> <project_key> <report_name>")
    sys.exit(1)

jira_base, jira_user, jira_token, project_key, report_name = sys.argv[1:6]
auth = HTTPBasicAuth(jira_user, jira_token)

headers_json = {"Accept": "application/json", "User-Agent": "JenkinsRTMClient/1.0"}
headers_file = {"Accept": "application/octet-stream", "User-Agent": "JenkinsRTMClient/1.0"}

report_dir = "report"
os.makedirs(report_dir, exist_ok=True)
pdf_path = os.path.join(report_dir, f"{project_key}_{report_name}_report.pdf")

# STEP 1 – Get saved reports list from RTM Cloud
saved_url = f"https://rtm-cloud.herokuapp.com/reports/saved?projectKey={project_key}"
print(f"[INFO] Querying saved reports: {saved_url}")

try:
    r = requests.get(saved_url, headers=headers_json, auth=auth)
    if r.status_code != 200:
        print(f"[ERROR] Failed to fetch saved reports. HTTP {r.status_code}")
        print(r.text)
        sys.exit(1)

    data = r.json()
    numeric_id = None
    for item in data:
        if report_name.lower() in item.get("name", "").lower():
            numeric_id = item.get("id")
            print(f"[SUCCESS] Found '{report_name}' → ID {numeric_id}")
            break

    if not numeric_id:
        print("[ERROR] Report name not found in saved reports list.")
        sys.exit(1)

except Exception as e:
    print(f"[EXCEPTION] Error fetching saved reports: {e}")
    sys.exit(1)

# STEP 2 – Download report by numeric id
download_url = f"https://rtm-cloud.herokuapp.com/file-download?id={numeric_id}&format=pdf"
print(f"[INFO] Downloading report from: {download_url}")

try:
    r = requests.get(download_url, headers=headers_file, stream=True)
    if r.status_code == 200:
        with open(pdf_path, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)
        print(f"[SUCCESS] Report saved at: {pdf_path}")
    else:
        print(f"[ERROR] Download failed. HTTP {r.status_code}")
        print(r.text)
        sys.exit(1)

except Exception as e:
    print(f"[EXCEPTION] Error downloading report: {e}")
    sys.exit(1)
