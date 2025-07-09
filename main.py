import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime

# DB 연결
conn = sqlite3.connect('books.db', check_same_thread=False)
c = conn.cursor()

# 테이블 생성
c.execute('''
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    rating INTEGER,
    review TEXT,
    date TEXT
)
''')
conn.commit()

st.title("📚 초등학생 독서 장려 웹")

# --- 데이터 입력 ---
with st.form("book_form"):
    st.subheader("✅ 읽은 책 입력하기")
    title = st.text_input("책 제목")
    rating = st.slider("별점", 1, 5, 3)
    review = st.text_area("간단한 감상")
    submitted = st.form_submit_button("저장하기")
    if submitted and title:
        date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('INSERT INTO books (title, rating, review, date) VALUES (?, ?, ?, ?)',
                  (title, rating, review, date))
        conn.commit()
        st.success(f"'{title}'을(를) 저장했어요!")

# --- DB에서 데이터 조회 ---
df_books = pd.read_sql_query('SELECT * FROM books', conn)

if not df_books.empty:
    st.subheader("📖 내가 읽은 책 목록")
    st.dataframe(df_books[['date', 'title', 'rating', 'review']])

    # --- 시각화 ---
    st.subheader("📊 독서 활동 시각화")
    df_books['date'] = pd.to_datetime(df_books['date'])
    df_count = df_books.groupby(df_books['date'].dt.to_period('M')).size().reset_index(name='읽은 권수')
    df_count['date'] = df_count['date'].astype(str)

    fig = px.bar(df_count, x='date', y='읽은 권수',
                 labels={'date': '월', '읽은 권수': '읽은 책 수'},
                 title="월별 읽은 책 수")
    st.plotly_chart(fig, use_container_width=True)

# --- 평점 기준 추천 도서 ---
st.subheader("🌟 평점 TOP 5 추천 도서")

# 제목별 평균 평점 계산
df_top = df_books.groupby('title')['rating'].mean().reset_index()
df_top = df_top.sort_values(by='rating', ascending=False).head(5)

# 이미지 매핑 (예시)
book_images = {
    "마법천자문": "https://image.aladin.co.kr/product/30223/5/cover500/k712837713_1.jpg",
    "수학도둑": "https://image.aladin.co.kr/product/27949/91/cover500/k712830826_1.jpg",
    "마틸다": "https://image.aladin.co.kr/product/31562/21/cover500/8954670424_1.jpg",
    "시간을 파는 상점": "https://image.aladin.co.kr/product/3562/97/cover500/8954609544_1.jpg",
    "완득이": "https://image.aladin.co.kr/product/157/19/cover500/895460092X_1.jpg"
}

cols = st.columns(len(df_top))
for idx, row in df_top.iterrows():
    with cols[idx]:
        img_url = book_images.get(row['title'], None)
        if img_url:
            st.image(img_url, caption=f"{row['title']} (⭐{row['rating']:.1f})", use_container_width=True)
        else:
            st.write(f"{row['title']} (⭐{row['rating']:.1f})")

