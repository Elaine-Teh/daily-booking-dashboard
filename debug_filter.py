import json

with open(r'C:\Users\elaineteh\WorkBuddy\20260522180506\daily-booking-dashboard\db_data.json', 'r', encoding='utf-8') as f:
    payload = json.load(f)

data = payload['data']
lane_list = payload['lane_list']

print("=== Simulating JS filter logic ===")
print(f"Total records: {len(data)}")
print(f"LANE_LIST: {lane_list[:10]}...")

# Scenario 1: ETD only (All Lanes)
etd_from, etd_to = '2026-01-01', '2026-06-20'
result1 = [r for r in data if r['etd'] >= etd_from and r['etd'] <= etd_to]
rex_in_result1 = [r for r in result1 if r['lane'] == 'REX']
print(f"\n[Scenario 1] ETD only ({etd_from} ~ {etd_to}): {len(result1)} records")
print(f"  REX records in result: {len(rex_in_result1)}")

# Scenario 2: Lane=REX + same ETD
lane_sel = {'REX'}
pol_sel = set(r['pol'] for r in data if r['lane'] == 'REX' and r['etd'] >= etd_from and r['etd'] <= etd_to and r['pol'])
cul_sel = set(r['cul_code'] for r in data if r['lane'] == 'REX' and r['etd'] >= etd_from and r['etd'] <= etd_to and r['cul_code'])
del_sel = set(r['del_port'] for r in data if r['lane'] == 'REX' and r['etd'] >= etd_from and r['etd'] <= etd_to and r['del_port'])

print(f"\n[Scenario 2] Lane=REX + ETD ({etd_from} ~ {etd_to})")
print(f"  pol_sel count: {len(pol_sel)}")
print(f"  cul_sel count: {len(cul_sel)}")
print(f"  del_sel count: {len(del_sel)}")

# Simulate getFilteredData
result2 = []
for r in data:
    if r['lane'] not in lane_sel:
        continue
    if r['pol'] not in pol_sel:
        continue
    if r['del_port'] not in del_sel:
        continue
    if r['cul_code'] not in cul_sel:
        continue
    if etd_from and r['etd'] < etd_from:
        continue
    if etd_to and r['etd'] > etd_to:
        continue
    result2.append(r)

print(f"  Filtered result: {len(result2)} records")

# Check if pol_sel/del_sel/cul_sel are correct
print(f"\n  Sample pol_sel: {sorted(pol_sel)[:10]}")
print(f"  Sample del_sel: {sorted(del_sel)[:10]}")
print(f"  Sample cul_sel: {sorted(cul_sel)[:10]}")

# Check a specific REX record
rex_sample = [r for r in data if r['lane'] == 'REX' and r['etd'] >= etd_from and r['etd'] <= etd_to][:3]
print(f"\n  Sample REX records:")
for r in rex_sample:
    print(f"    lane={r['lane']}, cul={r['cul_code']}, pol={r['pol']}, del={r['del_port']}, etd={r['etd']}")
    print(f"    pol in pol_sel: {r['pol'] in pol_sel}")
    print(f"    del in del_sel: {r['del_port'] in del_sel}")
    print(f"    cul in cul_sel: {r['cul_code'] in cul_sel}")
