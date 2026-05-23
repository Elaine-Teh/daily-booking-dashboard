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

# Push index.html
print("Pushing index.html...")
with open(r"C:\Users\elaineteh\WorkBuddy\20260522180506\daily-booking-dashboard\index.html", "rb") as f:
    html_b64 = base64.b64encode(f.read()).decode("utf-8")
file_info = api_get("/contents/index.html")
result1 = api_put("/contents/index.html", {
    "message": "fix: lightweight index.html (31KB) - CDN Chart.js + fetch db_data.json",
    "content": html_b64,
    "sha": file_info["sha"],
    "branch": BRANCH
})
print(f"  index.html -> {result1['commit']['sha'][:8]}")

# Push db_data.json
print("Pushing db_data.json (26.9MB, may take a moment)...")
with open(r"C:\Users\elaineteh\WorkBuddy\20260522180506\daily-booking-dashboard\db_data.json", "rb") as f:
    json_b64 = base64.b64encode(f.read()).decode("utf-8")
file_info2 = api_get("/contents/db_data.json")
result2 = api_put("/contents/db_data.json", {
    "message": "fix: db_data.json - 54K booking records with lane/pol/del/cul metadata",
    "content": json_b64,
    "sha": file_info2["sha"],
    "branch": BRANCH
})
print(f"  db_data.json -> {result2['commit']['sha'][:8]}")

print("\nDone! GitHub Pages will auto-deploy.")
print("Dashboard: https://elaine-teh.github.io/daily-booking-dashboard/")
