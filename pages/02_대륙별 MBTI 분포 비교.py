import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="대륙별 MBTI 분포 비교", layout="wide")

# =========================
# 1) 제목 & 설명
# =========================
st.title("🌐 대륙별 MBTI 분포 비교")
st.caption("대륙별 평균 MBTI 분포를 계산하고 레이더 차트로 비교합니다.")

# =========================
# 2) 데이터 로드
# =========================
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

df = load_data("countriesMBTI_16types.csv")

mbti_cols = [c for c in df.columns if c != "Country"]

# =========================
# 3) 대륙 매핑 (간단 버전)
# =========================
continent_map = {
    # 아시아
    "Korea, South": "Asia", "Korea, North": "Asia", "Japan": "Asia",
    "China": "Asia", "India": "Asia", "Thailand": "Asia", "Vietnam": "Asia",
    "Indonesia": "Asia", "Philippines": "Asia", "Malaysia": "Asia", "Singapore": "Asia",
    "Mongolia": "Asia", "Kazakhstan": "Asia", "Uzbekistan": "Asia", "Pakistan": "Asia",
    "Bangladesh": "Asia", "Afghanistan": "Asia", "Nepal": "Asia", "Sri Lanka": "Asia",

    # 유럽
    "Germany": "Europe", "France": "Europe", "Italy": "Europe", "Spain": "Europe",
    "United Kingdom": "Europe", "Poland": "Europe", "Netherlands": "Europe", "Belgium": "Europe",
    "Sweden": "Europe", "Norway": "Europe", "Denmark": "Europe", "Finland": "Europe",
    "Czech Republic": "Europe", "Austria": "Europe", "Switzerland": "Europe", "Hungary": "Europe",
    "Portugal": "Europe", "Greece": "Europe", "Ireland": "Europe", "Russia": "Europe",

    # 아메리카
    "United States": "Americas", "Canada": "Americas", "Mexico": "Americas",
    "Brazil": "Americas", "Argentina": "Americas", "Chile": "Americas", "Colombia": "Americas",
    "Peru": "Americas", "Venezuela": "Americas", "Cuba": "Americas",

    # 아프리카
    "South Africa": "Africa", "Nigeria": "Africa", "Egypt": "Africa",
    "Kenya": "Africa", "Ethiopia": "Africa", "Morocco": "Africa",
    "Algeria": "Africa", "Ghana": "Africa",

    # 오세아니아
    "Australia": "Oceania", "New Zealand": "Oceania"
}

df["Continent"] = df["Country"].map(continent_map)
df = df.dropna(subset=["Continent"])  # 대륙 매핑되지 않은 국가 제거

# =========================
# 4) 대륙별 평균 계산
# =========================
continent_avg = df.groupby("Continent")[mbti_cols].mean().reset_index()

# =========================
# 5) 레이더 차트 (Plotly)
# =========================
st.subheader("📊 대륙별 MBTI 평균 분포 (레이더 차트)")

fig = px.line_polar(
    continent_avg.melt(id_vars=["Continent"], var_name="MBTI", value_name="Value"),
    r="Value",
    theta="MBTI",
    color="Continent",
    line_close=True,
    markers=True
)

fig.update_traces(fill="toself", opacity=0.6)
fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, tickformat=".0%")),
    legend_title="대륙",
    margin=dict(l=20, r=20, t=40, b=20)
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# 6) 표 출력
# =========================
st.subheader("📋 대륙별 MBTI 평균값 (일부 소수점)")
st.dataframe(continent_avg.set_index("Continent").round(3))

