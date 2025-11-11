import os
import json
import requests
from requests.auth import HTTPBasicAuth

base = os.getenv("CONFLUENCE_BASE")
user = os.getenv("CONFLUENCE_USER")
token = os.getenv("CONFLUENCE_TOKEN")
space = os.getenv("CONFLUENCE_SPACE")
title = os.getenv("CONFLUENCE_TITLE")

auth = HTTPBasicAuth(user, token)
headers = {"X-Atlassian-Token": "no-check"}

def get_page_id():
    url = f"{base}/rest/api/content?spaceKey={space}&title={title}"
    r = requests.get(url, auth=auth)
    data = r.json()
    if data.get("results"):
        return data["results"][0]["id"]
    else:
        payload = {
            "type": "page",
            "title": title,
            "space": {"key": space},
            "body": {"storage": {"value": "<p>RTM Reports Page created automatically.</p>", "representation": "storage"}}
        }
        res = requests.post(f"{base}/rest/api/content", auth=auth, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
        return res.json().get("id")

def upload_or_update_attachment(page_id, file_path):
    filename = os.path.basename(file_path)
    url_check = f"{base}/rest/api/content/{page_id}/child/attachment?filename={filename}"
    res = requests.get(url_check, auth=auth)
    files = {"file": (filename, open(file_path, "rb"), "application/octet-stream")}

    # If attachment exists, update it
    if res.status_code == 200 and res.json().get("results"):
        attach_id = res.json()["results"][0]["id"]
        url_update = f"{base}/rest/api/content/{page_id}/child/attachment/{attach_id}/data"
        put_res = requests.put(url_update, headers=headers, auth=auth, files=files)
        if put_res.status_code in (200, 204):
            print(f"🔁 Updated existing attachment: {filename}")
        else:
            print(f"❌ Failed to update {filename}: {put_res.status_code} {put_res.text}")
    else:
        # Otherwise, upload as new
        post_res = requests.post(f"{base}/rest/api/content/{page_id}/child/attachment", headers=headers, auth=auth, files=files)
        if post_res.status_code in (200, 204):
            print(f"✅ Uploaded new attachment: {filename}")
        else:
            print(f"❌ Failed to upload {filename}: {post_res.status_code} {post_res.text}")

def update_page(page_id):
    # Optional: update timestamp or note on page
    update_body = {
        "version": {"number": 2},
        "title": title,
        "type": "page",
        "body": {"storage": {"value": "<p>Report updated successfully.</p>", "representation": "storage"}}
    }
    url = f"{base}/rest/api/content/{page_id}"
    res = requests.put(url, headers={"Content-Type": "application/json"}, auth=auth, data=json.dumps(update_body))
    if res.status_code in (200, 204):
        print(f"✅ Page content updated successfully.")
    else:
        print(f"⚠️ Page update warning: {res.status_code} {res.text}")

if __name__ == "__main__":
    page_id = get_page_id()
    if not page_id:
        print("❌ Unable to retrieve or create Confluence page.")
        exit(1)

    for file in ["report/rtm_execution_report.html", "report/rtm_execution_report.pdf"]:
        if os.path.exists(file):
            upload_or_update_attachment(page_id, file)
        else:
            print(f"⚠️ Missing file: {file}")

    update_page(page_id)
