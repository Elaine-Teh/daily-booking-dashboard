import urllib.request, json, os

PAT = os.environ.get("GH_PAT") or os.environ.get("GITHUB_PAT") or ""
if not PAT:
    print("ERROR: Set env var GH_PAT first (e.g. $env:GH_PAT='ghp_xxx')")
    raise SystemExit(1)

BASE = "https://api.github.com/repos/Elaine-Teh/daily-booking-dashboard/contents/"
HEADERS = {
    "Authorization": f"token {PAT}",
    "User-Agent": "WorkBuddy"
}

OUT_DIR = r"c:\Users\elaineteh\WorkBuddy\20260522180506\daily-booking-dashboard"
os.makedirs(OUT_DIR, exist_ok=True)

files_to_download = [
    "generate_daily_booking_dashboard.py",
    "README.md",
    ".gitignore",
]

for fname in files_to_download:
    url = BASE + fname
    req = urllib.request.Request(url, headers=HEADERS)
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    content = data["content"]
    if data.get("encoding") == "base64":
        import base64
        content = base64.b64decode(content)
    else:
        content = content.encode("utf-8")
    
    outpath = os.path.join(OUT_DIR, fname)
    with open(outpath, "wb") as f:
        f.write(content)
    print(f"Downloaded: {fname} ({len(content)} bytes)")

print("\nDone!")
