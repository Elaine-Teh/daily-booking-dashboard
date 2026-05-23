import json
with open(r'c:\Users\elaineteh\WorkBuddy\20260522180506\daily-booking-dashboard\db_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f"Valid JSON: keys={list(data.keys())}")
print(f"data array length: {len(data['data'])}")
print(f"lanes: {len(data['lane_list'])}")
print(f"pols: {len(data['pol_list'])}")
print(f"dels: {len(data['del_list'])}")
print(f"culs: {len(data['cul_list'])}")
print(f"generated_at: {data.get('generated_at')}")
