import sys
import os
import requests
from requests.auth import HTTPBasicAuth

# Ensure UTF-8 encoding (safety net)
sys.stdout.reconfigure(encoding='utf-8')

if len(sys.argv) < 6:
    print("Usage: fetch_saved_rtm_report.py <jira_base> <jira_user> <jira_token> <project_key> <report_name>")
    sys.exit(1)

jira_base, jira_user, jira_token, project_key, report_name = sys.argv[1:6]

auth = HTTPBasicAuth(jira_user, jira_token)
headers = {"Accept": "application/json"}

report_dir = "report"
os.makedirs(report_dir, exist_ok=True)

# --- Replace emojis with plain text ---
print(f"[INFO] Searching for Saved RTM Reports in project {project_key}...")

possible_paths = [
    f"{jira_base}/atm-cloud/rest/api/latest/reports/saved?projectKey={project_key}",
    f"{jira_base}/rest/atm/1.0/reports/saved?projectKey={project_key}",
    f"{jira_base}/jira/apps/64e045b8-e29a-40e5-bd2e-0cfdf4e8d4bb/7a2911d3-7421-4d99-89f7-762313d01b40/reports/saved?projectKey={project_key}",
    f"{jira_base}/apps/rtm-api/rest/api/latest/reports/saved?projectKey={project_key}",
]

report_list = None
selected_url = None

for url in possible_paths:
    print(f"[TRY]  {url}")
    try:
        resp = requests.get(url, auth=auth, headers=headers)
        if resp.status_code == 200:
            report_list = resp.json()
            selected_url = url
            print(f"[OK]   Success using endpoint: {url}")
            break
        else:
            print(f"[FAIL] GET {url} -> {resp.status_code}")
    except Exception as e:
        print(f"[ERROR] {e}")

if not report_list:
    print("[ERROR] Could not retrieve Saved Reports from any known endpoint.")
    sys.exit(1)
