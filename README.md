# Daily Booking Dashboard

CULines daily booking data analysis dashboard.

## Quick Start

1. Place `daily booking.xlsx` from SFTP (`Master Data-Bob/daily booking.xlsx`) into `data/`
2. Place `Income Data Base-Marketing.xlsx` from SFTP (`Master Data - Elaine/Income Data Base-Marketing.xlsx`) into `data/`
3. Run: `python generate_daily_booking_dashboard.py`
4. Open: `daily_booking_dashboard.html`

## Features

- **Multi-Lane filter**: Select one or more Trunk Lanes (42 lanes)
- **CUL Code filter**: Searchable multi-select (848 codes)
- **POL / DEL filter**: Searchable multi-select port filters
- **KPI cards**: 20ft, 40ft, 40RF, FEU, TEU, Booking Count, Container Weight
- **Summary pivot table**: Trunk Lane -> CUL Code -> POL/DEL -> metrics
- **Charts**: TEU by POL, TEU by DEL, Volume by DEL (Weight)
- **Detail table**: Searchable booking data with 17 columns
- **Custom Notes**: Per-lane notes with localStorage persistence

## Data Sources

- SFTP: 10.5.4.2:6622, Master Data-Bob/daily booking.xlsx
- SFTP: 10.5.4.2:6622, Master Data - Elaine/Income Data Base-Marketing.xlsx

## Tech Stack

- Python (openpyxl for Excel reading)
- Vanilla JavaScript + Chart.js (self-contained HTML)
