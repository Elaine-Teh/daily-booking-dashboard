import urllib.request, json, os

PAT = os.environ.get("GH_PAT") or os.environ.get("GITHUB_PAT") or ""
if not PAT:
    print("ERROR: Set env var GH_PAT first (e.g. $env:GH_PAT='ghp_xxx')")
    raise SystemExit(1)

req = urllib.request.Request('https://api.github.com/repos/Elaine-Teh/daily-booking-dashboard/contents/')
req.add_header('Authorization', f'token {PAT}')
req.add_header('User-Agent', 'WorkBuddy')
resp = urllib.request.urlopen(req)
data = json.loads(resp.read())
for f in data:
    name = f["name"]
    ftype = f["type"]
    size = f.get("size", "")
    dl = f.get("download_url", "")
    print(f"{name}  {ftype}  {size}  {dl}")
