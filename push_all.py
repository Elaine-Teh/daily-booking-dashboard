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
with open(r"c:\Users\elaineteh\WorkBuddy\20260522180506\daily-booking-dashboard\index.html", "rb") as f:
    idx = base64.b64encode(f.read()).decode("utf-8")

info = api_get("/contents/index.html")
api_put("/contents/index.html", {
    "message": "fix: sort POL alphabetically in summary table",
    "content": idx,
    "sha": info["sha"],
    "branch": BRANCH
})
print("index.html pushed")

# Push db_data.json
with open(r"c:\Users\elaineteh\WorkBuddy\20260522180506\daily-booking-dashboard\db_data.json", "rb") as f:
    dat = base64.b64encode(f.read()).decode("utf-8")

info2 = api_get("/contents/db_data.json")
api_put("/contents/db_data.json", {
    "message": "data update",
    "content": dat,
    "sha": info2["sha"],
    "branch": BRANCH
})
print("db_data.json pushed")

print("\nDashboard: https://elaine-teh.github.io/daily-booking-dashboard/")
