import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="MBTI 상위 10개국 (Altair)", layout="wide")

# 제목 & 설명
st.title("🌍 MBTI 상위 10개국 — Altair (세로 막대)")
st.caption("아래에서 MBTI 유형을 선택하면, 해당 유형 비율이 높은 상위 10개 국가를 세로 막대그래프로 표시합니다. (값은 0~1 비율)")

# 데이터 로드 (캐시)
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

df = load_data("countriesMBTI_16types.csv")

# 기본 컬럼 점검
if "Country" not in df.columns:
    st.error("데이터에 'Country' 컬럼이 없습니다. CSV를 확인해주세요.")
    st.stop()

mbti_cols = [c for c in df.columns if c != "Country"]

# 본문에서 MBTI 순서대로 선택 (ISTJ → … → ENTJ)
MBTI_ORDER = ["ISTJ","ISFJ","INFJ","INTJ","ISTP","ISFP","INFP","INTP",
              "ESTP","ESFP","ENFP","ENTP","ESTJ","ESFJ","ENFJ","ENTJ"]
ordered_mbti = [t for t in MBTI_ORDER if t in mbti_cols]  # 데이터에 있는 것만 사용

st.subheader("🎛️ MBTI 유형 선택")
default_idx = ordered_mbti.index("INFJ") if "INFJ" in ordered_mbti else 0
selected = st.selectbox("분석할 MBTI 유형을 선택하세요:", ordered_mbti, index=default_idx)

st.divider()

# 상위 10개 국가 추출
top10 = (
    df.loc[:, ["Country", selected]]
      .nlargest(10, selected)
      .rename(columns={selected: "Value"})
      .reset_index(drop=True)
)

# 세로형 막대그래프 (x=Country, y=Value), 값 기준 내림차순 정렬
st.subheader(f"📊 {selected} 비율 상위 10개 국가 (세로)")
chart = (
    alt.Chart(top10)
    .mark_bar()
    .encode(
        x=alt.X("Country:N", sort="-y", title="국가"),
        y=alt.Y("Value:Q", axis=alt.Axis(format=".0%"), title="비율"),
        tooltip=[
            alt.Tooltip("Country:N", title="국가"),
            alt.Tooltip("Value:Q", title="비율", format=".2%")
        ]
    )
    .properties(
        title=f"🏆 {selected} 상위 10개국",
        width=800,
        height=450
    )
)

st.altair_chart(chart, use_container_width=True)

# 표도 함께 표시
st.subheader("📋 데이터(상위 10)")
st.dataframe(
    top10.assign(**{"비율(%)": (top10["Value"] * 100).round(2)})[["Country", "비율(%)"]],
    use_container_width=True
)

st.info("✨ 팁: 위의 드롭다운에서 MBTI 유형을 바꾸면 그래프와 표가 같이 갱신됩니다!")
