import os, sys, re, json, time, pathlib, requests
from requests.auth import HTTPBasicAuth

# -------- Inputs from ENV / Jenkins --------
base        = os.getenv("JIRA_BASE", "").rstrip("/")
user        = os.getenv("JIRA_USER")
token       = os.getenv("JIRA_TOKEN")
issue_key   = os.getenv("JIRA_ISSUE_KEY", "RD-4")
env_name    = os.getenv("ENVIRONMENT", "DEV")
out_dir     = pathlib.Path("report")
out_dir.mkdir(parents=True, exist_ok=True)

auth = HTTPBasicAuth(user, token)
HEADERS_JSON = {"Accept": "application/json"}

def project_from_issue(key: str) -> str:
    m = re.match(r"([A-Z0-9]+)-\d+$", key.strip(), re.I)
    return m.group(1).upper() if m else key.split("-")[0].upper()

PROJECT_KEY = project_from_issue(issue_key)

def rtm_get(url, **kw):
    r = requests.get(url, auth=auth, headers=HEADERS_JSON, **kw)
    return r

def rtm_ok(r, expect=200):
    if r.status_code != expect:
        raise RuntimeError(f"{r.request.method} {r.url} -> {r.status_code} {r.text[:300]}")
    return r

def list_saved_reports():
    # ✅ Correct Cloud path
    url = f"{base}/atm-cloud/rest/api/latest/reports/saved?projectKey={PROJECT_KEY}"
    r = rtm_ok(rtm_get(url))
    return r.json() if r.text else []

def pick_report(items):
    """
    Strategy:
      1) Prefer Test Execution reports whose name/filters reference the given issue key or environment
      2) Otherwise, pick the newest item
    """
    if not isinstance(items, list):
        return None
    # enrich with timestamp fallback
    def score(it):
        name = (it.get("name") or "").upper()
        filters = json.dumps(it.get("filters", {})).upper()
        hits = 0
        if issue_key.upper() in name or issue_key.upper() in filters: hits += 2
        if env_name.upper() in name or env_name.upper() in filters: hits += 1
        # newer first if tie
        ts = it.get("updated") or it.get("created") or "1970-01-01T00:00:00.000Z"
        return (hits, ts)
    items_sorted = sorted(items, key=score, reverse=True)
    return items_sorted[0] if items_sorted else None

def export_report(report_id: str, kind: str):
    assert kind in ("pdf", "html")
    # ✅ Correct export URLs
    url = f"{base}/atm-cloud/rest/api/latest/reports/{report_id}/export/{kind}"
    r = rtm_ok(rtm_get(url), expect=200)
    return r.content

def main():
    print(f"🔎 Searching Saved RTM Reports in {PROJECT_KEY} for {issue_key}...")
    items = list_saved_reports()
    if not items:
        raise SystemExit("❌ No saved reports returned. Ensure you created one in RTM → Reports → Saved Reports.")

    chosen = pick_report(items)
    if not chosen:
        raise SystemExit("❌ Could not select a suitable saved report from the list.")

    rid   = str(chosen.get("id") or chosen.get("reportId") or "")
    rname = chosen.get("name") or f"report-{rid}"
    if not rid:
        raise SystemExit(f"❌ Saved report object has no id: {json.dumps(chosen)[:300]}")

    print(f"✅ Selected saved report: {rname} (id={rid})")

    # Download PDF + HTML
    pdf_bytes  = export_report(rid, "pdf")
    html_bytes = export_report(rid, "html")

    pdf_path  = out_dir / "rtm_execution_report.pdf"
    html_path = out_dir / "rtm_execution_report.html"

    pdf_path.write_bytes(pdf_bytes)
    html_path.write_bytes(html_bytes)

    print(f"💾 Saved: {pdf_path}")
    print(f"💾 Saved: {html_path}")
    print("🎉 Saved RTM report fetched successfully.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ {e}")
        sys.exit(1)
