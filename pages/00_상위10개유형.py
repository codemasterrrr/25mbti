import streamlit as st
import pandas as pd
import altair as alt
import re

st.set_page_config(page_title="MBTI 상위 10개국 — Altair(세로/약어)", layout="wide")

# 제목 & 설명
st.title("🌍 MBTI 상위 10개국 — 세로 막대 + 국가 약어")
st.caption("MBTI 유형을 고르면 해당 유형 비율 상위 10개 국가를 예쁜 색상으로 시각화합니다. 막대 아래 라벨은 읽기 쉬운 약어(Abbr)로 표시됩니다. (값: 0~1 비율)")

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

# -------- 국가 약어 생성 로직 --------
ABBR_OVERRIDES = {
    "Korea, South": "KOR",
    "Korea, North": "PRK",
    "United States": "USA",
    "United Kingdom": "UK",
    "United Arab Emirates": "UAE",
    "Czech Republic": "CZE",
    "Czechia": "CZE",
    "Côte d’Ivoire": "CIV",
    "Cote d'Ivoire": "CIV",
    "Russian Federation": "RUS",
    "Democratic Republic of the Congo": "DRC",
    "Congo, Democratic Republic of the": "DRC",
    "Republic of the Congo": "ROC",
    "Congo, Republic of the": "ROC",
}

def make_abbr(name: str) -> str:
    if name in ABBR_OVERRIDES:
        return ABBR_OVERRIDES[name]
    words = re.findall(r"[A-Za-z]+", name)
    if not words:
        return name[:3].upper()
    if len(words) == 1:
        return words[0][:3].upper()
    # 여러 단어면 이니셜로 2~3글자
    initials = "".join(w[0] for w in words).upper()
    if len(initials) >= 2:
        return initials[:3]
    # 그래도 부족하면 앞에서 3글자
    return "".join(words)[:3].upper()

# 중복 약어 방지: 충돌시 숫자 suffix 부여
def make_unique_abbrs(names: list[str]) -> list[str]:
    seen = {}
    result = []
    for nm in names:
        base = make_abbr(nm)
        ab = base
        k = 1
        while ab in seen:
            ab = f"{base}{k}"
            k += 1
        seen[ab] = True
        result.append(ab)
    return result

top10["Abbr"] = make_unique_abbrs(top10["Country"].tolist())

# 값 기준 내림차순 정렬
top10 = top10.sort_values("Value", ascending=False).reset_index(drop=True)

# -------- Altair 차트 (세로 막대 + 예쁜 팔레트 + 약어 라벨) --------
st.subheader(f"📊 {selected} 비율 상위 10개 국가 (세로 · 약어 라벨)")

base = alt.Chart(top10)

bars = base.mark_bar().encode(
    x=alt.X(
        "Abbr:N",
        sort="-y",
        title="국가(약어)",
        axis=alt.Axis(labelAngle=0, labelLimit=0, labelPadding=6)  # 약어를 수평 표시
    ),
    y=alt.Y("Value:Q", title="비율", axis=alt.Axis(format=".0%")),
    color=alt.Color(
        "Abbr:N",
        legend=None,  # 범례 숨김 (아래 라벨로 충분)
        scale=alt.Scale(scheme="tableau10")  # 예쁜 10색 팔레트
    ),
    tooltip=[
        alt.Tooltip("Country:N", title="국가(전체명)"),
        alt.Tooltip("Abbr:N", title="약어"),
        alt.Tooltip("Value:Q", title="비율", format=".2%")
    ]
)

# 막대 위 % 라벨
labels = base.mark_text(dy=-6).encode(
    x=alt.X("Abbr:N", sort="-y"),
    y=alt.Y("Value:Q"),
    text=alt.Text("Value:Q", format=".0%"),
    color=alt.value("#333")  # 라벨 색(가독성)
)

chart = (bars + labels).properties(
    width=800,
    height=450,
    title=f"🏆 {selected} 비율 상위 10개 — 약어 라벨"
)

st.altair_chart(chart, use_container_width=True)

# 표도 함께 표시: 약어/원래 국가명/비율(%)
st.subheader("📋 데이터(상위 10): 약어 ↔ 원래 국가명")
st.dataframe(
    top10.assign(**{"비율(%)": (top10["Value"] * 100).round(2)})[["Abbr", "Country", "비율(%)"]],
    use_container_width=True
)

st.info("✨ 팁: 위 드롭다운에서 MBTI 유형을 바꾸면 그래프와 표가 함께 갱신됩니다. (막대 아래 라벨은 약어, 툴팁과 표에서 전체 국가명을 확인하세요.)")
