# streamlit_forecast_dashboard/app.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- CONFIG ---
st.set_page_config(page_title="EV Sales Forecast Dashboard", layout="wide")
st.markdown("""
<style>
    body {
        background-color: #f9f9f9;
    }
    .stApp {
        font-family: "Segoe UI", sans-serif;
    }
    .variant-label {
        font-weight: bold;
        color: #1a1a1a;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ SPECTRA: EV Sales Forecast Dashboard")
st.markdown("""
_Your configuration-driven sales planning tool._
""")

# --- LOAD FORECAST DATA ---
@st.cache_data
def load_data():
    # Replace with your actual published Google Sheets CSV link
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRY9MtX0JNjOesEkpkyAtul0Im5QEqoToHSvwQizL_oGVdR_uwXNXVVXIupg7BuhOwMiA3S0FCiHNEk/pub?gid=1300259633&single=true&output=csv"
    df = pd.read_csv(url)
    df['Month'] = pd.to_datetime(df['Month'])
    return df

try:
    df = load_data()
except:
    st.error("❌ Unable to load forecast data. Check your sheet link or publish settings.")
    st.stop()

# --- PREPROCESS ---
if 'Zone' not in df.columns:
    df['Zone'] = 'South'  # Default if missing

# Add India aggregate
df_india = df.copy()
df_india['Zone'] = 'India'
df = pd.concat([df, df_india], ignore_index=True)

# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.header("🎛️ Filters")
    zone = st.selectbox("Select Zone", sorted(df["Zone"].unique()))
    showroom = st.selectbox("Select Showroom", sorted(df[df['Zone'] == zone]["Showroom ID"].unique()))
    variant = st.selectbox("Select Variant", sorted(df[df['Zone'] == zone]["Variant"].unique()))
    show_table = st.checkbox("Show Forecast Table", value=True)

# --- FILTERED DATA ---
df_filtered = df[(df["Zone"] == zone) & (df["Showroom ID"] == showroom) & (df["Variant"] == variant)]
df_filtered = df_filtered.sort_values("Month")

# --- FAN CHART ---
st.subheader(f"📈 Forecast Fan Chart for {variant} at {showroom} ({zone})")
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_filtered['Month'], y=df_filtered['Forecast'], mode='lines+markers',
    name='Forecast', line=dict(color='#1f77b4', width=2)))
fig.add_trace(go.Scatter(
    x=df_filtered['Month'], y=df_filtered['Upper Bound'], mode='lines',
    name='Upper Bound', line=dict(color='rgba(255,215,0,0.5)'), showlegend=False))
fig.add_trace(go.Scatter(
    x=df_filtered['Month'], y=df_filtered['Lower Bound'], mode='lines',
    name='Lower Bound', fill='tonexty', line=dict(color='rgba(255,215,0,0.5)'),
    fillcolor='rgba(255,215,0,0.3)', showlegend=False))
fig.update_layout(
    xaxis_title="Month",
    yaxis_title="Units",
    template="simple_white",
    height=400,
    margin=dict(l=20, r=20, t=40, b=20),
    plot_bgcolor='white',
    paper_bgcolor='white'
)
st.plotly_chart(fig, use_container_width=True)

# --- FORECAST TABLE ---
if show_table:
    st.subheader("🔢 Forecast Table")
    st.dataframe(
        df_filtered[["Month", "Horizon", "Forecast", "Lower Bound", "Upper Bound", "Confidence Level", "Model Used"]]
        .set_index("Month")
    )

# --- FOOTER ---
st.markdown("""
---
⚙️ Powered by Streamlit · Configurable Model Engine (ElasticNet / LightGBM) · Visual Planning with Confidence Bands
""")
