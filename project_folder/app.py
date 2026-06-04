import streamlit as st
from openai import OpenAI
import base64
import json
import pandas as pd

st.set_page_config(layout="wide")

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

st.title("공강 스케줄러")

api_key_input = st.text_input("OpenAI API Key를 입력하세요", type="password", value=st.session_state.api_key)

if api_key_input:
    st.session_state.api_key = api_key_input
    client = OpenAI(api_key=st.session_state.api_key)
    
    uploaded_file = st.file_uploader("에브리타임 시간표 이미지 업로드", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(uploaded_file, use_container_width=True)
        
        with col2:
            if st.button("시간표 분석하기"):
                with st.spinner("AI가 시간표를 읽고 있습니다..."):
                    base64_image = encode_image(uploaded_file)
                    
                    try:
                        response = client.chat.completions.create(
                            model="gpt-5.4-mini",
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You must output strictly in JSON format without any markdown wrappers. The format should be a list of dictionaries, like: [{\"요일\": \"월\", \"과목명\": \"수학\", \"시작\": \"09:00\", \"종료\": \"10:30\"}]"
                                },
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "text", 
                                            "text": "이 시간표 이미지에서 월요일부터 금요일까지의 수업 요일, 과목명, 시작 시간, 종료 시간을 JSON 형식으로 추출해."
                                        },
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/jpeg;base64,{base64_image}"
                                            }
                                        }
                                    ]
                                }
                            ],
                            max_completion_tokens=1500
                        )
                        
                        raw_text = response.choices[0].message.content
                        cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()
                        parsed_json = json.loads(cleaned_text)
                        
                        st.success("시간표 분석이 완료되었습니다")

                        df = pd.DataFrame(parsed_json)

                        st.dataframe(df, use_container_width=True, hide_index=True)
                        
                    except json.JSONDecodeError:
                        st.error("JSON 파싱 오류: AI가 형태를 잘못 반환했습니다. 다시 시도해주세요.")
                    except Exception as e:
                        st.error(f"오류가 발생했습니다: {e}")
else:
    st.warning("앱을 사용하려면 먼저 OpenAI API Key를 입력해주세요.")