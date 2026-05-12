import streamlit as st
import PyPDF2
import pandas as pd
import re
import webbrowser
import plotly.express as px
from urllib.parse import quote

# --- 1. SESSION STATE ---
if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {'admin': '12345'}
if 'is_logged_in' not in st.session_state:
    st.session_state['is_logged_in'] = False
if 'show_signup' not in st.session_state:
    st.session_state['show_signup'] = False

# --- 2. CUSTOM CSS (FOR 3D & NEON LOOK) ---
def local_css():
    st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #1e1e2f 0%, #121212 100%);
        color: #ffffff;
    }
    
    /* 3D Card Effect */
    div.stButton > button {
        background-color: #4e54c8;
        color: white;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        font-weight: bold;
    }
    div.stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(78, 84, 200, 0.5);
        background-color: #6366f1;
    }
    
    /* Metric Cards Styling */
    [data-testid="stMetricValue"] {
        font-size: 32px;
        color: #00d2ff;
        text-shadow: 0 0 10px rgba(0, 210, 255, 0.5);
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background-color: rgba(255, 255, 255, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC FUNCTIONS ---
def extract_contact_info(text):
    email = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    phone = re.findall(r'(\+?\d{10,15})', text)
    return (email[0] if email else "N/A"), (phone[0] if phone else "N/A")

def get_analysis(text, skills):
    text_lower = text.lower()
    return {skill: text_lower.count(skill.lower()) for skill in skills}

# --- 4. PAGES ---
def auth_page():
    local_css()
    st.markdown("<h1 style='text-align: center;'>🚀 AI Recruiter Pro</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state['show_signup']:
            st.subheader("📝 Sign Up")
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Create Account ✨"):
                st.session_state['users_db'][u] = p
                st.success("Account Ready! Login now.")
                st.session_state['show_signup'] = False
                st.rerun()
            if st.button("Back to Login"):
                st.session_state['show_signup'] = False
                st.rerun()
        else:
            st.subheader("🔐 Login")
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Enter Dashboard 🚀"):
                if u in st.session_state['users_db'] and st.session_state['users_db'][u] == p:
                    st.session_state['is_logged_in'] = True
                    st.rerun()
                else:
                    st.error("Invalid Credentials!")
            if st.button("New here? Create Account"):
                st.session_state['show_signup'] = True
                st.rerun()

def dashboard():
    local_css()
    # Sidebar
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=100)
    st.sidebar.title("Settings ⚙️")
    if st.sidebar.button("Logout 🚪"):
        st.session_state['is_logged_in'] = False
        st.rerun()

    st.sidebar.divider()
    min_score = st.sidebar.slider("🔥 Selection Threshold (%)", 0, 100, 60)
    skills_in = st.sidebar.text_area("🎯 Target Skills", "Python, SQL, React, Docker")
    REQUIRED_SKILLS = [s.strip() for s in skills_in.split(",") if s.strip()]

    # Main Header
    st.markdown("<h1 style='color: #00d2ff;'>💎 AI Talent Hub</h1>", unsafe_allow_html=True)
    st.write("Extracting the best candidates using Intelligence. ✨")

    # Upload Section
    with st.expander("📤 Upload Resumes (PDFs Only)", expanded=True):
        uploaded_files = st.file_uploader("", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        all_data = []
        for file in uploaded_files:
            reader = PyPDF2.PdfReader(file)
            text = "".join([p.extract_text() or "" for p in reader.pages])
            email, phone = extract_contact_info(text)
            counts = get_analysis(text, REQUIRED_SKILLS)
            found = [s for s, c in counts.items() if c > 0]
            score = (len(found) / len(REQUIRED_SKILLS)) * 100 if REQUIRED_SKILLS else 0
            
            all_data.append({
                "Name": file.name,
                "Match Score": round(score, 1),
                "Status": "✅ Shortlisted" if score >= min_score else "❌ Rejected",
                "Email": email, "Phone": phone, "Skills": ", ".join(found)
            })

        df = pd.DataFrame(all_data)

        # --- NEW DASHBOARD ELEMENTS ---
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Resumes", len(df))
        m2.metric("Shortlisted", len(df[df["Status"] == "✅ Shortlisted"]))
        m3.metric("Avg Match Rate", f"{round(df['Match Score'].mean(),1)}%")

        st.divider()

        # Visual Chart
        fig = px.bar(df, x="Name", y="Match Score", color="Status", 
                     title="Candidate Score Comparison", template="plotly_dark",
                     color_discrete_map={"✅ Shortlisted": "#00d2ff", "❌ Rejected": "#ff4b4b"})
        st.plotly_chart(fig, use_container_width=True)

        # Results Table
        st.subheader("📋 Screening Data")
        st.dataframe(df.style.background_gradient(subset=['Match Score'], cmap='Blues'), use_container_width=True)

        # --- OUTREACH SECTION ---
        st.markdown("### ✉️ Fast-Track Communication")
        select_c = st.selectbox("Pick a candidate to notify:", df["Name"].unique())
        c_info = df[df["Name"] == select_c].iloc[0]

        c1, c2 = st.columns(2)
        with c1:
            e_mail = st.text_input("Target Email", c_info["Email"])
            p_hone = st.text_input("Target WhatsApp", c_info["Phone"])
        with c2:
            msg_body = f"Hello {select_c}!\nWe are thrilled to inform you that you are {c_info['Status']} for the role."
            final_msg = st.text_area("Message Preview", msg_body)
            
            btn1, btn2 = st.columns(2)
            if btn1.button("📱 WhatsApp Now"):
                webbrowser.open(f"https://web.whatsapp.com/send?phone={p_hone}&text={quote(final_msg)}")
            if btn2.button("📧 Send Email"):
                webbrowser.open(f"mailto:{e_mail}?subject=Job Selection&body={quote(final_msg)}")

# --- START APP ---
if st.session_state['is_logged_in']:
    dashboard()
else:
    auth_page()
