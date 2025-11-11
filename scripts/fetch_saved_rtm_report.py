import os
import sys
import requests
from requests.auth import HTTPBasicAuth

if len(sys.argv) < 6:
    print("Usage: fetch_saved_rtm_report.py <jira_base> <jira_user> <jira_token> <project_key> <report_name>")
    sys.exit(1)

jira_base, jira_user, jira_token, project_key, report_name = sys.argv[1:6]
auth = HTTPBasicAuth(jira_user, jira_token)

headers_json = {
    "Accept": "application/json",
    "User-Agent": "JenkinsRTMClient/1.0"
}
headers_file = {
    "Accept": "application/octet-stream",
    "User-Agent": "JenkinsRTMClient/1.0"
}

report_dir = "report"
os.makedirs(report_dir, exist_ok=True)
pdf_path = os.path.join(report_dir, f"{project_key}_{report_name}_report.pdf")

# Step 1: Fetch saved reports list
base_urls = [
    f"{jira_base}/rest/atm/1.0/reports/saved?projectKey={project_key}",
    f"{jira_base}/apps/rtm-api/rest/api/latest/reports/saved?projectKey={project_key}",
    f"{jira_base}/jira/apps/64e045b8-e29a-40e5-bd2e-0cfdf4e8d4bb/7a2911d3-7421-4d99-89f7-762313d01b40/reports/saved?projectKey={project_key}"
]

numeric_id = None
for url in base_urls:
    print(f"[INFO] Trying: {url}")
    try:
        r = requests.get(url, headers=headers_json, auth=auth)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                for report in data:
                    if report_name.lower() in report.get("name", "").lower():
                        numeric_id = report.get("id")
                        print(f"[SUCCESS] Found report '{report_name}' with ID {numeric_id}")
                        break
        else:
            print(f"[WARN] {url} returned HTTP {r.status_code}")
    except Exception as e:
        print(f"[ERROR] Could not access {url}: {e}")

    if numeric_id:
        break

if not numeric_id:
    print("[ERROR] Could not find saved report matching given name.")
    sys.exit(1)

# Step 2: Download report using numeric ID
download_url = f"https://rtm-cloud.herokuapp.com/file-download?id={numeric_id}&format=pdf"
print(f"[INFO] Downloading from: {download_url}")

try:
    r = requests.get(download_url, headers=headers_file, stream=True)
    if r.status_code == 200:
        with open(pdf_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"[SUCCESS] Report downloaded successfully: {pdf_path}")
    else:
        print(f"[ERROR] Failed to download report. HTTP {r.status_code}")
        print(f"[DETAILS] {r.text}")
        sys.exit(1)

except Exception as e:
    print(f"[EXCEPTION] Error downloading report: {e}")
    sys.exit(1)
