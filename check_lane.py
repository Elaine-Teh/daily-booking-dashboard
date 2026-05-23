import json

with open(r'C:\Users\elaineteh\WorkBuddy\20260522180506\daily-booking-dashboard\db_data.json', 'r', encoding='utf-8') as f:
    payload = json.load(f)

data = payload['data']
print(f"Total records: {len(data)}")

# Check REX records
rex_records = [r for r in data if r['lane'] == 'REX']
print(f"Records with lane='REX': {len(rex_records)}")

if rex_records:
    etds = sorted(set(r['etd'] for r in rex_records if r['etd']))
    print(f"REX ETD range: {etds[0]} ~ {etds[-1]}")
    print(f"REX sample CULs: {sorted(set(r['cul_code'] for r in rex_records))[:10]}")
else:
    # Check what lanes exist that contain 'REX'
    lanes = set(r['lane'] for r in data)
    rex_like = [l for l in lanes if 'REX' in l.upper()]
    print(f"Lanes containing 'REX': {rex_like}")
    print(f"All lanes sample: {sorted(lanes)[:20]}")

# Check for ETD range overlap
etd_filtered = [r for r in data if r['etd'] >= '2026-01-01' and r['etd'] <= '2026-06-20']
print(f"\nRecords in ETD 2026-01-01 ~ 2026-06-20: {len(etd_filtered)}")
rex_etd = [r for r in etd_filtered if r['lane'] == 'REX']
print(f"REX records in that ETD range: {len(rex_etd)}")

# Check all unique lanes
all_lanes = sorted(set(r['lane'] for r in data if r['lane']))
print(f"\nTotal unique lanes: {len(all_lanes)}")
print(f"Lanes: {all_lanes}")
