import sys, os, requests, pandas as pd
from requests.auth import HTTPBasicAuth
from fpdf import FPDF
from datetime import datetime

# -----------------------------
# CLI Arguments from Jenkins
# -----------------------------
if len(sys.argv) < 6:
    print("Usage: fetch_rtm_execution.py <jira_base> <jira_user> <jira_token> <jira_issue_key> <environment>")
    sys.exit(1)

jira_base, jira_user, jira_token, jira_issue_key, environment = sys.argv[1:6]

auth = HTTPBasicAuth(jira_user, jira_token)
headers = {"Accept": "application/json"}
report_dir = "report"
os.makedirs(report_dir, exist_ok=True)
html_report = os.path.join(report_dir, "rtm_execution_report.html")
pdf_report = os.path.join(report_dir, "rtm_execution_report.pdf")

print(f"Fetching full RTM execution data for {jira_issue_key} ({environment})...")

# -----------------------------
# Fetch Execution Data (Deviniti RTM Cloud)
# -----------------------------
execution_url = f"{jira_base}/rest/atm/1.0/testrun/{jira_issue_key}"
response = requests.get(execution_url, headers=headers, auth=auth)

if response.status_code != 200:
    print(f"❌ Could not fetch test run {jira_issue_key}: {response.status_code}")
    sys.exit(1)

data = response.json()
test_cases = data.get("testCases", [])
summary = data.get("name", "N/A")
status = data.get("status", {}).get("name", "Unknown")
project_key = data.get("projectKey", "N/A")
created_on = data.get("created", "N/A")

records = []
for tc in test_cases:
    tc_key = tc.get("key", "N/A")
    tc_name = tc.get("name", "N/A")
    tc_status = tc.get("status", {}).get("name", "UNEXECUTED")
    assignee = tc.get("assignee", {}).get("displayName", "Unassigned")
    records.append({
        "Test Case Key": tc_key,
        "Test Case Name": tc_name,
        "Execution Status": tc_status,
        "Assignee": assignee,
        "Environment": environment
    })

# -----------------------------
# Generate HTML Report
# -----------------------------
print("Generating HTML report...")
df = pd.DataFrame(records)
total = len(df)
passed = len(df[df["Execution Status"] == "PASSED"])
failed = len(df[df["Execution Status"] == "FAILED"])
blocked = len(df[df["Execution Status"] == "BLOCKED"])
unexecuted = len(df[df["Execution Status"] == "UNEXECUTED"])
pass_rate = round((passed / total * 100), 2) if total else 0

header_html = f"""
<h2 style='color:#0D47A1;'>RTM Test Execution Report — {jira_issue_key}</h2>
<p><b>Project:</b> {project_key} | <b>Summary:</b> {summary}</p>
<p><b>Environment:</b> {environment} | <b>Status:</b> {status} | <b>Created:</b> {created_on}</p>
<hr>
<h3>Execution Summary</h3>
<ul>
  <li><b>Total Tests:</b> {total}</li>
  <li><b>Passed:</b> {passed}</li>
  <li><b>Failed:</b> {failed}</li>
  <li><b>Blocked:</b> {blocked}</li>
  <li><b>Unexecuted:</b> {unexecuted}</li>
  <li><b>Pass Rate:</b> {pass_rate}%</li>
</ul>
"""

df_html = df.to_html(index=False, border=1, justify="center")
with open(html_report, "w", encoding="utf-8") as f:
    f.write(header_html + df_html)

print(f"✅ HTML report generated at {html_report}")

# -----------------------------
# Generate PDF Report
# -----------------------------
print("Generating PDF report...")

class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, f"RTM Test Execution Report - {jira_issue_key}", 0, 1, "C")
        self.ln(5)

pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Helvetica", "", 10)

pdf.multi_cell(0, 8, f"Project: {project_key}\nSummary: {summary}\nEnvironment: {environment}\nStatus: {status}\nCreated On: {created_on}\nGenerated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
pdf.ln(10)

pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 10, "Execution Summary:", ln=True)
pdf.set_font("Helvetica", "", 10)
pdf.multi_cell(0, 8, f"Total Tests: {total}\nPassed: {passed}\nFailed: {failed}\nBlocked: {blocked}\nUnexecuted: {unexecuted}\nPass Rate: {pass_rate}%")
pdf.ln(10)

pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 10, "Test Case Results:", ln=True)
pdf.set_font("Helvetica", "", 9)

for _, row in df.iterrows():
    pdf.multi_cell(0, 6, f"{row['Test Case Key']} - {row['Test Case Name']} | Status: {row['Execution Status']} | Assignee: {row['Assignee']} | Env: {row['Environment']}")
    pdf.ln(2)

pdf.output(pdf_report)
print(f"✅ PDF report generated at {pdf_report}")
