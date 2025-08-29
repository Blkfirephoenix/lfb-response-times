import streamlit as st
import pandas as pd
from glob import glob
import io, os
from pathlib import Path

st.set_page_config(page_title="LFB Response Times — Dashboard", page_icon="🔥", layout="wide")

# -------- CSS (bigger title + tidy sidebar buttons) --------
st.markdown("""
<style>
.block-container { padding-top: 0.6rem; }
.lfb-title { font-size: 2.4rem; line-height: 1.1; font-weight: 800; margin: 0.2rem 0 0.6rem 0; }
.lfb-subtitle { color:#94a3b8; margin-bottom: 0.6rem; }
section[data-testid="stSidebar"] { background: #0f172a; }
.sidebar-card { background:#0b1220; border:1px solid #1f2937; padding:10px 12px; border-radius:12px; margin-bottom:10px; }
.sidebar-btn { width:100%; }
[data-baseweb="tag"] { display:none; } /* hide chips */
.headerbar { background:#0b1220; border:1px solid #1f2937; padding:10px 14px; border-radius:14px; margin-bottom: 0.5rem; }
.kpi { background:#111827; padding:12px 14px; border-radius:12px; border:1px solid #1f2937; }
.kpi h3 { margin:0; font-size:0.9rem; color:#94a3b8;}
.kpi p  { margin:6px 0 0 0; font-size:1.6rem; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# -------- Helpers --------
@st.cache_data
def load_from_path(path: str) -> pd.DataFrame:
    if path.lower().endswith(".parquet"):
        return pd.read_parquet(path)
    return pd.read_csv(path)

@st.cache_data
def load_uploaded(file) -> pd.DataFrame:
    name = file.name.lower()
    if name.endswith(".parquet"):
        data = file.read()
        return pd.read_parquet(io.BytesIO(data))
    return pd.read_csv(file)

def detect_coord_columns(df: pd.DataFrame):
    lat = lon = None
    for c in df.columns:
        low = c.strip().lower()
        if low in {"lat","latitude"} and lat is None: lat = c
        if low in {"lon","lng","long","longitude"} and lon is None: lon = c
    return lat, lon

def summarize(sel):
    if not sel: return "All"
    if len(sel) <= 3: return ", ".join(str(x) for x in sel)
    return f"{len(sel)} selected"

# -------- Sidebar: brand, data source, filter BUTTONS --------
with st.sidebar:
    st.markdown(
    """
    <div style="display:flex; flex-direction:column; align-items:center; text-align:center;">
        <div style="font-size:44px; line-height:1; margin-bottom:6px;">🔥</div>
        <div style="font-size:28px; font-weight:800; margin:0 0 4px 0;">
            London Fire Brigade
        </div>
        <div style="color:#94a3b8; margin:0;">
            Response Times Dashboard
        </div>
    </div>
    """,
    unsafe_allow_html=True,)
    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.subheader("Data source", divider="red")
    candidates = sorted(glob("lfb_fact_incident_kpi*.parquet") + glob("lfb_fact_incident_kpi*.csv"))
    choice = st.selectbox("Detected files", ["(none)"] + candidates, index=1 if candidates else 0)
    typed_path = st.text_input("Or paste full path")
    uploaded = st.file_uploader("Or upload CSV/Parquet", type=["csv","parquet"])
    st.markdown('</div>', unsafe_allow_html=True)

# Load
df = None; loaded_from = None
if typed_path.strip():
    try: df = load_from_path(typed_path.strip()); loaded_from = f"typed path: {typed_path.strip()}"
    except Exception as e: st.sidebar.error(f"Typed path error: {e}")
if df is None and choice != "(none)":
    try: df = load_from_path(choice); loaded_from = f"detected file: {choice}"
    except Exception as e: st.sidebar.error(f"Detected file error: {e}")
if df is None and uploaded is not None:
    try: df = load_uploaded(uploaded); loaded_from = f"uploaded: {uploaded.name}"
    except Exception as e: st.sidebar.error(f"Upload error: {e}")
if df is None:
    st.warning("No data loaded. Put the file next to this app, paste a full path, or upload it in the sidebar.")
    st.stop()
st.success(f"Loaded from {loaded_from}")

if "DateTimeOfCall" in df.columns: df["DateTimeOfCall"] = pd.to_datetime(df["DateTimeOfCall"], errors="coerce")
if "year" in df.columns: df["year"] = pd.to_numeric(df["year"], errors="coerce")

# Options
years = sorted(df["year"].dropna().unique().tolist()) if "year" in df else []
types = sorted(df["IncidentGroup"].dropna().unique().tolist()) if "IncidentGroup" in df else []
boroughs = sorted(df["Borough"].dropna().unique().tolist()) if "Borough" in df else []

if "year_sel" not in st.session_state: st.session_state.year_sel = years[-3:] if years else []
if "type_sel" not in st.session_state: st.session_state.type_sel = types[:] if types else []
if "borough_sel" not in st.session_state: st.session_state.borough_sel = boroughs[:] if boroughs else []

# Sidebar filter buttons (popover/expander inside a card)
with st.sidebar:
    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.subheader("Filters", divider="red")

    def button_popover(label, key, options, help_txt=None):
        # Popover if available; fallback to expander
        if hasattr(st, "popover"):
            with st.popover(label, use_container_width=True, help=help_txt):
                st.multiselect("Select", options=options, default=st.session_state.get(key, []), key=key)
        else:
            with st.expander(label, expanded=False):
                st.multiselect("Select", options=options, default=st.session_state.get(key, []), key=key)

    button_popover(f"Year ▾   |   {summarize(st.session_state.year_sel)}", "year_sel", years, "Filter by year")
    button_popover(f"Incident type ▾   |   {summarize(st.session_state.type_sel)}", "type_sel", types, "Filter by incident type")
    button_popover(f"Borough ▾   |   {summarize(st.session_state.borough_sel)}", "borough_sel", boroughs, "Filter by borough")

    if st.button("Reset filters", use_container_width=True):
        st.session_state.year_sel = years[-3:] if years else []
        st.session_state.type_sel = types[:] if types else []
        st.session_state.borough_sel = boroughs[:] if boroughs else []
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Apply filters
dff = df.copy()
if st.session_state.year_sel and "year" in dff:
    dff = dff[dff["year"].isin(st.session_state.year_sel)]
if st.session_state.type_sel and "IncidentGroup" in dff:
    dff = dff[dff["IncidentGroup"].isin(st.session_state.type_sel)]
if st.session_state.borough_sel and "Borough" in dff:
    dff = dff[dff["Borough"].isin(st.session_state.borough_sel)]

# -------- Title + KPIs --------
st.markdown('<div class="lfb-title">London Fire Brigade — Response Times</div>', unsafe_allow_html=True)
st.markdown('<div class="lfb-subtitle">Interactive analytics of incidents and response KPIs</div>', unsafe_allow_html=True)

st.markdown('<div class="headerbar">', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    n_inc = int(dff["IncidentNumber"].nunique()) if "IncidentNumber" in dff else len(dff)
    st.markdown(f'<div class="kpi"><h3>Incidents</h3><p>{n_inc:,}</p></div>', unsafe_allow_html=True)
with c2:
    v = float(dff["response_time_min"].median()) if "response_time_min" in dff else float("nan")
    st.markdown(f'<div class="kpi"><h3>Median response (min)</h3><p>{v:.1f}</p></div>', unsafe_allow_html=True)
with c3:
    import numpy as np
    v = float(dff["response_time_min"].quantile(0.90)) if "response_time_min" in dff else np.nan
    st.markdown(f'<div class="kpi"><h3>90th pct response (min)</h3><p>{v:.1f}</p></div>', unsafe_allow_html=True)
with c4:
    v = float(dff["mobilisation_time_min"].median()) if "mobilisation_time_min" in dff else float("nan")
    st.markdown(f'<div class="kpi"><h3>Median mobilisation (min)</h3><p>{v:.1f}</p></div>', unsafe_allow_html=True)
with c5:
    v = float(dff["travel_time_min"].median()) if "travel_time_min" in dff else float("nan")
    st.markdown(f'<div class="kpi"><h3>Median travel (min)</h3><p>{v:.1f}</p></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.caption(f"Filtered rows: {len(dff):,}")

# -------- Tabs --------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Trends", "Boroughs", "Incident Types", "Time of Day", "Map", "Data & Methods"])

with tab1:
    st.subheader("Monthly trends")
    if "month" in dff and "IncidentNumber" in dff:
        monthly = dff.groupby("month", as_index=False).agg(
            incidents=("IncidentNumber","count"),
            median_response=("response_time_min","median")
        ).sort_values("month")
        st.line_chart(monthly.set_index("month")[["incidents"]])
        if "response_time_min" in dff:
            st.line_chart(monthly.set_index("month")[["median_response"]])

with tab2:
    st.subheader("Borough comparison")
    if "Borough" in dff and "response_time_min" in dff:
        by_b = dff.groupby("Borough", as_index=False).agg(
            incidents=("IncidentNumber","count"),
            median_response=("response_time_min","median"),
            p90_response=("response_time_min", lambda s: s.quantile(0.90))
        ).sort_values("median_response")
        st.bar_chart(by_b.set_index("Borough")[["median_response"]])
        st.dataframe(by_b, use_container_width=True)

with tab3:
    st.subheader("Incident group comparison")
    if "IncidentGroup" in dff and "response_time_min" in dff:
        by_t = dff.groupby("IncidentGroup", as_index=False).agg(
            incidents=("IncidentNumber","count"),
            median_response=("response_time_min","median"),
            p90_response=("response_time_min", lambda s: s.quantile(0.90))
        ).sort_values("median_response")
        st.bar_chart(by_t.set_index("IncidentGroup")[["median_response"]])
        st.dataframe(by_t, use_container_width=True)

with tab4:
    left, right = st.columns(2)
    with left:
        st.subheader("By hour of day")
        if "hour" in dff and "response_time_min" in dff:
            by_hour = dff.groupby("hour", as_index=False).agg(
                incidents=("IncidentNumber","count"),
                median_response=("response_time_min","median")
            ).sort_values("hour")
            st.bar_chart(by_hour.set_index("hour")[["median_response"]])
    with right:
        st.subheader("By day of week")
        if "dow" in dff and "response_time_min" in dff:
            order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
            by_dow = dff.groupby("dow", as_index=False).agg(
                incidents=("IncidentNumber","count"),
                median_response=("response_time_min","median")
            )
            if set(order).issuperset(set(by_dow["dow"])):
                by_dow["dow"] = pd.Categorical(by_dow["dow"], categories=order, ordered=True)
                by_dow = by_dow.sort_values("dow")
            st.bar_chart(by_dow.set_index("dow")[["median_response"]])

with tab5:
    st.subheader("Incident map (sampled)")
    lat_col, lon_col = detect_coord_columns(dff)
    if not (lat_col and lon_col):
        st.error("No coordinate columns found")
    else:
        coords = dff.rename(columns={lat_col:"lat", lon_col:"lon"}).copy()
        for c in ["lat","lon"]:
            coords[c] = coords[c].replace({"NULL": None, "null": None, "": None})
            coords[c] = pd.to_numeric(coords[c], errors="coerce")
        use_bbox = st.checkbox("Keep only points inside London bounding box", value=True, help="51.2 ≤ lat ≤ 51.8 and -0.6 ≤ lon ≤ 0.3")
        if use_bbox:
            coords = coords[(coords["lat"].between(51.2, 51.8)) & (coords["lon"].between(-0.6, 0.3))]
        pts = coords.dropna(subset=["lat","lon"])
        st.caption(f"Detected columns → latitude: **{lat_col}**, longitude: **{lon_col}** | Valid points: **{len(pts):,}/{len(coords):,}**")
        if len(pts) > 0:
            n = st.slider("Max points on map", 500, 20000, min(3000, len(pts)), 500)
            st.map(pts[["lat","lon"]].sample(min(n, len(pts)), random_state=0))
        else:
            st.warning("No usable coordinates after cleaning/filters; try turning off the bounding box.")

with tab6:
    st.subheader("Data & Methods")
    st.dataframe(dff.head(1000), use_container_width=True)
    st.download_button("Download filtered CSV", dff.to_csv(index=False), file_name="lfb_filtered.csv")
    st.divider()
    st.markdown("**Notes**: KPIs = Response (Arrival − Call), Mobilisation (Mobilised − Call), Travel (Arrival − Mobilised).")
