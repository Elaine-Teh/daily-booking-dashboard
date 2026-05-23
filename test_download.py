import urllib.request, time

url = 'https://elaine-teh.github.io/daily-booking-dashboard/db_data.json'
req = urllib.request.Request(url, headers={'User-Agent': 'WorkBuddy'})

start = time.time()
try:
    resp = urllib.request.urlopen(req, timeout=60)
    content = resp.read()
    elapsed = time.time() - start
    print(f"Downloaded {len(content)/1024/1024:.2f} MB in {elapsed:.1f}s")
    print(f"Speed: {len(content)/1024/1024/elapsed:.2f} MB/s")
    
    # Check content-type
    ct = resp.headers.get('Content-Type', 'unknown')
    print(f"Content-Type: {ct}")
    
    # Check if gzip
    ce = resp.headers.get('Content-Encoding', 'none')
    print(f"Content-Encoding: {ce}")
except Exception as e:
    print(f"Error after {time.time()-start:.1f}s: {e}")
