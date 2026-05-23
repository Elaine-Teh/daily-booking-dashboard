import urllib.request, json, base64, os

PAT = os.environ.get("GH_PAT") or os.environ.get("GITHUB_PAT") or ""
if not PAT:
    print("ERROR: Set env var GH_PAT first (e.g. $env:GH_PAT='ghp_xxx')")
    raise SystemExit(1)
REPO = "Elaine-Teh/daily-booking-dashboard"
BRANCH = "main"
HEADERS = {
    "Authorization": "token " + PAT,
    "User-Agent": "WorkBuddy",
    "Content-Type": "application/json"
}
API = f"https://api.github.com/repos/{REPO}"

def api_get(path):
    req = urllib.request.Request(API + path, headers=HEADERS)
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

def api_put(path, data):
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(API + path, data=body, headers=HEADERS, method="PUT")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

# Read local file
script_path = r"c:\Users\elaineteh\WorkBuddy\20260522180506\daily-booking-dashboard\generate_daily_booking_dashboard.py"
with open(script_path, "rb") as f:
    file_content = f.read()
content_b64 = base64.b64encode(file_content).decode("utf-8")

# Get current file SHA for update
file_info = api_get("/contents/generate_daily_booking_dashboard.py")
sha = file_info["sha"]

# Commit
result = api_put("/contents/generate_daily_booking_dashboard.py", {
    "message": "fix: refactor to dual-file architecture (index.html + db_data.json)\n\n- index.html: lightweight UI shell (~35KB) with CDN Chart.js\n- db_data.json: data loaded async via fetch\n- Removed inline data embedding (was causing 16.7MB single file)\n- Added loading state and error handling\n- Output renamed from daily_booking_dashboard.html to index.html",
    "content": content_b64,
    "sha": sha,
    "branch": BRANCH
})

print(f"Committed: {result['commit']['sha'][:8]}")
print(f"URL: {result['content']['html_url']}")
