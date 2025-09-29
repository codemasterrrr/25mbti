# 00은 페이지의 위치를 결정하는 것
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="MBTI 상위 10개국 시각화", layout="wide")

# 제목 & 설명
st.title("🌍 MBTI 상위 10개국 시각화")
st.caption("원하는 MBTI 유형을 선택하면, 해당 유형 비율이 높은 상위 10개 국가를 막대 그래프로 보여줍니다.")

# 데이터 로드 (캐시)
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

df = load_data("countriesMBTI_16types.csv")

# MBTI 열 목록 확인
mbti_cols = [c for c in df.columns if c != "Country"]
if not mbti_cols:
    st.error("MBTI 열을 찾을 수 없습니다. 'Country'를 제외한 16개 MBTI 열이 있어야 합니다.")
    st.stop()

# 사이드바: MBTI 선택
st.sidebar.header("⚙️ 설정")
selected = st.sidebar.selectbox("분석할 MBTI 유형을 선택하세요:", sorted(mbti_cols))

# 상위 10개 추출
top10 = (
    df.loc[:, ["Country", selected]]
      .nlargest(10, selected)
      .rename(columns={selected: "Value"})
      .reset_index(drop=True)
)

# 안내
st.subheader(f"👀 선택한 유형: **{selected}** — 상위 10개 국가")
st.caption("막대 그래프는 비율(0~1)을 %로 표현합니다.")

# Altair 차트 (가로형 막대)
chart = (
    alt.Chart(top10)
    .mark_bar()
    .encode(
        x=alt.X("Value:Q", title="비율", axis=alt.Axis(format=".0%")),
        y=alt.Y("Country:N", sort="-x", title="국가"),
        tooltip=[
            alt.Tooltip("Country:N", title="국가"),
            alt.Tooltip("Value:Q", title="비율", format=".2%")
        ]
    )
    .properties(
        title=f"🏆 {selected} 비율 상위 10개 국가",
        width=800,
        height=420
    )
)

st.altair_chart(chart, use_container_width=True)

# 표도 함께 표시
st.subheader("📋 데이터(상위 10)")
st.dataframe(
    top10.assign(**{"비율(%)": (top10["Value"] * 100).round(2)})
         .drop(columns=["Value"])
)
st.info("✨ 팁: 사이드바에서 MBTI 유형을 바꾸면 그래프와 표가 함께 갱신됩니다!")
