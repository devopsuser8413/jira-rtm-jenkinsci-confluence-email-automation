import os, requests
from requests.auth import HTTPBasicAuth

# -----------------------------
# Environment Variables
# -----------------------------
base = os.getenv("JIRA_BASE")  # e.g. https://devopsuser8413-1761792468908.atlassian.net
user = os.getenv("JIRA_USER")
token = os.getenv("JIRA_TOKEN")
issue_key = os.getenv("JIRA_ISSUE_KEY")

auth = HTTPBasicAuth(user, token)
headers = {"Accept": "application/json"}

print(f"🔍 Searching Saved RTM Reports for {issue_key}...")

# Step 1 - Fetch saved reports (RTM Cloud)
saved_url = f"{base}/gateway/api/atm/cloud/rest/api/latest/reports/saved"
resp = requests.get(saved_url, headers=headers, auth=auth)

if resp.status_code != 200:
    print(f"❌ Failed to fetch saved reports: {resp.status_code} {resp.text}")
    exit(1)

reports = resp.json()
if not reports:
    print("❌ No saved reports found in RTM.")
    exit(1)

report_id = None
for rpt in reports:
    if issue_key in str(rpt):
        report_id = rpt["id"]
        print(f"✅ Found report '{rpt['name']}' ({report_id}) for {issue_key}")
        break

if not report_id:
    print(f"❌ No saved report found for issue key {issue_key}")
    exit(1)

# Step 2 - Download PDF
pdf_url = f"{base}/gateway/api/atm/cloud/rest/api/latest/reports/export/pdf/{report_id}"
r_pdf = requests.get(pdf_url, auth=auth)
os.makedirs("report", exist_ok=True)
pdf_path = "report/rtm_execution_report.pdf"
with open(pdf_path, "wb") as f:
    f.write(r_pdf.content)
print(f"✅ PDF report downloaded: {pdf_path}")

# Step 3 - Optional HTML report
html_url = f"{base}/gateway/api/atm/cloud/rest/api/latest/reports/export/html/{report_id}"
r_html = requests.get(html_url, auth=auth)
html_path = "report/rtm_execution_report.html"
with open(html_path, "wb") as f:
    f.write(r_html.content)
print(f"✅ HTML report downloaded: {html_path}")

print("🎯 RTM Saved Report successfully fetched and stored in /report directory.")
