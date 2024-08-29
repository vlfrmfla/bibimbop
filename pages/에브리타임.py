import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(layout="wide")

# JSON 파일 경로
json_file_path = "./anonymous_board.json"

# JSON 파일에서 데이터를 읽어오는 함수
def load_data():
    if os.path.exists(json_file_path):
        with open(json_file_path, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []  # JSON 파일이 비어 있거나 잘못된 형식인 경우 빈 리스트 반환
    else:
        return []

# JSON 파일에 데이터를 저장하는 함수
def save_data(data):
    with open(json_file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# 게시글 데이터 로드
posts = load_data()

# 게시글 추가 함수
def add_post(author, content, password):
    post = {
        "author": author,
        "content": content,
        "password": password,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    posts.append(post)
    save_data(posts)

# 게시글 수정 함수
def edit_post(index, new_content, password):
    if posts[index]["password"] == password:
        posts[index]["content"] = new_content
        posts[index]["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S (수정됨)")
        save_data(posts)
        return True
    else:
        return False

# 게시글 삭제 함수
def delete_post(index, password):
    if posts[index]["password"] == password:
        posts.pop(index)
        save_data(posts)
        return True
    else:
        return False

# Streamlit 페이지 레이아웃 설정
st.title("익명 게시판")

# 페이지 초기화 시 세션 상태 설정
if 'update' not in st.session_state:
    st.session_state.update = False

# 게시글 작성 섹션
st.subheader("📌 글쓰기")

with st.form(key="write_form"):
    author = st.text_input("작성자", "익명")
    content = st.text_area("내용")
    password = st.text_input("비밀번호", type="password")
    submit_button = st.form_submit_button(label="글 작성")

if submit_button:
    if content and password:
        add_post(author, content, password)
        st.success("글이 작성되었습니다!")
        st.session_state.update = not st.session_state.update  # 세션 상태를 변경하여 페이지 업데이트 트리거
        st.experimental_set_query_params(update=st.session_state.update)  # 페이지를 새로고침하지 않고 업데이트

# 게시글 목록 표시
st.subheader("📋 글 목록")

if posts:
    for index, post in enumerate(posts):
        st.markdown(f"**작성자**: {post['author']}  \n**날짜**: {post['date']}  \n**내용**: {post['content']}")
        with st.expander("수정/삭제"):
            new_content = st.text_area("수정할 내용", post["content"], key=f"edit_content_{index}")
            edit_password = st.text_input("비밀번호 입력", type="password", key=f"edit_password_{index}")
            edit_button = st.button("수정", key=f"edit_button_{index}")
            delete_button = st.button("삭제", key=f"delete_button_{index}")

            if edit_button:
                if edit_post(index, new_content, edit_password):
                    st.success("글이 수정되었습니다!")
                    st.session_state.update = not st.session_state.update  # 세션 상태를 변경하여 페이지 업데이트 트리거
                    st.experimental_set_query_params(update=st.session_state.update)
                else:
                    st.error("비밀번호가 틀렸습니다.")

            if delete_button:
                if delete_post(index, edit_password):
                    st.success("글이 삭제되었습니다!")
                    st.session_state.update = not st.session_state.update  # 세션 상태를 변경하여 페이지 업데이트 트리거
                    st.experimental_set_query_params(update=st.session_state.update)
                else:
                    st.error("비밀번호가 틀렸습니다.")
else:
    st.info("아직 작성된 글이 없습니다.")
