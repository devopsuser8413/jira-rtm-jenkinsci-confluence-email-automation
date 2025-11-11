import os, json, requests
from requests.auth import HTTPBasicAuth

# -----------------------------
# Environment Variables
# -----------------------------
base = os.getenv("CONFLUENCE_BASE")
user = os.getenv("CONFLUENCE_USER")
token = os.getenv("CONFLUENCE_TOKEN")
space = os.getenv("CONFLUENCE_SPACE")
title = os.getenv("CONFLUENCE_TITLE")
report_files = [
    "report/rtm_execution_report.html",
    "report/rtm_execution_report.pdf"
]

auth = HTTPBasicAuth(user, token)

# -----------------------------
# Helper: Get or Create Page
# -----------------------------
def get_page_id():
    url = f"{base}/rest/api/content?spaceKey={space}&title={title}"
    r = requests.get(url, auth=auth)
    if r.status_code == 200 and r.json().get("results"):
        return r.json()["results"][0]["id"]
    
    print(f"ℹ️ Page '{title}' not found, creating new page...")
    payload = {
        "type": "page",
        "title": title,
        "space": {"key": space},
        "body": {"storage": {"value": "<p>RTM Reports Page created automatically.</p>", "representation": "storage"}}
    }
    res = requests.post(f"{base}/rest/api/content", auth=auth, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
    if res.status_code in (200, 201):
        print(f"✅ Created Confluence page '{title}'")
        return res.json().get("id")
    else:
        print(f"❌ Failed to create page: {res.status_code} {res.text}")
        return None

# -----------------------------
# Helper: Upload Attachments
# -----------------------------
def upload_attachments(page_id):
    url = f"{base}/rest/api/content/{page_id}/child/attachment"
    for file_path in report_files:
        if not os.path.exists(file_path):
            print(f"⚠️ File not found: {file_path}")
            continue
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, "application/octet-stream")}
            response = requests.post(url, auth=auth, headers={"X-Atlassian-Token": "no-check"}, files=files)
            if response.status_code in (200, 201):
                print(f"✅ Uploaded {os.path.basename(file_path)} to Confluence page ID {page_id}")
            else:
                print(f"❌ Failed to upload {file_path}: {response.status_code} {response.text}")

# -----------------------------
# Helper: Embed Attachments in Page Body
# -----------------------------
def embed_attachments(page_id):
    # Get current page version
    page_url = f"{base}/rest/api/content/{page_id}?expand=body.storage,version"
    page_data = requests.get(page_url, auth=auth).json()
    version = page_data["version"]["number"] + 1

    # Build file embed HTML
    file_links = ""
    for f in report_files:
        if os.path.exists(f):
            file_name = os.path.basename(f)
            file_links += f'<ac:structured-macro ac:name="view-file"><ac:parameter ac:name="name">{file_name}</ac:parameter></ac:structured-macro><br/>'

    new_body = f"""
    <p>Latest RTM Automation Report uploaded from Jenkins.</p>
    <p><b>Build Timestamp:</b> Auto-generated via Jenkins pipeline</p>
    <hr/>
    {file_links}
    """

    payload = {
        "id": page_id,
        "type": "page",
        "title": title,
        "space": {"key": space},
        "version": {"number": version},
        "body": {"storage": {"value": new_body, "representation": "storage"}}
    }

    update_url = f"{base}/rest/api/content/{page_id}"
    res = requests.put(update_url, auth=auth, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
    if res.status_code in (200, 201):
        print("✅ Page content updated with embedded report links.")
    else:
        print(f"❌ Failed to update page content: {res.status_code} {res.text}")

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    pid = get_page_id()
    if pid:
        upload_attachments(pid)
        embed_attachments(pid)
