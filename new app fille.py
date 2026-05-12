import streamlit as st
import PyPDF2
import pandas as pd
import re
import webbrowser
from urllib.parse import quote

# --- FUNCTIONS ---
def extract_contact_info(text):
    email = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    phone = re.findall(r'(\+?\d{10,15})', text)
    return (email[0] if email else "Not Found"), (phone[0] if phone else "")

def get_analysis(text, skills):
    text_lower = text.lower()
    return {skill: text_lower.count(skill.lower()) for skill in skills}

# --- LOGIN SYSTEM ---
def login():
    st.title("🔐 HR Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "12345": # Aap ye badal sakte hain
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Ghalat Username ya Password!")

# --- MAIN APP ---
def main_app():
    st.set_page_config(page_title="AI Recruiter Pro", layout="wide")
    
    # Logout Button
    if st.sidebar.button("Log Out"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.title("🤖 Smart AI Resume Screener")

    # --- SIDEBAR: CRITERIA SETTINGS ---
    st.sidebar.header("🎯 Selection Criteria")
    min_score = st.sidebar.slider("Pass Marks (%)", 0, 100, 50)
    skills_input = st.sidebar.text_input("Required Skills (Comma separated)", "Python, SQL, React")
    REQUIRED_SKILLS = [s.strip() for s in skills_input.split(",") if s.strip()]

    # --- FILE UPLOADER ---
    uploaded_files = st.file_uploader("Upload Resumes (PDF)", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        all_data = []
        for file in uploaded_files:
            reader = PyPDF2.PdfReader(file)
            text = "".join([page.extract_text() or "" for page in reader.pages])
            
            email, phone = extract_contact_info(text)
            skill_counts = get_analysis(text, REQUIRED_SKILLS)
            found_skills = [s for s, count in skill_counts.items() if count > 0]
            score = (len(found_skills) / len(REQUIRED_SKILLS)) * 100 if REQUIRED_SKILLS else 0
            
            # Criteria logic
            status = "✅ Shortlisted" if score >= min_score else "❌ Rejected"
            
            all_data.append({
                "Candidate": file.name,
                "Score %": round(score, 1),
                "Status": status,
                "Email": email,
                "Phone": phone,
                "Skills Found": ", ".join(found_skills)
            })

        df = pd.DataFrame(all_data)
        st.subheader("📊 Screening Results")
        st.dataframe(df, use_container_width=True)

        # --- OUTREACH PANEL ---
        st.divider()
        st.header("📲 Contact Selected Candidates")
        
        # Sirf Shortlisted logo ki list dikhayi degi
        shortlisted_only = df[df["Status"] == "✅ Shortlisted"]
        
        if not shortlisted_only.empty:
            selection = st.selectbox("Select Candidate to Notify", shortlisted_only["Candidate"].unique())
            user_row = df[df["Candidate"] == selection].iloc[0]

            col1, col2 = st.columns(2)
            with col1:
                target_email = st.text_input("Email", user_row["Email"])
                target_phone = st.text_input("Phone (Country Code ke sath)", user_row["Phone"])
            
            with col2:
                msg = st.text_area("Message", f"Hi {selection},\nCongratualtions! You are shortlisted for the interview. Let us know your availability.")
                
                c_btn1, c_btn2 = st.columns(2)
                if c_btn1.button("📱 WhatsApp"):
                    if target_phone:
                        webbrowser.open(f"https://web.whatsapp.com/send?phone={target_phone}&text={quote(msg)}")
                    else: st.error("Phone number nahi mila!")
                
                if c_btn2.button("📧 Email"):
                    webbrowser.open(f"mailto:{target_email}?subject=Job Selection&body={quote(msg)}")
        else:
            st.warning("Koi bhi candidate criteria par poora nahi utra.")

# --- APP FLOW CONTROL ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    main_app()
else:
    login()
