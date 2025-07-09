import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="초등학생 독서 장려 웹", page_icon="📚", layout="wide")

st.title("📚 초등학생 독서 장려 웹")
st.write("책을 읽고 기록하며, 추천도서를 확인하고 나의 독서 활동을 시각화해보세요!")

# 세션 상태에 책 목록 저장
if 'books' not in st.session_state:
    st.session_state['books'] = []

# --- 데이터 입력 ---
with st.form("book_form"):
    st.subheader("✅ 읽은 책 입력하기")
    title = st.text_input("책 제목")
    rating = st.slider("별점", 1, 5, 3)
    review = st.text_area("간단한 감상")
    submitted = st.form_submit_button("저장하기")
    if submitted and title:
        st.session_state['books'].append({
            "제목": title,
            "별점": rating,
            "감상": review,
            "날짜": datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        })
        st.success(f"'{title}'을(를) 저장했어요!")

# --- 읽은 책 목록 표시 ---
if st.session_state['books']:
    st.subheader("📖 내가 읽은 책 목록")
    df_books = pd.DataFrame(st.session_state['books'])
    st.dataframe(df_books[['날짜', '제목', '별점', '감상']])

    # --- 시각화 ---
    st.subheader("📊 독서 활동 시각화")
    df_books['날짜'] = pd.to_datetime(df_books['날짜'])
    df_count = df_books.groupby(df_books['날짜'].dt.to_period('M')).size().reset_index(name='읽은 권수')
    df_count['날짜'] = df_count['날짜'].astype(str)

    fig = px.bar(df_count, x='날짜', y='읽은 권수',
                 labels={'날짜': '월', '읽은 권수': '읽은 책 수'},
                 title="월별 읽은 책 수")
    st.plotly_chart(fig, use_container_width=True)

# --- 추천 도서 ---
st.subheader("🌟 추천 도서")
recommended_books = [
    "마법천자문",
    "수학도둑",
    "마틸다",
    "시간을 파는 상점",
    "완득이"
]
st.write(", ".join(recommended_books))
