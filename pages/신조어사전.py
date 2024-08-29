import streamlit as st
import json
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import hgtk
import requests


st.set_page_config(layout="wide")

# JSON 파일 경로
json_file_path = "./new_words.json"

# JSON 파일에서 데이터를 읽어오는 함수
def load_data():
    try:
        with open(json_file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# JSON 파일에 데이터를 저장하는 함수
def save_data(data):
    with open(json_file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# 초성 분리 함수
def extract_initials(word):
    initials = []
    for char in word:
        if hgtk.checker.is_hangul(char):
            try:
                initial = hgtk.letter.decompose(char)[0]
                initials.append(initial)
            except hgtk.exception.NotHangulException:
                initials.append(char)
        else:
            initials.append(char)
    return ''.join(initials)

# 신조어 데이터 로드
new_words_dict = load_data()

# 페이지 자동 새로 고침 설정 (3초마다 새로 고침)
count = st_autorefresh(interval=3000, limit=None, key="fizzbuzzcounter")

# Streamlit 제목 설정
st.title("📝 신조어 사전")

# 세션 상태 초기화
if 'index' not in st.session_state:
    st.session_state.index = 0

# 신조어 슬라이드 애니메이션 효과
words = list(new_words_dict.items())
if words:
    display_slot = st.empty()

    # 현재 인덱스에 따라 신조어 표시
    current_batch = words[st.session_state.index:st.session_state.index + 5]
    st.session_state.index = (st.session_state.index + 5) % len(words)

    # 전체 목록을 하나의 둥근 테두리로 묶기 위한 스타일
    rounded_box_style = """
    <style>
    .rounded-box {
        border: 2px solid #ddd;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 20px;
        background-color: white;
        color: black;
    }
    .rounded-box p {
        margin: 0;
        padding: 0;
    }
    </style>
    """
    st.markdown(rounded_box_style, unsafe_allow_html=True)

    # 신조어 목록 전체를 하나의 둥근 테두리로 묶음
    with display_slot.container():
        html_content = '<div class="rounded-box">'
        for word, info in current_batch:
            html_content += f"<p><strong>{word}</strong>: {info['definition']} (추가된 날짜: {info['date']})</p>"
        html_content += '</div>'
        st.markdown(html_content, unsafe_allow_html=True)
else:
    st.write("사전에 신조어가 없습니다.")
# 신조어 검색 기능
search_word = st.text_input("🔍 신조어 검색 (초성 및 일반 검색 지원)", "")

# 고정된 유튜브 링크 딕셔너리 (키워드와 유튜브 링크 매칭)
fixed_youtube_links = {
    "갓띵작": "https://youtube.com/shorts/fszBquMocC4?si=d2gSp2eZ5xzvHHs0",
    "추구미": "https://youtube.com/shorts/drUgTiltRpw?si=xGhIyyXRsIqycdXM"
    # 여기에 추가적인 키워드와 링크를 넣으세요
}

# 추천 검색어 업데이트
if search_word:
    # 초성으로 검색
    initial_search_results = {word: info for word, info in new_words_dict.items() if extract_initials(word).startswith(search_word)}

    # 일반 검색
    general_search_results = {word: info for word, info in new_words_dict.items() if search_word in word}

    # 추천 검색 목록
    recommended_search = list(set(initial_search_results.keys()).union(set(general_search_results.keys())))

    # 추천 검색어가 있을 경우, 추천 검색어 목록 표시
    if recommended_search:
        st.write("추천 검색어:")
        for suggestion in recommended_search:
            st.write(suggestion)

    # 검색 결과가 있는 경우, 검색 결과 표시
    if initial_search_results or general_search_results:
        st.subheader("🔍 검색 결과")
        combined_results = {**initial_search_results, **general_search_results}
        for word, info in combined_results.items():
            st.markdown(f"**{word}**: {info['definition']} (추가된 날짜: {info['date']})")
    else:
        st.warning("해당 초성이나 검색어로 시작하는 신조어가 없습니다.")

    # 고정된 유튜브 링크 표시
    if search_word in fixed_youtube_links:
        original_video_url = fixed_youtube_links[search_word]
        
        # 유튜브 쇼츠 링크를 일반 유튜브 링크로 변환
        if "youtube.com/shorts/" in original_video_url:
            video_id = original_video_url.split('/')[-1].split('?')[0]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
        else:
            video_url = original_video_url
        
        st.subheader("유튜브 동영상")
        st.video(video_url)
    else:
        st.write("관련 유튜브 동영상을 찾을 수 없습니다.")


# 신조어 추가 기능
st.subheader("➕ 신조어 추가하기")

new_word = st.text_input("신조어", "")
new_definition = st.text_area("정의", "")

if st.button("추가"):
    if new_word and new_definition:
        new_words_dict[new_word] = {
            "definition": new_definition,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        save_data(new_words_dict)  # JSON 파일에 저장
        st.success(f"'{new_word}'이(가) 사전에 추가되었습니다!")
    else:
        st.error("신조어와 정의를 모두 입력해 주세요.")

# 신조어 목록 표시
st.subheader("📚 신조어 목록")

if new_words_dict:
    for word, info in new_words_dict.items():
        st.markdown(f"**{word}**: {info['definition']} (추가된 날짜: {info['date']})")
else:
    st.write("사전에 신조어가 없습니다.")