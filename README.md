# 🧩 RTM Jira → Jenkins → Confluence → Email Automation Pipeline
**Version 1.0.0**
**Author:** DevSecOps Automation Team – Ramu

This project automates your QA lifecycle — integrating **Jira RTM Test Executions** with **Jenkins CI/CD**, automatically generating HTML/PDF reports, publishing them to **Confluence**, and notifying teams via **Email**.

## 📘 Table of Contents
1. Software Installation
2. Environment Setup
3. Jenkins Initial Setup
4. Required Plugins
5. Credentials Configuration
6. Jira Configuration & RTM Setup
7. Jenkins Pipeline Setup & Execution
8. Token & Password Creation
9. Pipeline Stage-by-Stage Explanation
10. Debugging & Troubleshooting
11. Folder Structure
12. Version Control & Audit
13. Architecture Diagram

---

## 1️⃣ Software Installation
| Component | Version | Notes |
|------------|----------|-------|
| Python | 3.11+ | Add to PATH |
| Git | 2.40+ | For repo checkout |
| Jenkins | 2.440+ (LTS) | Run as Windows service |
| Node (optional) | 18+ | For frontend testing |
| Docker (optional) | 28+ | If you containerize Jenkins |

```bash
python --version
git --version
```

Install Jenkins (Windows MSI) and access:  
➡️ http://localhost:8080

---

## 2️⃣ Environment Setup
Add to **System Environment Variables**:

| Variable | Example |
|-----------|----------|
| PYTHONPATH | C:\Python311 |
| JENKINS_HOME | C:\Users\<user>\.jenkins |
| PATH | Include C:\Python311 and C:\Python311\Scripts |

---

## 3️⃣ Jenkins Initial Setup
1. Open http://localhost:8080  
2. Enter admin password from C:\Program Files\Jenkins\secrets\initialAdminPassword  
3. Install Suggested Plugins  
4. Create admin user → Save configuration  

---

## 4️⃣ Required Plugins
| Plugin | Purpose |
|--------|----------|
| Git | SCM checkout |
| Pipeline | Declarative pipeline |
| Email-ext | Email notifications |
| Publish HTML | Publish RTM HTML report |
| HTTP Request | For REST API |
| Credentials Binding | Secure secrets |

---

## 5️⃣ Credentials Configuration
**Manage Jenkins → Credentials → Global → Add Credentials**

| ID | Type | Description |
|----|------|-------------|
| jira-base | Secret Text | e.g. https://yourdomain.atlassian.net |
| jira-user | Username + Password | Jira email |
| jira-api-token | Secret Text | Jira API token |
| confluence-base | Secret Text | e.g. https://yourdomain.atlassian.net/wiki |
| confluence-user | Username + Password | Confluence email |
| confluence-token | Secret Text | Confluence API token |
| smtp-user | Username + Password | Email + App password |
| smtp-pass | Secret Text | App password only |
| sender-email | Secret Text | From address |
| receiver-email | Secret Text | Recipients (comma separated) |

---

## 6️⃣ Jira Configuration & RTM Setup

### 🧱 A. Create Scrum Project
1. Jira → Projects → Create Project  
2. Select Scrum Software Project → Name: RTM Automation Demo  
3. Note the Key (e.g., EMP)

### 🧩 B. Install RTM App
1. Settings → Apps → Find new apps  
2. Search Requirements & Test Management for Jira (Deviniti)  
3. Click Install

### 🧰 C. Enable RTM in Your Project
RTM → Enable App in Project → Select Project (EMP) → Enable

### 🧪 D. Create Artifacts
| Artifact | Steps |
|-----------|-------|
| Requirement | RTM → Requirements → Create Requirement |
| Test Case | RTM → Test Cases → Create Test Case |
| Link | Requirement → Traceability → Link Test Case |
| Test Execution | RTM → Test Executions → Create Execution |
| Execute | Mark results as PASS / FAIL |
| Defect | Create Defect from failed step |
| Report | RTM → Reports → Export Traceability/Coverage |

### 🧾 E. Get Your Test Execution Key
From URL:  
`https://yourdomain.atlassian.net/browse/EMP-TE-05`  
➡️ JIRA_ISSUE_KEY = EMP-TE-05

---

## 7️⃣ Jenkins Pipeline Setup & Execution
1. Create new Pipeline Job → Name: RTM-Jira-Confluence-Email  
2. Select Pipeline Script from SCM  
   - SCM: Git  
   - Repo URL: https://github.com/devopsuser8413/rtm-jira-confluence-email.git  
3. Add parameters:
   - JIRA_ISSUE_KEY = default EMP-TE-01
   - ENVIRONMENT = choice [DEV, QA, UAT, PROD]
4. Click Build Now → enter your Test Execution key  

---

## 8️⃣ Token & Password Creation

### 🔑 Jira Token
1. Atlassian Profile → Security → API Tokens  
2. Create new token → copy and save as jira-api-token

### 🔑 Confluence Token
Same page → Create another → save as confluence-token

### 📧 Email App Password
For Outlook/Gmail:
1. Enable 2FA  
2. Create App Password for “Mail” or “Jenkins”  
3. Save as smtp-pass

---

## 9️⃣ Pipeline Stage-by-Stage Explanation

| Stage | Description |
|--------|--------------|
| Checkout Repository | Pulls Jenkinsfile + Python scripts from GitHub |
| Setup Python Env | Creates .venv, installs dependencies (pip install -r requirements.txt) |
| Fetch RTM Test Execution Data | Calls Jira REST API (/rest/atm/1.0/testrun/{JIRA_ISSUE_KEY}) → builds HTML + PDF |
| Publish Report to Confluence | Uploads both files via REST API to page ${CONFLUENCE_TITLE} |
| Send Email Notification | Uses Jenkins Email-ext plugin to send to multiple recipients |
| Post Section | Archives all reports as Jenkins build artifacts |

---

## 🔍 10️⃣ Debugging & Troubleshooting

| Issue | Root Cause | Resolution |
|--------|-------------|------------|
| Missing RTM menus | App not enabled | Enable in project settings |
| 401 Unauthorized | Invalid token or wrong ID | Regenerate Jira/Confluence tokens |
| Email not sent | SMTP blocked or invalid credentials | Re-verify host/port/app password |
| Python import error | Virtual env missing packages | Re-run pip install -r requirements.txt |
| Wrong report data | Incorrect JIRA_ISSUE_KEY | Use real Test Execution key |
| Upload fails to Confluence | Missing “Add Attachment” permission | Grant edit rights in Confluence Space |
| Encoding error | Windows locale | Add PYTHONUTF8=1 in environment |

---

## 📁 11️⃣ Folder Structure
```
rtm-jira-confluence-email/
├── Jenkinsfile
├── requirements.txt
├── report/
│   ├── rtm_execution_report.html
│   ├── rtm_execution_report.pdf
│   └── version.txt
├── scripts/
│   ├── fetch_rtm_execution.py
│   ├── upload_confluence.py
│   └── send_email.py
└── .gitignore
```

---

## 🧾 12️⃣ Version Control & Audit
Each run saves report versions inside /report/version.txt.  
Example:
```bash
echo v1.0.$(date +%Y%m%d%H%M) > report/version.txt
```
Then attach the versioned report to Confluence with unique timestamp for traceability.

---

## 🏗️ 13️⃣ Architecture Diagram

```mermaid
flowchart LR
    subgraph Jira["📘 Jira Cloud (RTM)"]
        A1[Create Requirements]
        A2[Create Test Cases]
        A3[Run Test Execution]
        A4[Get JIRA_ISSUE_KEY e.g. EMP-TE-05]
    end

    subgraph Jenkins["⚙️ Jenkins CI Pipeline"]
        B1[Checkout Repository]
        B2[Setup Python Virtual Env]
        B3[Fetch RTM Data via Jira API]
        B4[Generate HTML + PDF Report]
        B5[Upload to Confluence]
        B6[Send Email Notification]
        B7[Archive Artifacts]
    end

    subgraph Confluence["🧾 Confluence Space"]
        C1[Upload HTML/PDF Attachments]
        C2[Update Page Version]
    end

    subgraph Email["📧 Notification Recipients"]
        D1[QA Team]
        D2[Developers]
        D3[Managers]
    end

    Jira -->|Test Execution Key (EMP-TE-XX)| Jenkins
    Jenkins -->|REST API & Upload| Confluence
    Jenkins -->|SMTP| Email
    Confluence -->|Links shared in email| Email
```

---

## ✅ Expected Output
1. HTML + PDF Reports created under /report/  
2. Both reports uploaded to Confluence  
3. Jenkins sends notification email  
4. All artifacts archived in Jenkins  

Console Output Example:
```
Fetching RTM Test Execution for EMP-TE-05 (QA)...
✅ HTML report generated
✅ PDF report generated
✅ Uploaded to Confluence
✅ Email sent to qa@domain.com, dev@domain.com, manager@domain.com
✅ Build SUCCESS
```

---

**License:** Internal Use Only
