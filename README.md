<p align="center">
  <img src="lfb_logo.png" alt="LFB logo" width="120"><br/>
  <strong style="font-size:26px">London Fire Brigade — Response Times</strong><br/>
  Interactive Streamlit dashboard for incidents and response KPIs
</p>

<p align="center">
  <!-- Replace this after you deploy -->
  <a href="[https://YOUR-STREAMLIT-URL.streamlit.app](https://lfb-response-times-data-scientest-project.streamlit.app/)" target="_blank"><b>▶ LIVE APP</b></a>
</p>

---

## Overview
This dashboard explores **London Fire Brigade (LFB)** incident data and response performance.

### Features
- Clean sidebar with dropdown-style filters (Year, Borough, Incident type)
- KPI tiles (median & 90th percentile response, mobilisation, travel)
- Monthly trends, borough comparisons, incident-type comparisons
- Time-of-day patterns (hour, day-of-week)
- Robust **map**: auto-detects `Latitude/Longitude` (or `lat/lon`), cleans `"NULL"` values, optional **London bounding box**
- Download the **filtered dataset** as CSV

---

## Data requirements
This file (CSV or Parquet) includes:

- `IncidentNumber`
- `DateTimeOfCall` (datetime)
- `Borough`
- `IncidentGroup`
- Coordinates: `Latitude` / `Longitude` (or `lat` / `lon`, `lng`, `long`)
- KPIs: `response_time_min`, `mobilisation_time_min`, `travel_time_min`
- Time fields: `year`, `month`, `hour`, `dow`

**KPI logic**
- **Response** = `ArrivalTime − DateTimeOfCall`  
- **Mobilisation** = `MobilisedTime − DateTimeOfCall`  
- **Travel** = `ArrivalTime − MobilisedTime`

> Missing columns are handled gracefully—affected charts just hide with a helpful note.

---

## Repo structure

```text
.
├─ streamlit_app_v7.py
├─ requirements.txt
├─ lfb_fact_incident_kpi.parquet
└─ assets/
   ├─ lfb_logo.png
   └─ fire_icon.png
```

---

## Run locally
1. Install dependencies:
   ```bash
   pip install -r requirements.txt

2. Start the app:
   ```bash
    streamlit run streamlit_app_v7.py

3. Load data:
   - Place your .parquet/.csv in the repo root (auto-detected), or
   - Paste a full path in the sidebar, or
   - Upload the file via the sidebar.

## Deploy on Streamlit Community Cloud

1. Push this repo to GitHub.
2. Go to https://streamlit.io/cloud → New app.
3. Select this repo and set:
   -  Branch: main
   -  Main file: streamlit_app_v7.py
4. Click Deploy and update the LIVE APP link at the top of this README.

Large files note: The GitHub web uploader limits single files to 25 MB. Use GitHub Desktop or git push (allows up to 100 MB per file). For files >100 MB, use Git LFS or host externally and load at runtime.
