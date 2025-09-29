import streamlit as st
import pandas as pd

# 앱 제목
st.title("🌍 MBTI 국가별 데이터 미리보기")

# CSV 파일 불러오기(같은 폴더에 있는 경우)
df = pd.read_csv("countriesMBTI_16types.csv")

# 데이퍼 프레임 상위 5줄 출력
st.subheader("👀 데이터 상위 5행")
st.dataframe(df.head())

# 간단한 안내 메시지
st.info("✨ 위 표는 업로드된 데이터의 앞부분만 보여줍니다!")

