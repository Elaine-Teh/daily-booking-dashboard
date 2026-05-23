import urllib.request, re

req = urllib.request.Request(
    'https://raw.githubusercontent.com/Elaine-Teh/daily-booking-dashboard/main/index.html',
    headers={'User-Agent': 'WorkBuddy'}
)
resp = urllib.request.urlopen(req)
html = resp.read().decode('utf-8')

# Find all script tags and look for fetch/db_data
scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
print(f"Found {len(scripts)} script blocks")

for i, script in enumerate(scripts):
    script_clean = script.encode('ascii', 'ignore').decode('ascii')
    if 'db_data' in script_clean or 'fetch' in script_clean or 'initDashboard' in script_clean:
        print(f"\n=== Script block {i} (first 2000 chars) ===")
        print(script_clean[:2000])
        print("\n...[truncated]...")
        break
else:
    print("No script with fetch/db_data found")
