import streamlit as st
import pandas as pd
from csv_parser.loader import cvs2csv,clear_csv
from rag.rag import query_rag, clear_data as clear_rag
import os
from dotenv import load_dotenv
from auth.authenticate import Authentificator
from utils import get_messages

load_dotenv()
@st.cache_data
def process_files(files):
    cvs2csv(files)
authenticator=Authentificator(
    secret_path="client_secret.json",
    redirect_uri="http://localhost:8501",
    token_key=os.environ["TOKEN_KEY"]
)
authenticator.check_login()
authenticator.login()
if st.session_state["connected"]:
    authenticator.check_access_token()
    with st.sidebar:
        st.markdown(
            f"""
            <div style="margin-bottom:10px;padding: 10px; border-radius: 8px; background-color: #f0f2f6; text-align:center; font-weight: bold; color:black;">
                👤 {st.session_state["user_infos"].get("email")}
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("logout"):
            authenticator.logout()
        st.divider()
        st.subheader("⚙️ Settings")
        with st.expander("Candidate Feature Weights"):
            education_weight = st.slider("📚 Education", 0, 5, 2)
            experience_weight = st.slider("💼 Experience", 0, 5, 2)
            skills_weight = st.slider("🛠️ Skills", 0, 5, 2)
            certificates_weight = st.slider("📜 Certificates", 0, 5, 2)

        # Store preferences for model use
        user_preferences = {
            "education": education_weight,
            "experience": experience_weight,
            "skills": skills_weight,
            "certificates": certificates_weight
        }
        with st.expander("Advanced Settings"):
            st.write("Automatically fetch resumes from your inbox.")
            subject=st.text_input("📧 Subject:")
            before=st.date_input("📅 Before:")
            after=st.date_input("📅 After:")
            clicked=st.button("📧 Fetch emails", disabled= (len(subject)==0))
            if clicked:
                if (after > before):
                  st.warning("Before date must be after the after date.",icon="🚨")
                else:
                    loading_gmail_text=st.text("Fetching CVs...")
                    try:
                        files=get_messages(
                            st.session_state["user_infos"].get("email"),
                            before.strftime("%Y/%m/%d"),
                            after.strftime("%Y/%m/%d"),
                            subject,
                            token=st.session_state["user_infos"].get("tokens", {})["access_token"]
                            )
                        loading_gmail_text.text(f"✅{len(files)} CVs fetched successfully!" if len(files)>0 else "No CVs found.")
                        if len(files)>0:
                            parsing_text=st.text("Parsing CVs...")
                            process_files(files)
                            parsing_text.text("✅CVs parsed successfully!")
                    except Exception as e:
                        st.error(f"An error occured: {e}")

    st.title("Welcome to your Dashboard 🌟")
    st.write("Upload the resumes you want to analyze and start asking questions!")
    uploaded_files=st.file_uploader(
        "Only pdf files are accepted.", accept_multiple_files=True, label_visibility="collapsed", type=["pdf"])
    if uploaded_files:
        text_loader=st.text("loading data...")
        process_files(uploaded_files)
        text_loader.text("")
    file_exists=os.path.isfile(os.environ["OUTPUT_DATA_PATH"]) and os.path.getsize(os.environ["OUTPUT_DATA_PATH"])>0
    if file_exists:
        try:
            df=pd.read_csv(os.environ["OUTPUT_DATA_PATH"],encoding="utf-8")
            if not df.empty:
                st.subheader("Your candidates:")
                clicked=st.button("Clear data")
                if clicked:
                    try:
                        st.cache_data.clear()
                        clear_csv()
                        clear_rag()
                        st.rerun()
                    except Exception as e:
                        st.error(f"An error occured: {e}")
                        st.stop()
                st.dataframe(df)
                if prompt:=st.chat_input("Filter your candidates..."):
                    rag_loader=st.text("✨✨...Processing...✨✨")
                    refined_candidates = query_rag(prompt,user_preferences)
                    refined_candidates = eval(refined_candidates)
                    if len(refined_candidates) == 0:
                        rag_loader.write("No candidates found.")
                    else:
                        rag_loader.write("✨Here are your refined candidates based on your preferences:")
                        st.dataframe(refined_candidates)
        except Exception as e:
            st.error(f"An error occured: {e}")    
        
        
    