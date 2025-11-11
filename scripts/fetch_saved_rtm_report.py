import os
import sys
import requests
from requests.auth import HTTPBasicAuth

# ----------------------------
# Usage:
# python scripts/fetch_saved_rtm_report.py <jira_base> <jira_user> <jira_token> <project_key> <report_name>
# Example:
# python scripts/fetch_saved_rtm_report.py https://devopsuser8413-1761792468908.atlassian.net user@example.com <token> RD "Test Execution Summary"
# ----------------------------

if len(sys.argv) < 6:
    print("Usage: fetch_saved_rtm_report.py <jira_base> <jira_user> <jira_token> <project_key> <report_name>")
    sys.exit(1)

jira_base, jira_user, jira_token, project_key, report_name = sys.argv[1:6]

auth = HTTPBasicAuth(jira_user, jira_token)
headers = {"Accept": "application/json"}

report_dir = "report"
os.makedirs(report_dir, exist_ok=True)

# ----------------------------------------------------------------------
# STEP 1: Attempt to list all Saved Reports
# ----------------------------------------------------------------------
# 🔹 NOTE: For RTM Cloud, the actual API path may differ depending on tenant.
# 🔹 Try these automatically in sequence until one returns 200 OK.
# ----------------------------------------------------------------------

possible_paths = [
    f"{jira_base}/atm-cloud/rest/api/latest/reports/saved?projectKey={project_key}",
    f"{jira_base}/rest/atm/1.0/reports/saved?projectKey={project_key}",
    f"{jira_base}/jira/apps/64e045b8-e29a-40e5-bd2e-0cfdf4e8d4bb/7a2911d3-7421-4d99-89f7-762313d01b40/reports/saved?projectKey={project_key}",
    f"{jira_base}/apps/rtm-api/rest/api/latest/reports/saved?projectKey={project_key}",
]

report_list = None
selected_url = None

print(f"🔍 Searching for Saved RTM Reports in {project_key}...")

for url in possible_paths:
    try:
        print(f"➡️  Trying {url}")
        resp = requests.get(url, auth=auth, headers=headers)
        if resp.status_code == 200:
            report_list = resp.json()
            selected_url = url
            print(f"✅ Success using endpoint: {url}")
            break
        else:
            print(f"❌ GET {url} -> {resp.status_code} {resp.text[:150]}...")
    except Exception as e:
        print(f"⚠️  Error trying {url}: {e}")

if not report_list:
    print("❌ Could not retrieve Saved Reports from any known endpoint.")
    sys.exit(1)

# ----------------------------------------------------------------------
# STEP 2: Find matching Saved Report by name
# ----------------------------------------------------------------------

reports = report_list if isinstance(report_list, list) else report_list.get("values", [])
report_id = None

for rep in reports:
    if report_name.lower() in str(rep).lower():
        report_id = rep.get("id") or rep.get("key") or rep.get("uuid")
        print(f"✅ Found report '{report_name}' with ID: {report_id}")
        break

if not report_id:
    print(f"❌ Report named '{report_name}' not found in list.")
    sys.exit(1)

# ----------------------------------------------------------------------
# STEP 3: Try to export the Saved Report as PDF
# ----------------------------------------------------------------------

export_paths = [
    f"{jira_base}/atm-cloud/rest/api/latest/reports/{report_id}/export/pdf",
    f"{jira_base}/rest/atm/1.0/report/export/pdf/{report_id}",
    f"{jira_base}/apps/rtm-api/rest/api/latest/reports/{report_id}/export/pdf",
    f"{jira_base}/jira/apps/64e045b8-e29a-40e5-bd2e-0cfdf4e8d4bb/7a2911d3-7421-4d99-89f7-762313d01b40/reports/export/pdf/{report_id}",
]

pdf_file = os.path.join(report_dir, f"rtm_saved_report_{report_id}.pdf")

for pdf_url in export_paths:
    print(f"📥 Trying to download PDF from {pdf_url}")
    r = requests.get(pdf_url, auth=auth, headers=headers, stream=True)
    if r.status_code == 200 and r.headers.get("Content-Type", "").startswith("application/pdf"):
        with open(pdf_file, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Saved RTM PDF report at {pdf_file}")
        sys.exit(0)
    else:
        print(f"❌ Failed to fetch PDF ({r.status_code}): {r.text[:200]}")

print("❌ None of the PDF export endpoints worked. Please check browser Network tab to capture actual export URL.")
sys.exit(1)
