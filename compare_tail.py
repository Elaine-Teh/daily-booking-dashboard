import urllib.request

# Get GitHub raw file tail
req = urllib.request.Request(
    'https://raw.githubusercontent.com/Elaine-Teh/daily-booking-dashboard/main/db_data.json',
    headers={'User-Agent': 'WorkBuddy'}
)
resp = urllib.request.urlopen(req)
# Read the tail - use range request if possible, or read all
content = resp.read()
github_tail = content[-200:]
print(f"GitHub raw size: {len(content)/1024/1024:.2f} MB")
print(f"GitHub tail: {github_tail}")
print()

# Get local file tail
with open(r'c:\Users\elaineteh\WorkBuddy\20260522180506\daily-booking-dashboard\db_data.json', 'rb') as f:
    f.seek(0, 2)
    size = f.tell()
    f.seek(max(0, size - 200))
    local_tail = f.read()
    print(f"Local size: {size/1024/1024:.2f} MB")
    print(f"Local tail: {local_tail}")
    print()
    
print(f"Match: {github_tail == local_tail}")
