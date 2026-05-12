import streamlit as st
import PyPDF2
import pandas as pd
import re
import plotly.express as px
from urllib.parse import quote

# --- 1. SESSION STATE ---
if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {'admin': '12345'}
if 'is_logged_in' not in st.session_state:
    st.session_state['is_logged_in'] = False
if 'show_signup' not in st.session_state:
    st.session_state['show_signup'] = False

# --- 2. STYLING ---
def local_css():
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1e1e2f 0%, #121212 100%); color: white; }
    div.stButton > button { 
        background-color: #4e54c8; color: white; border-radius: 12px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.3); transition: 0.3s;
    }
    div.stButton > button:hover { transform: translateY(-2px); background-color: #6366f1; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC ---
def extract_contact_info(text):
    email = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    phone = re.findall(r'(\+?\d{10,15})', text)
    return (email[0] if email else "N/A"), (phone[0] if phone else "N/A")

def get_analysis(text, skills):
    text_lower = text.lower()
    return {skill: text_lower.count(skill.lower()) for skill in skills}

# --- 4. AUTHENTICATION ---
def auth_page():
    local_css()
    st.markdown("<h1 style='text-align: center;'>🔐 AI Recruiter Pro</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state['show_signup']:
            st.subheader("📝 Create Account")
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Sign Up ✨"):
                st.session_state['users_db'][u] = p
                st.success("Account Created!")
                st.session_state['show_signup'] = False
                st.rerun()
            if st.button("Back to Login"):
                st.session_state['show_signup'] = False
                st.rerun()
        else:
            st.subheader("🔑 Login")
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Login 🚀"):
                if u in st.session_state['users_db'] and st.session_state['users_db'][u] == p:
                    st.session_state['is_logged_in'] = True
                    st.rerun()
                else: st.error("Wrong Username/Password!")
            if st.button("Create New Account"):
                st.session_state['show_signup'] = True
                st.rerun()

# --- 5. DASHBOARD ---
def dashboard():
    local_css()
    st.sidebar.title("Settings ⚙️")
    if st.sidebar.button("Logout 🚪"):
        st.session_state['is_logged_in'] = False
        st.rerun()

    min_score = st.sidebar.slider("Pass Threshold (%)", 0, 100, 50)
    skills_in = st.sidebar.text_area("Target Skills", "Python, SQL, React")
    REQUIRED_SKILLS = [s.strip() for s in skills_in.split(",") if s.strip()]

    st.markdown("<h1 style='color: #00d2ff;'>💎 Talent Dashboard</h1>", unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader("Upload Resumes", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        data = []
        for file in uploaded_files:
            try:
                reader = PyPDF2.PdfReader(file)
                text = "".join([p.extract_text() or "" for p in reader.pages])
                email, phone = extract_contact_info(text)
                score = (len([s for s in REQUIRED_SKILLS if s.lower() in text.lower()]) / len(REQUIRED_SKILLS)) * 100 if REQUIRED_SKILLS else 0
                data.append({
                    "Name": file.name, "Score": round(score, 1),
                    "Status": "✅ Selected" if score >= min_score else "❌ Rejected",
                    "Email": email, "Phone": phone
                })
            except Exception as e:
                st.error(f"Error reading {file.name}")

        df = pd.DataFrame(data)
        st.plotly_chart(px.bar(df, x="Name", y="Score", color="Status", template="plotly_dark"))
        st.dataframe(df, use_container_width=True)

        # --- OUTREACH SECTION ---
        st.divider()
        st.subheader("✉️ Contact Candidate")
        sel = st.selectbox("Select Name", df["Name"].unique())
        user = df[df["Name"] == sel].iloc[0]
        
        c1, c2 = st.columns(2)
        with c1:
            target_email = st.text_input("Email", user["Email"])
            target_phone = st.text_input("WhatsApp", user["Phone"])
        with c2:
            msg = f"Hi {sel}, you are {user['Status']} for the role."
            final_msg = st.text_area("Message", msg)
            
            b1, b2 = st.columns(2)
            with b1:
                st.link_button("📱 WhatsApp", f"https://wa.me/{target_phone.replace('+', '')}?text={quote(final_msg)}")
            with b2:
                st.link_button("📧 Email", f"mailto:{target_email}?subject=Update&body={quote(final_msg)}")

# --- RUN ---
if st.session_state['is_logged_in']:
    dashboard()
else:
    auth_page()
