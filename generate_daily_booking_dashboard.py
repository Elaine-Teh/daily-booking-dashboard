#!/usr/bin/env python3
"""
Daily Booking Dashboard Generator v2
- Multi-VVD selection (searchable checkbox dropdown)
- Searchable multi-select POL / DEL filters
- Summary pivot table: TRUNK LANE -> CUL CODE -> POR Region / DEL / Booking / Weight
- KPI cards with Container Weight
- TEU by POL & DEL charts
- Custom notes panel (localStorage per VVD)
"""

import json, os, openpyxl, warnings
from datetime import datetime

warnings.filterwarnings('ignore')

EXCEL_PATH = r'data\daily booking.xlsx'
INCOME_PATH = r'data\Income Data Base-Marketing.xlsx'
OUTPUT_HTML = r'daily_booking_dashboard.html'

# ============ Build POR -> Region mapping from Income Data Base ============
print("1/3 Building POR->Region mapping...")
por_region_map = {}
iwb = openpyxl.load_workbook(INCOME_PATH, read_only=True, data_only=True)
iws = iwb['Sheet1']
iheaders = next(iws.iter_rows(min_row=1, max_row=1, values_only=True))
por_code_idx = por_region_idx = None
for i, h in enumerate(iheaders):
    hs = str(h).strip() if h else ''
    if 'POR Code' in hs: por_code_idx = i
    if 'POR Region' in hs: por_region_idx = i
for row in iws.iter_rows(min_row=2, values_only=True):
    pc = str(row[por_code_idx]).strip() if row[por_code_idx] else ''
    pr = str(row[por_region_idx]).strip() if row[por_region_idx] else ''
    if pc and pr and pc not in por_region_map:
        por_region_map[pc] = pr
iwb.close()
print(f"  {len(por_region_map)} POR->Region mappings")

# ============ Read daily booking data ============
print("2/3 Reading daily booking.xlsx...")
wb = openpyxl.load_workbook(EXCEL_PATH, read_only=True, data_only=True)
ws = wb['Sheet1']

def s(val):
    if val is None: return ''
    return str(val).strip()
def f(val):
    if val is None: return 0
    try: return float(val)
    except: return 0
def i(val): return int(f(val))
def dt(val):
    if val is None: return ''
    if isinstance(val, datetime): return val.strftime('%Y-%m-%d')
    return s(val)

raw_data = []
lane_set, pol_set, del_set, cul_set = set(), set(), set(), set()

for row in ws.iter_rows(min_row=2, values_only=True):
    trunk_vessel = s(row[3])  # col D: TRUNK VESSEL NAME
    if not trunk_vessel or trunk_vessel == '0000E': continue

    pol = s(row[15])      # col P: POL
    del_port = s(row[18]) # col S: DEL
    por = s(row[14])      # col O: POR
    ft20 = i(row[19])     # col T: 20ft
    ft40 = i(row[20])     # col U: 40ft
    ft40rf = i(row[21])   # col V: 40rf
    booking_teu = f(row[49])  # col AX: BOOKING TTL TEU
    ttl_teu = booking_teu if booking_teu > 0 else (ft20 + (ft40 + ft40rf) * 2)

    rec = {
        'vvd': trunk_vessel,
        'cul_code': s(row[4]),
        'lane': s(row[2]),
        'first_vessel': s(row[1]),
        'bl_no': s(row[5]),
        'pol': pol, 'pod': s(row[17]), 'del_port': del_port,
        'por': por, 'por_region': por_region_map.get(por, ''),
        'etd': dt(row[16]),
        'ft20': ft20, 'ft40': ft40, 'ft40rf': ft40rf, 'teu': ttl_teu,
        'shipper': s(row[11]), 'forwarder': s(row[12]),
        'contract_no': s(row[8]), 'freight_term': s(row[10]),
        'sul_yn': s(row[7]),
        'booking_cnt': i(row[22]),
        'container_weight': f(row[23]),
    }
    raw_data.append(rec)
    if pol: pol_set.add(pol)
    if del_port: del_set.add(del_port)
    cul_code = s(row[4])
    if cul_code: cul_set.add(cul_code)
    lane = s(row[2])
    if lane: lane_set.add(lane)
wb.close()

lane_list = sorted(lane_set)
pol_list = sorted(pol_set)
del_list = sorted(del_set)
cul_list = sorted(cul_set)

print(f"  {len(raw_data)} records, {len(lane_list)} Lanes, {len(pol_list)} POLs, {len(del_list)} DELs, {len(cul_list)} CULs")

# ============ Generate HTML ============
print("3/3 Generating HTML...")

HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Daily Booking Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f0f2f5;color:#1a1a2e}
.header{background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);color:#fff;padding:16px 24px;display:flex;align-items:center;justify-content:space-between}
.header h1{font-size:20px;font-weight:600}
.header .updated{font-size:12px;opacity:.7}
.container{max-width:1400px;margin:0 auto;padding:16px 20px}

/* Filters Bar */
.filters-bar{background:#fff;border-radius:10px;padding:14px 18px;margin-bottom:14px;box-shadow:0 1px 3px rgba(0,0,0,.08);display:flex;gap:12px;flex-wrap:wrap;align-items:center}
.filter-group{display:flex;align-items:center;gap:6px}
.filter-group label{font-size:12px;font-weight:600;color:#666;white-space:nowrap;text-transform:uppercase;letter-spacing:.5px}

/* Multi-Select Dropdown */
.multi-select{position:relative;min-width:200px}
.multi-select .ms-trigger{display:flex;align-items:center;justify-content:space-between;background:#f5f6fa;border:1px solid #ddd;border-radius:6px;padding:6px 10px;cursor:pointer;font-size:13px;min-width:160px;user-select:none;transition:border-color .2s}
.multi-select .ms-trigger:hover{border-color:#0f3460}
.multi-select.active .ms-trigger{border-color:#0f3460;box-shadow:0 0 0 2px rgba(15,52,96,.15)}
.ms-trigger .ms-text{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1}
.ms-trigger .ms-arrow{font-size:10px;margin-left:6px;transition:transform .2s;color:#888}
.multi-select.active .ms-arrow{transform:rotate(180deg)}
.ms-dropdown{display:none;position:absolute;top:100%;left:0;margin-top:4px;background:#fff;border:1px solid #ddd;border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,.12);z-index:1000;min-width:280px;max-height:380px;overflow:hidden}
.multi-select.active .ms-dropdown{display:block}
.ms-search{width:100%;border:none;border-bottom:1px solid #eee;padding:10px 12px;font-size:13px;outline:none}
.ms-actions{display:flex;gap:8px;padding:8px 12px;border-bottom:1px solid #eee}
.ms-actions button{flex:1;padding:4px 8px;font-size:11px;border:1px solid #ddd;border-radius:4px;background:#fff;cursor:pointer;transition:.15s}
.ms-actions button:hover{background:#0f3460;color:#fff;border-color:#0f3460}
.ms-list{max-height:260px;overflow-y:auto;padding:4px 0}
.ms-list label{display:flex;align-items:center;gap:8px;padding:6px 12px;font-size:13px;cursor:pointer;transition:background .1s}
.ms-list label:hover{background:#f0f4ff}
.ms-list input[type=checkbox]{accent-color:#0f3460}
.ms-badge{display:inline-block;background:#0f3460;color:#fff;border-radius:10px;padding:1px 8px;font-size:11px;margin-left:4px}
.ms-count{font-size:11px;color:#999;margin-left:auto}
.filter-clear{font-size:11px;color:#e74c3c;cursor:pointer;text-decoration:underline;white-space:nowrap}
.filter-clear:hover{color:#c0392b}

/* KPI Cards */
.kpi-row{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px;margin-bottom:14px}
.kpi-card{background:#fff;border-radius:10px;padding:16px 18px;box-shadow:0 1px 3px rgba(0,0,0,.08);text-align:center}
.kpi-card .kpi-value{font-size:28px;font-weight:700;color:#0f3460;line-height:1.2}
.kpi-card .kpi-label{font-size:11px;color:#999;text-transform:uppercase;letter-spacing:.5px;margin-top:4px}
.kpi-card.accent .kpi-value{color:#e74c3c}

/* Charts */
.chart-row{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:14px}
.chart-box{background:#fff;border-radius:10px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,.08)}
.chart-box h3{font-size:14px;font-weight:600;color:#1a1a2e;margin-bottom:12px}
.chart-box canvas{max-height:320px}

/* Summary Table */
.summary-section{background:#fff;border-radius:10px;padding:16px 18px;margin-bottom:14px;box-shadow:0 1px 3px rgba(0,0,0,.08)}
.summary-section h2{font-size:15px;font-weight:600;color:#1a1a2e;margin-bottom:12px;display:flex;align-items:center;gap:8px}
.summary-section h2 .badge{font-size:11px;font-weight:400;background:#e8f0fe;color:#0f3460;padding:2px 8px;border-radius:10px}
.summary-table{width:100%;border-collapse:collapse;font-size:13px}
.summary-table th{background:#f5f6fa;padding:8px 10px;text-align:left;font-weight:600;font-size:11px;text-transform:uppercase;color:#666;border-bottom:2px solid #e0e0e0;white-space:nowrap}
.summary-table td{padding:8px 10px;border-bottom:1px solid #eee}
.summary-table .lane-row{background:#f0f4ff;font-weight:700;cursor:pointer}
.summary-table .lane-row td{font-size:13px;color:#0f3460}
.summary-table .lane-row .expand-icon{display:inline-block;width:16px;text-align:center;transition:transform .2s}
.summary-table .lane-row.expanded .expand-icon{transform:rotate(90deg)}
.summary-table .cul-row td{padding-left:28px;font-weight:600;font-size:12px}
.summary-table .detail-row td{padding-left:46px;font-size:12px;color:#555}
.summary-table tr.detail-row.hidden{display:none}
.summary-table .num{text-align:right;font-variant-numeric:tabular-nums}
.summary-table .highlight{color:#0f3460;font-weight:600}

/* Detail Table */
.detail-section{background:#fff;border-radius:10px;padding:16px 18px;margin-bottom:14px;box-shadow:0 1px 3px rgba(0,0,0,.08)}
.detail-section h2{font-size:15px;font-weight:600;margin-bottom:12px;display:flex;align-items:center;justify-content:space-between}
.detail-search{width:240px;padding:6px 10px;border:1px solid #ddd;border-radius:6px;font-size:13px;outline:none}
.detail-search:focus{border-color:#0f3460}
.detail-table-wrap{max-height:500px;overflow:auto}
.detail-table{width:100%;border-collapse:collapse;font-size:12px}
.detail-table th{position:sticky;top:0;background:#f5f6fa;padding:8px 8px;text-align:left;font-weight:600;font-size:11px;text-transform:uppercase;color:#666;z-index:1}
.detail-table td{padding:7px 8px;border-bottom:1px solid #f0f0f0;white-space:nowrap}
.detail-table tr:hover{background:#f8faff}
.detail-info{font-size:12px;color:#999;margin-top:8px}

/* Notes Panel */
.notes-section{background:#fff;border-radius:10px;padding:16px 18px;margin-bottom:14px;box-shadow:0 1px 3px rgba(0,0,0,.08)}
.notes-section h2{font-size:15px;font-weight:600;margin-bottom:12px}
.notes-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:10px}
.note-card{background:#fafbfc;border:1px solid #eee;border-radius:8px;padding:10px 12px}
.note-card .note-vvd{font-size:12px;font-weight:600;color:#0f3460;margin-bottom:6px}
.note-card textarea{width:100%;border:1px solid #e0e0e0;border-radius:4px;padding:8px;font-size:12px;resize:vertical;min-height:50px;font-family:inherit;outline:none}
.note-card textarea:focus{border-color:#0f3460}
.note-card .note-save{font-size:10px;color:#27ae60;margin-top:4px}
.note-actions{display:flex;gap:8px;margin-bottom:10px}
.note-actions button{padding:4px 12px;font-size:12px;border:1px solid #ddd;border-radius:4px;background:#fff;cursor:pointer}
.note-actions button:hover{background:#0f3460;color:#fff;border-color:#0f3460}
.note-actions button.primary{background:#0f3460;color:#fff;border-color:#0f3460}

@media(max-width:1100px){.chart-row{grid-template-columns:1fr}.kpi-row{grid-template-columns:repeat(2,1fr)}.filters-bar{flex-direction:column;align-items:stretch}}
</style>
</head>
<body>
<div class="header">
  <h1>📊 Daily Booking Dashboard</h1>
  <span class="updated">UPDATED_TS</span>
</div>
<div class="container">
  <!-- FILTERS -->
  <div class="filters-bar">
    <div class="filter-group">
      <label>Trunk Lane</label>
      <div class="multi-select" id="msLane" style="min-width:180px">
        <div class="ms-trigger" id="msLaneTrigger"><span class="ms-text">All Lanes</span><span class="ms-arrow">▼</span></div>
        <div class="ms-dropdown" id="msLaneDropdown">
          <input class="ms-search" id="msLaneSearch" placeholder="Search Lane...">
          <div class="ms-actions">
            <button id="msLaneAll">Select All</button>
            <button id="msLaneNone">Clear All</button>
          </div>
          <div class="ms-list" id="msLaneList"></div>
        </div>
      </div>
    </div>
    <div class="filter-group">
      <label>CUL Code</label>
      <div class="multi-select" id="msCul">
        <div class="ms-trigger" id="msCulTrigger"><span class="ms-text">All CULs</span><span class="ms-arrow">▼</span></div>
        <div class="ms-dropdown" id="msCulDropdown">
          <input class="ms-search" id="msCulSearch" placeholder="Search CUL Code...">
          <div class="ms-actions">
            <button id="msCulAll">Select All</button>
            <button id="msCulNone">Clear All</button>
          </div>
          <div class="ms-list" id="msCulList"></div>
        </div>
      </div>
    </div>
    <div class="filter-group">
      <label>POL</label>
      <div class="multi-select" id="msPol">
        <div class="ms-trigger" id="msPolTrigger"><span class="ms-text">All POLs</span><span class="ms-arrow">▼</span></div>
        <div class="ms-dropdown" id="msPolDropdown">
          <input class="ms-search" id="msPolSearch" placeholder="Search POL...">
          <div class="ms-actions">
            <button id="msPolAll">Select All</button>
            <button id="msPolNone">Clear All</button>
          </div>
          <div class="ms-list" id="msPolList"></div>
        </div>
      </div>
    </div>
    <div class="filter-group">
      <label>DEL</label>
      <div class="multi-select" id="msDel">
        <div class="ms-trigger" id="msDelTrigger"><span class="ms-text">All DELs</span><span class="ms-arrow">▼</span></div>
        <div class="ms-dropdown" id="msDelDropdown">
          <input class="ms-search" id="msDelSearch" placeholder="Search DEL...">
          <div class="ms-actions">
            <button id="msDelAll">Select All</button>
            <button id="msDelNone">Clear All</button>
          </div>
          <div class="ms-list" id="msDelList"></div>
        </div>
      </div>
    </div>
    <span class="filter-clear" id="resetAll">Reset All</span>
  </div>

  <!-- KPI CARDS -->
  <div class="kpi-row">
    <div class="kpi-card"><div class="kpi-value" id="kpiLane">0</div><div class="kpi-label">Lanes</div></div>
    <div class="kpi-card"><div class="kpi-value" id="kpi20">0</div><div class="kpi-label">20ft</div></div>
    <div class="kpi-card"><div class="kpi-value" id="kpi40">0</div><div class="kpi-label">40ft</div></div>
    <div class="kpi-card accent"><div class="kpi-value" id="kpiTeu">0</div><div class="kpi-label">Total TEU</div></div>
    <div class="kpi-card"><div class="kpi-value" id="kpiBooking">0</div><div class="kpi-label">Booking Count</div></div>
    <div class="kpi-card"><div class="kpi-value" id="kpiWeight">0</div><div class="kpi-label">Container Weight</div></div>
  </div>

  <!-- SUMMARY TABLE -->
  <div class="summary-section">
    <h2>📋 Summary by Trunk Lane & CUL Code <span class="badge" id="summaryCount"></span></h2>
    <div style="overflow-x:auto">
      <table class="summary-table" id="summaryTable"><thead>
        <tr>
          <th style="min-width:80px">TRUNK LANE</th>
          <th style="min-width:110px">CUL CODE</th>
          <th style="min-width:80px">POL</th>
          <th style="min-width:80px">DEL</th>
          <th class="num" style="min-width:60px">20ft</th>
          <th class="num" style="min-width:60px">40ft</th>
          <th class="num" style="min-width:60px">40RF</th>
          <th class="num accent" style="min-width:60px">FEU</th>
          <th class="num">Sum of Booking</th>
          <th class="num">Sum of Container Weight</th>
          <th class="num">Avg Weight</th>
        </tr>
      </thead><tbody></tbody></table>
    </div>
  </div>

  <!-- CHARTS -->
  <div class="chart-row">
    <div class="chart-box"><h3>TEU by POL</h3><canvas id="chartPol"></canvas></div>
    <div class="chart-box"><h3>TEU by DEL</h3><canvas id="chartDel"></canvas></div>
    <div class="chart-box"><h3>Volume by DEL (Weight)</h3><canvas id="chartDelVol"></canvas></div>
  </div>

  <!-- DETAIL TABLE -->
  <div class="detail-section">
    <h2>📄 Detail Data <input class="detail-search" id="detailSearch" placeholder="Search BL / Shipper / Forwarder..."></h2>
    <div class="detail-table-wrap">
      <table class="detail-table" id="detailTable"><thead><tr>
        <th>BL No.</th><th>CUL Code</th><th>Trunk VVD</th><th>Lane</th><th>POR</th><th>POL</th><th>ETD</th><th>POD</th><th>DEL</th><th>20ft</th><th>40ft</th><th>TEU</th><th>Booking</th><th>Weight</th><th>Shipper</th><th>Forwarder</th>
      </tr></thead><tbody></tbody></table>
    </div>
    <div class="detail-info" id="detailCount"></div>
  </div>

  <!-- NOTES -->
  <div class="notes-section">
    <h2>✏️ Custom Notes <span style="font-weight:400;font-size:12px;color:#999">— saved automatically per Lane</span></h2>
    <div class="note-actions">
      <button class="primary" id="btnAddNote">+ Add Note for Selected Lane</button>
      <button id="btnClearNotes">Clear All Notes</button>
    </div>
    <div class="notes-grid" id="notesGrid"></div>
  </div>
</div>

<script>
Chart.defaults.font.family = "-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif";
Chart.defaults.font.size = 11;

var ALL_DATA = __DATA__;
var LANE_LIST = __LANE_LIST__;
var POL_LIST = __POL_LIST__;
var DEL_LIST = __DEL_LIST__;
var CUL_LIST = __CUL_LIST__;

// ============ MULTI-SELECT ENGINE ============
function buildMultiSelect(id, items, onChange) {
  var root = document.getElementById('ms' + id);
  var trigger = document.getElementById('ms' + id + 'Trigger');
  var dropdown = document.getElementById('ms' + id + 'Dropdown');
  var search = document.getElementById('ms' + id + 'Search');
  var list = document.getElementById('ms' + id + 'List');
  var btnAll = document.getElementById('ms' + id + 'All');
  var btnNone = document.getElementById('ms' + id + 'None');

  var selected = new Set(items);
  var state = { input: false, focused: false };

  function updateTrigger() {
    var count = selected.size, total = items.length;
    var txt = count === total ? 'All ' + id.toUpperCase() + 's' : count + ' ' + id.toUpperCase() + ' selected';
    trigger.querySelector('.ms-text').textContent = txt;
    if (trigger.querySelector('.ms-badge')) trigger.querySelector('.ms-badge').remove();
    if (count > 0 && count < total) {
      var badge = document.createElement('span'); badge.className = 'ms-badge'; badge.textContent = count;
      trigger.appendChild(badge);
    }
  }

  function renderList(filter) {
    list.innerHTML = '';
    var filt = (filter || '').toLowerCase();
    items.forEach(function(item) {
      if (filt && item.toLowerCase().indexOf(filt) === -1) return;
      var label = document.createElement('label');
      var cb = document.createElement('input');
      cb.type = 'checkbox'; cb.checked = selected.has(item);
      cb.onchange = function() {
        if (cb.checked) selected.add(item); else selected.delete(item);
        updateTrigger(); onChange(selected);
      };
      label.appendChild(cb);
      label.appendChild(document.createTextNode(item));
      list.appendChild(label);
    });
  }

  function toggle() {
    root.classList.toggle('active');
    if (root.classList.contains('active')) {
      search.value = ''; renderList(''); search.focus();
    }
  }

  trigger.onclick = function(e) { e.stopPropagation(); toggle(); };
  search.oninput = function() { renderList(search.value); };
  btnAll.onclick = function(e) { e.stopPropagation(); selected = new Set(items); updateTrigger(); renderList(search.value); onChange(selected); };
  btnNone.onclick = function(e) { e.stopPropagation(); selected = new Set(); updateTrigger(); renderList(search.value); onChange(selected); };

  document.addEventListener('click', function(e) {
    if (!root.contains(e.target)) root.classList.remove('active');
  });

  updateTrigger(); renderList('');
  return { getSelected: function() { return selected; }, setAll: function() { selected = new Set(items); updateTrigger(); renderList(''); }, clear: function() { selected = new Set(); updateTrigger(); renderList(''); } };
}

// ============ FILTERING LOGIC ============
function getFilteredData() {
  var laneSel = msLane.getSelected();
  var polSel = msPol.getSelected();
  var delSel = msDel.getSelected();
  var culSel = msCul.getSelected();
  return ALL_DATA.filter(function(r) {
    return laneSel.has(r.lane) && polSel.has(r.pol) && delSel.has(r.del_port) && culSel.has(r.cul_code);
  });
}

// ============ INIT ============
var msLane, msPol, msDel, msCul;
function initFilters() {
  msLane = buildMultiSelect('Lane', LANE_LIST, refreshAll);
  msPol = buildMultiSelect('Pol', POL_LIST, refreshAll);
  msDel = buildMultiSelect('Del', DEL_LIST, refreshAll);
  msCul = buildMultiSelect('Cul', CUL_LIST, refreshAll);
}

// ============ KPI CARDS ============
function updateKPIs(data) {
  var laneSet = new Set(data.map(function(r) { return r.lane; }));
  document.getElementById('kpiLane').textContent = laneSet.size;
  document.getElementById('kpi20').textContent = data.reduce(function(s,r){return s+r.ft20},0);
  document.getElementById('kpi40').textContent = data.reduce(function(s,r){return s+r.ft40},0);
  var tteu = data.reduce(function(s,r){return s+r.teu},0);
  document.getElementById('kpiTeu').textContent = tteu.toLocaleString();
  document.getElementById('kpiBooking').textContent = data.length;
  var tw = data.reduce(function(s,r){return s+r.container_weight},0);
  document.getElementById('kpiWeight').textContent = tw.toLocaleString();
}

// ============ SUMMARY TABLE ============
function buildSummary(data) {
  var groups = {};
  data.forEach(function(r) {
    var lk = r.lane || '(blank)';
    var ck = r.cul_code || '(blank)';
    var comboKey = r.pol + '|||' + r.del_port;
    if (!groups[lk]) groups[lk] = {};
    if (!groups[lk][ck]) groups[lk][ck] = {};
    if (!groups[lk][ck][comboKey]) {
      groups[lk][ck][comboKey] = { pol: r.pol, del: r.del_port, booking_sum: 0, weight_sum: 0, ft20_sum: 0, ft40_sum: 0, ft40rf_sum: 0 };
    }
    groups[lk][ck][comboKey].booking_sum += r.booking_cnt;
    groups[lk][ck][comboKey].weight_sum += r.container_weight;
    groups[lk][ck][comboKey].ft20_sum += r.ft20;
    groups[lk][ck][comboKey].ft40_sum += r.ft40;
    groups[lk][ck][comboKey].ft40rf_sum += r.ft40rf;
  });

  var tbody = '';
  var totalRows = 0;
  var lanes = Object.keys(groups).sort();
  lanes.forEach(function(lane) {
    var laneBooking = 0, laneWeight = 0, laneFT20 = 0, laneFT40 = 0, laneFT40RF = 0;
    var culCodes = Object.keys(groups[lane]).sort();
    culCodes.forEach(function(ck) {
      var combos = Object.values(groups[lane][ck]);
      laneBooking += combos.reduce(function(s,v){return s+v.booking_sum},0);
      laneWeight += combos.reduce(function(s,v){return s+v.weight_sum},0);
      laneFT20 += combos.reduce(function(s,v){return s+v.ft20_sum},0);
      laneFT40 += combos.reduce(function(s,v){return s+v.ft40_sum},0);
      laneFT40RF += combos.reduce(function(s,v){return s+v.ft40rf_sum},0);
    });

    var laneFEU = laneFT40 + laneFT40RF;

    tbody += '<tr class="lane-row" onclick="toggleLane(this)" data-lane="' + escapeHtml(lane) + '">';
    tbody += '<td><span class="expand-icon">▶</span> <b>' + escapeHtml(lane) + '</b></td>';
    tbody += '<td></td><td></td><td></td><td class="num highlight">' + laneFT20.toLocaleString() + '</td>';
    tbody += '<td class="num highlight">' + laneFT40.toLocaleString() + '</td>';
    tbody += '<td class="num highlight">' + laneFT40RF.toLocaleString() + '</td>';
    tbody += '<td class="num highlight accent">' + laneFEU.toLocaleString() + '</td>';
    tbody += '<td class="num highlight">' + laneBooking.toLocaleString() + '</td>';
    tbody += '<td class="num highlight">' + laneWeight.toLocaleString() + '</td>';
    tbody += '<td class="num highlight">' + (laneBooking > 0 ? Math.round(laneWeight/laneBooking).toLocaleString() : '0') + '</td>';
    tbody += '</tr>';

    culCodes.forEach(function(ck) {
      var combos = Object.values(groups[lane][ck]);
      var culBooking = combos.reduce(function(s,v){return s+v.booking_sum},0);
      var culWeight = combos.reduce(function(s,v){return s+v.weight_sum},0);
      var culFT20 = combos.reduce(function(s,v){return s+v.ft20_sum},0);
      var culFT40 = combos.reduce(function(s,v){return s+v.ft40_sum},0);
      var culFT40RF = combos.reduce(function(s,v){return s+v.ft40rf_sum},0);
      var culFEU = culFT40 + culFT40RF;

      tbody += '<tr class="cul-row hidden" data-parent="' + escapeHtml(lane) + '">';
      tbody += '<td></td><td><b>' + escapeHtml(ck) + '</b></td>';
      tbody += '<td></td><td></td>';
      tbody += '<td class="num">' + culFT20.toLocaleString() + '</td>';
      tbody += '<td class="num">' + culFT40.toLocaleString() + '</td>';
      tbody += '<td class="num">' + culFT40RF.toLocaleString() + '</td>';
      tbody += '<td class="num accent">' + culFEU.toLocaleString() + '</td>';
      tbody += '<td class="num">' + culBooking.toLocaleString() + '</td>';
      tbody += '<td class="num">' + culWeight.toLocaleString() + '</td>';
      tbody += '<td class="num">' + (culBooking > 0 ? Math.round(culWeight/culBooking).toLocaleString() : '0') + '</td>';
      tbody += '</tr>';
      totalRows++;

      combos.forEach(function(c) {
        var cFEU = c.ft40_sum + c.ft40rf_sum;
        tbody += '<tr class="detail-row hidden" data-parent="' + escapeHtml(lane) + '">';
        tbody += '<td></td><td></td>';
        tbody += '<td>' + escapeHtml(c.pol) + '</td>';
        tbody += '<td>' + escapeHtml(c.del) + '</td>';
        tbody += '<td class="num">' + c.ft20_sum.toLocaleString() + '</td>';
        tbody += '<td class="num">' + c.ft40_sum.toLocaleString() + '</td>';
        tbody += '<td class="num">' + c.ft40rf_sum.toLocaleString() + '</td>';
        tbody += '<td class="num accent">' + cFEU.toLocaleString() + '</td>';
        tbody += '<td class="num">' + c.booking_sum.toLocaleString() + '</td>';
        tbody += '<td class="num">' + c.weight_sum.toLocaleString() + '</td>';
        var avg = c.booking_sum > 0 ? Math.round(c.weight_sum / c.booking_sum) : 0;
        tbody += '<td class="num">' + avg.toLocaleString() + '</td>';
        tbody += '</tr>';
        totalRows++;
      });
    });
  });

  document.getElementById('summaryTable').querySelector('tbody').innerHTML = tbody;
  document.getElementById('summaryCount').textContent = totalRows + ' groups';
}

function toggleLane(row) {
  row.classList.toggle('expanded');
  row.classList.toggle('collapsed', !row.classList.contains('expanded'));
  var lane = row.dataset.lane;
  var visible = row.classList.contains('expanded');
  document.querySelectorAll('[data-parent="' + lane + '"]').forEach(function(r) {
    r.classList.toggle('hidden', !visible);
  });
}

// ============ CHARTS ============
var chartPolInst, chartDelInst, chartDelVolInst;
function updateCharts(data) {
  // TEU by POL
  var polMap = {};
  data.forEach(function(r) {
    var k = r.pol || '(blank)';
    polMap[k] = (polMap[k] || 0) + r.teu;
  });
  var polEntries = Object.entries(polMap).sort(function(a,b){return b[1]-a[1]}).slice(0,15);

  var ctxPol = document.getElementById('chartPol').getContext('2d');
  if (chartPolInst) chartPolInst.destroy();
  chartPolInst = new Chart(ctxPol, {
    type: 'bar', data: { labels: polEntries.map(function(e){return e[0]}), datasets: [{ label: 'TEU', data: polEntries.map(function(e){return e[1]}), backgroundColor: '#0f3460', borderRadius: 4 }] },
    options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { callback: function(v){ return v.toLocaleString(); } } } } }
  });

  // TEU by DEL
  var delMap = {};
  data.forEach(function(r) {
    var k = r.del_port || '(blank)';
    delMap[k] = (delMap[k] || 0) + r.teu;
  });
  var delEntries = Object.entries(delMap).sort(function(a,b){return b[1]-a[1]}).slice(0,15);

  var ctxDel = document.getElementById('chartDel').getContext('2d');
  if (chartDelInst) chartDelInst.destroy();
  chartDelInst = new Chart(ctxDel, {
    type: 'bar', data: { labels: delEntries.map(function(e){return e[0]}), datasets: [{ label: 'TEU', data: delEntries.map(function(e){return e[1]}), backgroundColor: '#e74c3c', borderRadius: 4 }] },
    options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { callback: function(v){ return v.toLocaleString(); } } } } }
  });

  // DEL Volume (Container Weight) by DEL
  var delVolMap = {};
  data.forEach(function(r) {
    var k = r.del_port || '(blank)';
    delVolMap[k] = (delVolMap[k] || 0) + r.container_weight;
  });
  var delVolEntries = Object.entries(delVolMap).sort(function(a,b){return b[1]-a[1]}).slice(0,15);

  var ctxDelVol = document.getElementById('chartDelVol').getContext('2d');
  if (chartDelVolInst) chartDelVolInst.destroy();
  chartDelVolInst = new Chart(ctxDelVol, {
    type: 'bar', data: { labels: delVolEntries.map(function(e){return e[0]}), datasets: [{ label: 'Weight', data: delVolEntries.map(function(e){return e[1]}), backgroundColor: '#27ae60', borderRadius: 4 }] },
    options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { callback: function(v){ return v.toLocaleString(); } } } } }
  });
}

// ============ DETAIL TABLE ============
function updateDetail(data) {
  var searchTxt = (document.getElementById('detailSearch').value || '').toLowerCase();
  var filtered = data;
  if (searchTxt) {
    filtered = data.filter(function(r) {
      return (r.bl_no || '').toLowerCase().indexOf(searchTxt) !== -1
          || (r.shipper || '').toLowerCase().indexOf(searchTxt) !== -1
          || (r.forwarder || '').toLowerCase().indexOf(searchTxt) !== -1
          || (r.contract_no || '').toLowerCase().indexOf(searchTxt) !== -1
          || (r.vvd || '').toLowerCase().indexOf(searchTxt) !== -1
          || (r.lane || '').toLowerCase().indexOf(searchTxt) !== -1;
    });
  }
  var rows = filtered.slice(0, 500).map(function(r) {
    return '<tr>' +
      '<td>' + escapeHtml(r.bl_no) + '</td>' +
      '<td>' + escapeHtml(r.cul_code) + '</td>' +
      '<td>' + escapeHtml(r.vvd) + '</td>' +
      '<td>' + escapeHtml(r.lane) + '</td>' +
      '<td>' + escapeHtml(r.por) + '</td>' +
      '<td><b>' + escapeHtml(r.pol) + '</b></td>' +
      '<td>' + escapeHtml(r.etd) + '</td>' +
      '<td>' + escapeHtml(r.pod) + '</td>' +
      '<td><b>' + escapeHtml(r.del_port) + '</b></td>' +
      '<td class="num">' + r.ft20 + '</td>' +
      '<td class="num">' + r.ft40 + '</td>' +
      '<td class="num"><b>' + r.teu + '</b></td>' +
      '<td class="num">' + r.booking_cnt + '</td>' +
      '<td class="num">' + r.container_weight.toLocaleString() + '</td>' +
      '<td>' + escapeHtml(r.shipper) + '</td>' +
      '<td>' + escapeHtml(r.forwarder) + '</td>' +
      '</tr>';
  }).join('');
  document.getElementById('detailTable').querySelector('tbody').innerHTML = rows || '<tr><td colspan="16" style="text-align:center;padding:20px">No matching records</td></tr>';
  document.getElementById('detailCount').textContent = 'Showing ' + Math.min(filtered.length, 500) + ' of ' + filtered.length + ' records';
}

// ============ CUSTOM NOTES ============
function getNotes() {
  try { return JSON.parse(localStorage.getItem('db_notes') || '{}'); } catch(e) { return {}; }
}
function saveNotes(notes) {
  localStorage.setItem('db_notes', JSON.stringify(notes));
}
function renderNotes() {
  var notes = getNotes();
  var selectedLanes = Array.from(msLane ? msLane.getSelected() : []);
  var grid = document.getElementById('notesGrid');
  var html = '';
  selectedLanes.forEach(function(lane) {
    var note = notes[lane] || '';
    html += '<div class="note-card">' +
      '<div class="note-vvd">' + escapeHtml(lane) + '</div>' +
      '<textarea data-lane="' + escapeHtml(lane) + '" placeholder="Add your notes here...">' + escapeHtml(note) + '</textarea>' +
      (note ? '<div class="note-save">✓ Saved</div>' : '') +
      '</div>';
  });
  if (!html) html = '<div style="color:#999;font-size:13px;padding:8px">Select Lane(s) above to add notes.</div>';
  grid.innerHTML = html;

  // Auto-save on blur
  grid.querySelectorAll('textarea').forEach(function(ta) {
    ta.onblur = function() {
      var lane = ta.dataset.lane;
      var notes = getNotes();
      notes[lane] = ta.value;
      saveNotes(notes);
      ta.nextElementSibling && ta.nextElementSibling.remove();
      if (ta.value) {
        var s = document.createElement('div'); s.className = 'note-save'; s.textContent = '✓ Saved';
        ta.parentNode.appendChild(s);
      }
    };
  });
}

function addNoteForSelected() {
  var selected = Array.from(msLane.getSelected());
  if (selected.length === 0) { alert('Please select at least one Lane first.'); return; }
  var lane = selected[0];
  var notes = getNotes();
  notes[lane] = notes[lane] || '';
  saveNotes(notes);
  renderNotes();
}

// ============ MAIN REFRESH ============
function refreshAll() {
  var data = getFilteredData();
  updateKPIs(data);
  buildSummary(data);
  updateCharts(data);
  updateDetail(data);
  renderNotes();
}

// ============ SETUP ============
function escapeHtml(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

document.getElementById('detailSearch').oninput = function() { updateDetail(getFilteredData()); };
document.getElementById('resetAll').onclick = function() {
  msLane.setAll(); msPol.setAll(); msDel.setAll(); msCul.setAll(); refreshAll();
};
document.getElementById('btnAddNote').onclick = addNoteForSelected;
document.getElementById('btnClearNotes').onclick = function() {
  if (confirm('Clear all saved notes?')) { localStorage.removeItem('db_notes'); renderNotes(); }
};

initFilters();
refreshAll();
</script>
</body>
</html>'''

# Embed data
data_json = json.dumps(raw_data, ensure_ascii=False)
lane_json = json.dumps(lane_list, ensure_ascii=False)
pol_json = json.dumps(pol_list, ensure_ascii=False)
del_json = json.dumps(del_list, ensure_ascii=False)
cul_json = json.dumps(cul_list, ensure_ascii=False)

HTML = HTML.replace('__DATA__', data_json)
HTML = HTML.replace('__LANE_LIST__', lane_json)
HTML = HTML.replace('__POL_LIST__', pol_json)
HTML = HTML.replace('__DEL_LIST__', del_json)
HTML = HTML.replace('__CUL_LIST__', cul_json)
HTML = HTML.replace('UPDATED_TS', datetime.now().strftime('Updated: %Y-%m-%d %H:%M'))

with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
    f.write(HTML)

size_mb = os.path.getsize(OUTPUT_HTML) / (1024*1024)
print(f"\nDone! -> {OUTPUT_HTML} ({size_mb:.1f} MB)")
