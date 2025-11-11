import os
import sys
import requests
from requests.auth import HTTPBasicAuth

# -----------------------------
# Usage / Args
# -----------------------------
if len(sys.argv) < 6:
    print("Usage: fetch_saved_rtm_report.py <jira_base> <jira_user> <jira_token> <project_key> <report_id>")
    sys.exit(1)

jira_base, jira_user, jira_token, project_key, report_id = sys.argv[1:6]

auth = HTTPBasicAuth(jira_user, jira_token)

# -----------------------------
# Headers for RTM Cloud Heroku endpoint
# -----------------------------
headers = {
    "Accept": "application/octet-stream",   # required per 406 response
    "User-Agent": "JenkinsRTMClient/1.0"
}

# -----------------------------
# Output setup
# -----------------------------
report_dir = "report"
os.makedirs(report_dir, exist_ok=True)
pdf_path = os.path.join(report_dir, f"{project_key}_{report_id}_report.pdf")

download_url = f"https://rtm-cloud.herokuapp.com/file-download?reportId={report_id}&format=pdf"

print(f"[INFO] Starting RTM Saved Report Fetch for project: {project_key}")
print(f"[INFO] Report ID: {report_id}")
print(f"[INFO] Download URL: {download_url}")

try:
    # -----------------------------
    # Request RTM Cloud file
    # -----------------------------
    response = requests.get(download_url, headers=headers, auth=auth, stream=True)
    status = response.status_code

    if status == 200:
        # Write file in binary chunks
        with open(pdf_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"[SUCCESS] Report downloaded successfully: {pdf_path}")
    else:
        print(f"[ERROR] Failed to download report. HTTP {status}")
        print(f"[DETAILS] {response.text}")
        sys.exit(1)

except requests.exceptions.RequestException as e:
    print(f"[EXCEPTION] Network error: {e}")
    sys.exit(1)

except Exception as e:
    print(f"[EXCEPTION] Unexpected error: {e}")
    sys.exit(1)
