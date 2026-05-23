import urllib.request, json
req = urllib.request.Request(
    'https://api.github.com/repos/Elaine-Teh/daily-booking-dashboard/contents/db_data.json',
    headers={'User-Agent': 'WorkBuddy'}
)
resp = urllib.request.urlopen(req)
data = json.loads(resp.read())
print(f"GitHub size: {data['size']/1024/1024:.2f} MB")
print(f"SHA: {data['sha'][:16]}")
print(f"Download URL: {data['download_url'][:60]}...")
