import datetime
import pandas as pd
import requests
import streamlit as st
import pytz

# 페이지 기본 설정 (타이틀, 레이아웃)
st.set_page_config(
    page_title="날짜별 박스오피스 순위",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 날짜별 박스오피스 순위")

# -------------------------------------------------------------------
# 1. secrets 키 확인 및 기준 날짜 설정
# -------------------------------------------------------------------
# Streamlit Secrets에서 KOBIS_KEY 가져오기
if "KOBIS_KEY" not in st.secrets:
    st.error("❌ secrets 설정에서 `KOBIS_KEY`를 찾을 수 없습니다.")
    st.info(
        "**확인사항:**\n"
        "Streamlit Cloud 관리 화면의 **Secrets** 항목에 "
        "`KOBIS_KEY = \"발급받은_키\"` 형태로 비밀키를 입력했는지 확인해 주세요."
    )
    st.stop()

api_key = st.secrets["KOBIS_KEY"]

# Streamlit Cloud 서버 시간과 상관없이 한국 시간(Asia/Seoul)을 기준으로 설정
korea_tz = pytz.timezone("Asia/Seoul")
now_korea = datetime.datetime.now(korea_tz).date()

# 오늘 자 데이터는 집계 전이므로 선택 가능한 최대 날짜는 '어제'
max_selectable_date = now_korea - datetime.timedelta(days=1)

# 사이드바 또는 상단에서 날짜 선택 (기본값: 어제)
selected_date = st.date_input(
    label="📅 조회할 날짜를 선택하세요 (최대 어제까지 선택 가능)",
    value=max_selectable_date,
    max_value=max_selectable_date,
    min_value=datetime.date(2004, 1, 1)  # KOBIS 데이터 시작 시점 근처
)

# API 요청용 날짜 포맷 (YYYYMMDD) 및 화면 출력용 포맷
target_dt = selected_date.strftime("%Y%m%d")
display_date = selected_date.strftime("%Y년 %m월 %d일")

st.caption(f"📅 선택된 조회 일자: {display_date} (한국 시간 기준)")

# -------------------------------------------------------------------
# 2. KOBIS API 데이터 요청
# -------------------------------------------------------------------
url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
params = {
    "key": api_key,
    "targetDt": target_dt
}

try:
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
except Exception as e:
    st.error("❌ API 서버 통신 중 오류가 발생했습니다.")
    st.info(
        "**확인사항:**\n"
        "- 인터넷 연결 상태를 확인해 주세요.\n"
        "- KOBIS OpenAPI 서버가 정상 작동 중인지 확인해 주세요."
    )
    st.stop()

# -------------------------------------------------------------------
# 3. 응답 데이터 검증 (faultInfo 및 빈 리스트 처리)
# -------------------------------------------------------------------
if "faultInfo" in data:
    fault_message = data["faultInfo"].get("message", "알 수 없는 오류")
    st.error(f"❌ API 오류 응답: {fault_message}")
    st.info(
        "**확인사항:**\n"
        "- `secrets`에 입력한 KOBIS API 키가 올바른지 확인해 주세요.\n"
        "- 영화진흥위원회 통합전산망(KOBIS)에서 키가 활성화 상태인지 확인해 주세요."
    )
    st.stop()

box_office_result = data.get("boxOfficeResult", {})
daily_list = box_office_result.get
