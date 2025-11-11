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

print(f"Fetching Jira issue details for {jira_issue_key} ({environment})...")

# -----------------------------
# Fetch Jira Issue Data
# -----------------------------
issue_url = f"{jira_base}/rest/api/3/issue/{jira_issue_key}"
response = requests.get(issue_url, headers=headers, auth=auth)

if response.status_code != 200:
    print(f"❌ Could not fetch issue {jira_issue_key}: {response.status_code}")
    print(response.text)
    sys.exit(1)

data = response.json()
fields = data.get("fields", {})

project_key = fields.get("project", {}).get("key", "N/A")
summary = fields.get("summary", "N/A")
status = fields.get("status", {}).get("name", "N/A")
issue_type = fields.get("issuetype", {}).get("name", "N/A")
reporter = fields.get("reporter", {}).get("displayName", "N/A")
assignee = fields.get("assignee", {}).get("displayName", "Unassigned")
created_on = fields.get("created", "N/A")
priority = fields.get("priority", {}).get("name", "N/A")
description = fields.get("description", "No description provided.")

# -----------------------------
# Prepare Data for Report
# -----------------------------
records = [{
    "Field": "Project Key", "Value": project_key
}, {
    "Field": "Summary", "Value": summary
}, {
    "Field": "Status", "Value": status
}, {
    "Field": "Issue Type", "Value": issue_type
}, {
    "Field": "Priority", "Value": priority
}, {
    "Field": "Reporter", "Value": reporter
}, {
    "Field": "Assignee", "Value": assignee
}, {
    "Field": "Created On", "Value": created_on
}, {
    "Field": "Environment", "Value": environment
}]

# -----------------------------
# Generate HTML Report
# -----------------------------
print("Generating HTML report...")
df = pd.DataFrame(records)

header_html = f"""
<h2 style='color:#0D47A1;'>Jira Issue Report — {jira_issue_key}</h2>
<p><b>Project:</b> {project_key} | <b>Issue Type:</b> {issue_type}</p>
<p><b>Status:</b> {status} | <b>Priority:</b> {priority}</p>
<p><b>Reporter:</b> {reporter} | <b>Assignee:</b> {assignee}</p>
<p><b>Environment:</b> {environment}</p>
<hr>
<h3>Issue Summary</h3>
<p>{summary}</p>
<h3>Description</h3>
<p>{description}</p>
<hr>
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
        self.cell(0, 10, f"Jira Issue Report - {jira_issue_key}", 0, 1, "C")
        self.ln(5)

pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Helvetica", "", 10)

pdf.multi_cell(
    0, 8,
    f"Project: {project_key}\nIssue Key: {jira_issue_key}\nSummary: {summary}\n"
    f"Status: {status}\nPriority: {priority}\nReporter: {reporter}\nAssignee: {assignee}\n"
    f"Created On: {created_on}\nEnvironment: {environment}\n"
    f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)
pdf.ln(10)

pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 10, "Field Details:", ln=True)
pdf.set_font("Helvetica", "", 10)
for _, row in df.iterrows():
    pdf.cell(0, 8, f"{row['Field']}: {row['Value']}", ln=True)

pdf.ln(10)
pdf.multi_cell(0, 8, f"Description:\n{description}")

pdf.output(pdf_report)
print(f"✅ PDF report generated at {pdf_report}")
