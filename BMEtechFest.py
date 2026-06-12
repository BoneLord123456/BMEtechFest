import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import gspread

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Sensor Dashboard",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st_autorefresh(interval=10000, key="sensor_refresh")

hex_code = "20252e"



# ==========================================
# CUSTOM CSS
# ==========================================
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Page background: soft blue-gray so white cards pop ── */
    [data-testid="stAppViewContainer"] {
        background-color: #{hex_code} !important;
    }

    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* ── Metric cards: light gray surface ── */
    [data-testid="metric-container"] {
        background: #F1F5F9 !important;
        border-radius: 18px !important;
        padding: 22px 26px !important;
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.09) !important;
        border: 1px solid #E2E8F0 !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 11px !important;
        color: #64748B !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.2px !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 36px !important;
        color: #0F172A !important;
        font-weight: 900 !important;
    }

    [data-testid="stMetricDelta"] {
        font-size: 13px !important;
        font-weight: 600 !important;
    }

    /* ── Divider ── */
    hr {
        border: none !important;
        border-top: 2px solid #DDE4EE !important;
        margin: 1.5rem 0 2rem 0 !important;
    }

    /* ── Round chart cards ── */
    [data-testid="stPlotlyChart"] > div {
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.08) !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# DATA FETCHING
# ==========================================
sheet_id = "1vQbudVJ-6Ojjn5JJG2NjAlxePPR_GOBJ6JkoSJO_Ogk"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
url2 = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=1924829800"

try:
    df = pd.read_csv(url)
    df2=pd.read_csv(url2,header=None)
except Exception as e:
    st.error("Failed to load data. Please check the Google Sheet connection.")
    st.stop()

if df.empty:
    st.warning("Waiting for sensor data...")
    st.stop()

df["TimeStamp"] = pd.to_datetime(df["TimeStamp"])

if len(df) < 2:
    difference1 = difference2 = difference3 = difference4 = 0.0
else:
    difference1 = df["TempScore"].iloc[-1]     - df["TempScore"].iloc[-2]
    difference2 = df["HumidityScore"].iloc[-1] - df["HumidityScore"].iloc[-2]
    difference3 = df["SoundScore"].iloc[-1]    - df["SoundScore"].iloc[-2]
    difference4 = df["LightScore"].iloc[-1]    - df["LightScore"].iloc[-2]

current_temp     = df["TempScore"].iloc[-1]
current_humidity = df["HumidityScore"].iloc[-1]
current_sound    = df["SoundScore"].iloc[-1]
current_light    = df["LightScore"].iloc[-1]
current_pcs      = df["PCS"].iloc[-1]
current_status   = df["Status"].iloc[-1]
current_advisory = df["Advisory"].iloc[-1]

iTemp=df2.iloc[0,1]
iHum=df2.iloc[1,1]
iLight=df2.iloc[2,1]
iSound=df2.iloc[3,1]

# ==========================================
# HEADER BANNER
# ==========================================
st.markdown("""
<div style="
    display: flex;
    align-items: center;
    gap: 18px;
    background: #FFFFFF;
    padding: 20px 28px;
    border-radius: 20px;
    box-shadow: 0 2px 16px rgba(15,23,42,0.08);
    border: 1px solid #E2E8F0;
    margin-bottom: 28px;
">
    <span style="font-size: 40px;">📡</span>
    <div>
        <h1 style="color:#0F172A; font-weight:900; margin:0; font-size:26px; line-height:1.1;">
            Sensor Dashboard
        </h1>
        <p style="color:#94A3B8; margin:5px 0 0 0; font-size:13px; font-weight:500;">
            Live environmental monitoring &nbsp;·&nbsp; Auto-refreshes every 10 seconds
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# TOP ROW: METRIC CARDS
# ==========================================

cola,colm1,colb=st.columns([3,1,3])
with cola:
    col1, col2 = st.columns(2)
    col1.metric("🌡️ Temperature",    f"{current_temp}",     f"{difference1:.2f}")
    col2.metric(f"Recommended Change",f"{iTemp-current_temp:.2f}")
with colm1:
    st.metric("\t","\t")
with colb:
    col3, col4 = st.columns(2)
    col3.metric("💧 Humidity",        f"{current_humidity}", f"{difference2:.2f}")
    col4.metric(f"Recommended Change",f"{iHum-current_humidity:.2f}")
colc,colm2,cold=st.columns([3,1,3])
with colc:
    col5,col6 = st.columns(2)
    col5.metric("🔊 Sound Level",     f"{current_sound}",    f"{difference3:.2f}")
    col6.metric(f"Recommended Change",f"{iSound-current_sound:.2f}")
with colm2:
    st.metric("\t","\t")
with cold:
    col7,col8 = st.columns(2)
    col7.metric("☀️ Light Intensity", f"{current_light}",    f"{difference4:.2f}")
    col8.metric(f"Recommended Change",f"{iLight-current_light:.2f}")


st.divider()

# ==========================================
# CHART BUILDER — light gray bg, black labels
# ==========================================
def create_styled_chart(data, x_col, y_col, title, line_color, fill_color):
    fig = px.area(data, x=x_col, y=y_col, hover_data=["PCS", "Advisory", "Status"])

    fig.update_traces(
        line=dict(color=line_color, width=2.5),
        fillcolor=fill_color
    )

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=15, color="#0F172A", family="Inter"),
            x=0.04,
            y=0.95
        ),
        # ── Light gray for the data area, white for the card surround ──
        plot_bgcolor="#F1F5F9",
        paper_bgcolor="#FFFFFF",
        font=dict(family="Inter", color="#0F172A", size=11),
        margin=dict(l=54, r=20, t=68, b=50),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            title="",
            tickfont=dict(color="#0F172A", size=10, family="Inter"),
            linecolor="#CBD5E1",
            tickcolor="#CBD5E1",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#E2E8F0",
            zeroline=False,
            title="",
            tickfont=dict(color="#0F172A", size=10, family="Inter"),
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="#E2E8F0",
            font_size=12,
            font_family="Inter",
            font_color="#0F172A"
        )
    )
    return fig

fig1 = create_styled_chart(df, "TimeStamp", "TempScore",     "🌡️ Temperature Trend",    "#EF4444", "rgba(239,68,68,0.18)")
fig2 = create_styled_chart(df, "TimeStamp", "HumidityScore", "💧 Humidity Trend",        "#3B82F6", "rgba(59,130,246,0.18)")
fig3 = create_styled_chart(df, "TimeStamp", "SoundScore",    "🔊 Noise Level Trend",     "#8B5CF6", "rgba(139,92,246,0.18)")
fig4 = create_styled_chart(df, "TimeStamp", "LightScore",    "☀️ Light Intensity Trend", "#F59E0B", "rgba(245,158,11,0.18)")

# ==========================================
# MAIN LAYOUT: CHARTS (LEFT) + STATUS (RIGHT)
# ==========================================
left_col, right_col = st.columns([3, 1], gap="large")

with left_col:
    col_g1, col_g2 = st.columns(2)
    with col_g1: st.plotly_chart(fig1, use_container_width=True)
    with col_g2: st.plotly_chart(fig2, use_container_width=True)

    st.write("")

    col_g3, col_g4 = st.columns(2)
    with col_g3: st.plotly_chart(fig3, use_container_width=True)
    with col_g4: st.plotly_chart(fig4, use_container_width=True)

# ==========================================
# RIGHT COLUMN: SYSTEM OVERVIEW CARDS
# ==========================================
with right_col:
    st.markdown(
        "<h3 style='color:#0F172A; font-weight:900; font-size:20px;"
        " margin-bottom:22px;'>🖥️ System Overview</h3>",
        unsafe_allow_html=True
    )

    is_safe      = current_pcs > 1
    zone_text    = "Safe Zone" if is_safe else "Danger Zone"
    status_icon  = "✅" if is_safe else "🚨"

    # ── Each card gets its own distinct vivid gradient ──
    status_grad  = (
        "linear-gradient(135deg, #10B981 0%, #059669 100%)"
        if is_safe else
        "linear-gradient(135deg, #EF4444 0%, #B91C1C 100%)"
    )
    advisory_grad = "linear-gradient(135deg, #6366F1 0%, #4338CA 100%)"
    pcs_grad      = (
        "linear-gradient(135deg, #0EA5E9 0%, #0369A1 100%)"
        if is_safe else
        "linear-gradient(135deg, #F97316 0%, #C2410C 100%)"
    )

    # ── Card builder: fully single-line HTML, no comments, no multi-line style attrs ──
    def overview_card(label, value_html, gradient):
        outer = f'<div style="background:{gradient};padding:28px 24px;border-radius:22px;margin-bottom:18px;box-shadow:0 16px 36px rgba(0,0,0,0.22);color:white;position:relative;overflow:hidden;">'
        blob1 = '<div style="position:absolute;top:-28px;right:-28px;width:100px;height:100px;background:rgba(255,255,255,0.14);border-radius:50%;"></div>'
        blob2 = '<div style="position:absolute;bottom:-40px;right:10px;width:130px;height:130px;background:rgba(255,255,255,0.07);border-radius:50%;"></div>'
        lbl   = f'<p style="margin:0 0 10px 0;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:2px;opacity:0.82;">{label}</p>'
        val   = f'<div style="font-size:22px;font-weight:800;line-height:1.45;position:relative;z-index:1;">{value_html}</div>'
        return outer + blob1 + blob2 + lbl + val + '</div>'

    pcs_value = (
        f'<span style="font-size:32px;font-weight:900;">{current_pcs}</span>'
        f'<div style="font-size:14px;font-weight:600;opacity:0.88;margin-top:6px;">{zone_text}</div>'
    )

    st.markdown(overview_card("● Current Status",  f"{status_icon} {current_status}", status_grad),   unsafe_allow_html=True)
    st.markdown(overview_card("◈ Active Advisory", current_advisory,                  advisory_grad), unsafe_allow_html=True)
    st.markdown(overview_card("◎ PCS Index",        pcs_value,                        pcs_grad),      unsafe_allow_html=True)

    temp=st.number_input(label="Set Ideal Temperature",value=iTemp)
    hum=st.number_input(label="Set Ideal Humidity",value=iHum)
    light=st.number_input(label="Set Ideal Light",value=iLight)
    sound=st.number_input(label="Set Ideal Sound",value=iSound)

    gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])

    sheet = gc.open_by_key("1vQbudVJ-6Ojjn5JJG2NjAlxePPR_GOBJ6JkoSJO_Ogk")

    config = sheet.worksheet("Config")

    config.update("B1", [[temp]])
    config.update("B2", [[hum]])
    config.update("B3", [[light]])
    config.update("B4", [[sound]])
    # df2.iloc[0,1]=temp
    # df2.iloc[1,1]=hum
    # df2.iloc[2,1]=light
    # df2.iloc[3,1]=sound
