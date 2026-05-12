import streamlit as st
import PyPDF2
import pandas as pd
import re
import webbrowser
from urllib.parse import quote

# --- 1. SESSION STATE INITIALIZATION ---
# Is se app yaad rakhti hai ke user ne account banaya hai ya nahi
if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {}  # Yahan temporary account store honge
if 'is_logged_in' not in st.session_state:
    st.session_state['is_logged_in'] = False
if 'show_signup' not in st.session_state:
    st.session_state['show_signup'] = False

# --- 2. HELPER FUNCTIONS ---
def extract_contact_info(text):
    email = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    phone = re.findall(r'(\+?\d{10,15})', text)
    return (email[0] if email else "Not Found"), (phone[0] if phone else "")

def get_analysis(text, skills):
    text_lower = text.lower()
    return {skill: text_lower.count(skill.lower()) for skill in skills}

# --- 3. AUTHENTICATION PAGES ---

def auth_page():
    st.set_page_config(page_title="AI Recruiter - Auth", page_icon="🔐")
    
    if st.session_state['show_signup']:
        # --- SIGN UP PAGE ---
        st.title("📝 Create New Account")
        new_user = st.text_input("Choose Username")
        new_pass = st.text_input("Choose Password", type="password")
        confirm_pass = st.text_input("Confirm Password", type="password")
        
        if st.button("Create Account"):
            if new_user in st.session_state['users_db']:
                st.warning("Username pehle se maujood hai!")
            elif new_pass != confirm_pass:
                st.error("Passwords match nahi kar rahe!")
            elif new_user and new_pass:
                st.session_state['users_db'][new_user] = new_pass
                st.success("Account ban gaya! Ab login karein.")
                st.session_state['show_signup'] = False
                st.rerun()
            else:
                st.error("Fields khali na chorrein.")
        
        if st.button("Already have an account? Login"):
            st.session_state['show_signup'] = False
            st.rerun()
            
    else:
        # --- LOGIN PAGE ---
        st.title("🔐 HR Admin Login")
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login"):
                if user in st.session_state['users_db'] and st.session_state['users_db'][user] == pw:
                    st.session_state['is_logged_in'] = True
                    st.rerun()
                else:
                    st.error("Username ya Password ghalat hai!")
        with col2:
            if st.button("New User? Sign Up"):
                st.session_state['show_signup'] = True
                st.rerun()

# --- 4. MAIN DASHBOARD ---

def dashboard():
    st.set_page_config(page_title="HR Dashboard", layout="wide")
    
    # Sidebar
    st.sidebar.title("Settings")
    if st.sidebar.button("Logout"):
        st.session_state['is_logged_in'] = False
        st.rerun()
        
    st.title("🤖 AI Resume Screening Dashboard")
    st.write(f"Welcome back, Admin!")

    # Criteria
    st.sidebar.divider()
    st.sidebar.header("🎯 Match Criteria")
    min_score = st.sidebar.slider("Minimum Matching %", 0, 100, 50)
    skills_input = st.sidebar.text_input("Skills (comma separated)", "Python, SQL, AWS")
    REQUIRED_SKILLS = [s.strip() for s in skills_input.split(",") if s.strip()]

    # Uploader
    uploaded_files = st.file_uploader("Upload Candidates' Resumes", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        all_results = []
        for file in uploaded_files:
            reader = PyPDF2.PdfReader(file)
            text = "".join([p.extract_text() or "" for p in reader.pages])
            email, phone = extract_contact_info(text)
            
            skill_counts = get_analysis(text, REQUIRED_SKILLS)
            found = [s for s, c in skill_counts.items() if c > 0]
            score = (len(found) / len(REQUIRED_SKILLS)) * 100 if REQUIRED_SKILLS else 0
            status = "✅ Shortlisted" if score >= min_score else "❌ Not Selected"
            
            all_results.append({
                "Name": file.name,
                "Match %": round(score, 1),
                "Status": status,
                "Email": email,
                "Phone": phone,
                "Matched Skills": ", ".join(found)
            })

        df = pd.DataFrame(all_results)
        st.subheader("📊 Candidate Rankings")
        st.dataframe(df, use_container_width=True)

        # Outreach
        st.divider()
        st.subheader("✉️ Fast Outreach")
        shortlisted = df[df["Status"] == "✅ Shortlisted"]
        
        if not shortlisted.empty:
            target = st.selectbox("Select Candidate", shortlisted["Name"])
            c_data = shortlisted[shortlisted["Name"] == target].iloc[0]
            
            c1, c2 = st.columns(2)
            with c1:
                email_addr = st.text_input("Email", c_data["Email"])
                phone_num = st.text_input("Phone", c_data["Phone"])
            with c2:
                msg = st.text_area("Message", f"Hi {target}, congrats! You are shortlisted.")
                if st.button("Send WhatsApp"):
                    if phone_num:
                        webbrowser.open(f"https://web.whatsapp.com/send?phone={phone_num}&text={quote(msg)}")
                if st.button("Send Email"):
                    webbrowser.open(f"mailto:{email_addr}?subject=Job Update&body={quote(msg)}")
        else:
            st.info("No one shortlisted yet based on current criteria.")

# --- 5. LOGIC CONTROL ---
if st.session_state['is_logged_in']:
    dashboard()
else:
    auth_page()
