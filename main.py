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
            "날짜": datetime.today().strftime("%Y-%m-%d %H:%M:%S")  # 날짜+시간
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

# --- 추천 도서 (이미지 포함) ---
st.subheader("🌟 이달의 추천 도서")

# 추천 도서 정보 (제목 + 이미지 URL)
recommended_books = [
    {"title": "마법천자문", "img": "https://i.namu.wiki/i/qsinpdBT8Ls2crMFWEDZzrIzEVyoMea7ZM7ZHK0hkNmdjgd_DZjTjpJNMM_rg7pGIMut8tM8wWCMN684LcEHPw.webp"},
    {"title": "수학도둑", "img": "https://image.aladin.co.kr/product/27949/91/cover500/k712830826_1.jpg"},
    {"title": "마틸다", "img": "https://image.aladin.co.kr/product/31562/21/cover500/8954670424_1.jpg"},
    {"title": "시간을 파는 상점", "img": "https://image.aladin.co.kr/product/3562/97/cover500/8954609544_1.jpg"},
    {"title": "완득이", "img": "https://image.aladin.co.kr/product/157/19/cover500/895460092X_1.jpg"}
]

# 도서 수만큼 컬럼 생성
cols = st.columns(len(recommended_books))

# 각 도서를 컬럼에 이미지+제목으로 출력
for idx, book in enumerate(recommended_books):
    with cols[idx]:
        st.image(book["img"], caption=book["title"], use_container_width=True)
