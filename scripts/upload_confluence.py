import os, json, requests
from requests.auth import HTTPBasicAuth

base = os.getenv("CONFLUENCE_BASE")
user = os.getenv("CONFLUENCE_USER")
token = os.getenv("CONFLUENCE_TOKEN")
space = os.getenv("CONFLUENCE_SPACE")
title = os.getenv("CONFLUENCE_TITLE")
report_path = os.getenv("REPORT_PATH", "report/rtm_execution_report.html")

auth = HTTPBasicAuth(user, token)
headers = {"X-Atlassian-Token": "no-check"}

def get_page_id():
    url = f"{base}/rest/api/content?spaceKey={space}&title={title}"
    r = requests.get(url, auth=auth).json()
    if r.get("results"):
        return r["results"][0]["id"]
    else:
        payload = {
            "type": "page",
            "title": title,
            "space": {"key": space},
            "body": {"storage": {"value": "<p>RTM Reports Page created automatically.</p>", "representation": "storage"}}
        }
        res = requests.post(f"{base}/rest/api/content", auth=auth, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
        return res.json().get("id")

def upload_attachment(page_id):
    url = f"{base}/rest/api/content/{page_id}/child/attachment"
    for path in ["report/rtm_execution_report.html", "report/rtm_execution_report.pdf"]:
        if not os.path.exists(path):
            continue
        with open(path, "rb") as f:
            files = {"file": (os.path.basename(path), f, "application/octet-stream")}
            r = requests.post(url, headers=headers, auth=auth, files=files)
            if r.status_code in (200, 204):
                print(f"✅ Uploaded {os.path.basename(path)} to Confluence page ID {page_id}")
            else:
                print(f"❌ Failed to upload {path}: {r.status_code} {r.text}")

if __name__ == "__main__":
    pid = get_page_id()
    if pid:
        upload_attachment(pid)
