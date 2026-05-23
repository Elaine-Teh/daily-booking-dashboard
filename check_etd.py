import json
with open(r'C:\Users\elaineteh\WorkBuddy\20260522180506\daily-booking-dashboard\db_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
rows = d['data']
print('Sample ETD values:')
for r in rows[:20]:
    print(f"  etd={r.get('etd')!r} (type={type(r.get('etd')).__name__}) lane={r.get('lane')!r}")
