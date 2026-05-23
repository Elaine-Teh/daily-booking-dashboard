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

# Read new index.html
with open(r"c:\Users\elaineteh\WorkBuddy\20260522180506\daily-booking-dashboard\index.html", "rb") as f:
    file_content = f.read()
content_b64 = base64.b64encode(file_content).decode("utf-8")

# Get current file SHA
file_info = api_get("/contents/index.html")
sha = file_info["sha"]

# Commit
result = api_put("/contents/index.html", {
    "message": "fix: add cache-buster (?v=2) + 30s timeout + better error messages\n\n- fetch URL now includes ?v=2 to bypass CDN cache\n- Added AbortController with 30s timeout\n- Enhanced error messages for timeout vs network errors",
    "content": content_b64,
    "sha": sha,
    "branch": BRANCH
})

print(f"index.html -> {result['commit']['sha'][:8]}")
print(f"Dashboard: https://elaine-teh.github.io/daily-booking-dashboard/")
