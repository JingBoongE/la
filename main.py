import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime

# --- 제목 정규화 함수 ---
def normalize_title(title):
    title = title.strip()               # 앞뒤 공백 제거
    title = ' '.join(title.split())    # 여러 공백을 한 칸 공백으로
    title = title.lower()               # 소문자 변환
    return title

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
        normalized_title = normalize_title(title)  # 제목 정규화
        date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('INSERT INTO books (title, rating, review, date) VALUES (?, ?, ?, ?)',
                  (normalized_title, rating, review, date))
        conn.commit()
        st.success(f"'{title}'을(를) 저장했어요!")

# --- DB에서 데이터 조회 ---
df_books = pd.read_sql_query('SELECT * FROM books', conn)

if not df_books.empty:
    st.subheader("📖 내가 읽은 책 목록")

# 삭제할 책 id 저장용 변수
delete_id = None

for idx, row in df_books.iterrows():
    cols = st.columns([4, 1])
    with cols[0]:
        st.write(f"{row['date']} - {row['title']} (⭐{row['rating']})")
    with cols[1]:
        if st.button("삭제", key=f"del_{row['id']}"):
            delete_id = row['id']

# 삭제 실행
if delete_id is not None:
    c.execute('DELETE FROM books WHERE id=?', (delete_id,))
    conn.commit()
    df_books = pd.read_sql_query('SELECT * FROM books', conn)
    st.success("책이 삭제되었어요!")

# 삭제 후 갱신된 데이터 출력
if not df_books.empty:
    st.dataframe(df_books[['date', 'title', 'rating', 'review']])
else:
    st.write("저장된 책이 없어요!")

# --- 시각화 ---
if not df_books.empty:
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
    "마법천자문": "https://i.namu.wiki/i/qsinpdBT8Ls2crMFWEDZzrIzEVyoMea7ZM7ZHK0hkNmdjgd_DZjTjpJNMM_rg7pGIMut8tM8wWCMN684LcEHPw.webp",
    "수학도둑": "https://i.namu.wiki/i/urnbnsfp-itJqnkcKuKEFy7bXIuj7qr3eDegTnSAZcAbVgPpHRk117iqWv59l7KePWyK-QxqSWhmA3VvDhfkkg.webp",
    "마틸다": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTANC5U88sj6OpjQL4CKZabDOwzNctJXNCFqg&s",
    "시간을 파는 상점": "https://image.yes24.com/Goods/6699994/XL",
    "완득이": "https://image.yes24.com/goods/2849279/XL"
}

if not df_top.empty and len(df_top) > 0:
    cols = st.columns(len(df_top))
    for idx, row in df_top.iterrows():
        with cols[idx]:
            img_url = book_images.get(row['title'])
            if img_url:
                st.image(img_url, caption=f"{row['title']} (⭐{row['rating']:.1f})", use_container_width=True)
            else:
                st.write(f"{row['title']} (⭐{row['rating']:.1f})")
else:
    st.info("추천할 책 데이터가 아직 없어요! 책을 추가해보세요!")
