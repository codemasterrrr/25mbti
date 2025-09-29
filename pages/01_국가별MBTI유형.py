import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="MBTI 국가별 분포", layout="wide")

# =========================
# 1) 제목 & 안내
# =========================
st.title("🌏 국가 선택 → MBTI 분포 보기")
st.caption("나라를 고르면 해당 국가의 16개 MBTI 유형 비율을 예쁘게 시각화합니다. (값은 0~1 사이 비율)")

# =========================
# 2) 데이터 로드
# =========================
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

df = load_data("countriesMBTI_16types.csv")

# 기본 컬럼 체크
if "Country" not in df.columns:
    st.error("데이터에 'Country' 컬럼이 없습니다. CSV를 확인해주세요.")
    st.stop()

mbti_cols = [c for c in df.columns if c != "Country"]
if len(mbti_cols) != 16:
    st.warning(f"MBTI 컬럼 수가 16개가 아닙니다. 현재 {len(mbti_cols)}개가 감지되었습니다.")

# =========================
# 3) 사이드바: 국가 선택
# =========================
st.sidebar.header("🎛️ 설정")
countries = df["Country"].dropna().sort_values().tolist()
default_idx = countries.index("Korea, South") if "Korea, South" in countries else 0
selected_country = st.sidebar.selectbox("국가를 선택하세요:", countries, index=default_idx)

# =========================
# 4) 선택 국가의 데이터 추출/정리
# =========================
row = df.loc[df["Country"] == selected_country, mbti_cols]
if row.empty:
    st.error("해당 국가 데이터를 찾을 수 없습니다.")
    st.stop()

series = row.iloc[0].copy()
country_df = (
    series.reset_index()
          .rename(columns={"index": "MBTI", 0: "Value"})
          .sort_values("Value", ascending=False)
          .reset_index(drop=True)
)

# =========================
# 5) 색상 팔레트 설정 (센스있게 ✨)
#    - Set3 계열의 부드러운 파스텔톤
# =========================
palette = px.colors.qualitative.Set3
# 그래도 16개 MBTI 전용으로 길이를 맞춰줍니다 (부족하면 반복)
while len(palette) < len(country_df):
    palette = palette + palette

# =========================
# 6) 그래프: 가로형 막대 (값은 %로 라벨/툴팁)
# =========================
st.subheader(f"🧠 {selected_country}의 MBTI 분포 (상위→하위)")
fig = px.bar(
    country_df,
    x="Value",
    y="MBTI",
    orientation="h",
    color="MBTI",
    color_discrete_sequence=palette[: len(country_df)],
    hover_data={"Value": ":.2%"},
)

fig.update_layout(
    xaxis_title="비율 (%)",
    yaxis_title="MBTI 유형",
    legend_title="MBTI",
    margin=dict(l=10, r=10, t=40, b=10),
)
fig.update_xaxes(tickformat=".0%")

st.plotly_chart(fig, use_container_width=True)

# =========================
# 7) 표: % 컬럼 함께 제공
# =========================
st.subheader("📋 데이터")
show_pct = country_df.assign(**{"비율(%)": (country_df["Value"] * 100).round(2)})
st.dataframe(show_pct[["MBTI", "비율(%)"]], use_container_width=True)

# =========================
# 8) 작은 팁
# =========================
st.info("✨ 팁: 사이드바에서 국가를 바꾸면 그래프와 표가 함께 갱신됩니다!")
