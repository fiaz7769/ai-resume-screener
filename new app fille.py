import streamlit as st
import PyPDF2
import pandas as pd
import re
import plotly.express as px
from urllib.parse import quote

# --- 1. SESSION STATE (User ka data yaad rakhne ke liye) ---
if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {'admin': '12345'}
if 'is_logged_in' not in st.session_state:
    st.session_state['is_logged_in'] = False
if 'show_signup' not in st.session_state:
    st.session_state['show_signup'] = False

# --- 2. STYLING (Yahan se colors change hote hain) ---
def local_css():
    st.markdown("""
    <style>
    /* Pure App ka Background - Pink Gradient */
    .stApp { 
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%); 
        color: #4a4a4a; 
    }
    
    /* Buttons ka Style - Dark Pink/Rose */
    div.stButton > button { 
        background-color: #ff4bb4; 
        color: white; 
        border-radius: 20px; 
        border: none;
        box-shadow: 0 4px 15px rgba(255, 75, 180, 0.3);
        font-weight: bold;
    }
    
    /* Input Boxes ka Style */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #ff9a9e;
    }

    /* Sidebar ka color */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC (CV se email aur phone nikalne ke liye) ---
def extract_contact_info(text):
    email = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    phone = re.findall(r'(\+?\d{10,15})', text)
    return (email[0] if email else "N/A"), (phone[0] if phone else "N/A")

# --- 4. AUTHENTICATION (Login aur Signup Page) ---
def auth_page():
    local_css()
    st.markdown("<h1 style='text-align: center; color: #d63384;'>🌸 HR Talent Portal</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state['show_signup']:
            st.subheader("📝 Naya Account Banayein")
            u = st.text_input("Username Choose Karein")
            p = st.text_input("Password Choose Karein", type="password")
            if st.button("Sign Up ✨"):
                st.session_state['users_db'][u] = p
                st.success("Account Ban Gaya! Ab Login Karein.")
                st.session_state['show_signup'] = False
                st.rerun()
            if st.button("Wapis Login par Jayein"):
                st.session_state['show_signup'] = False
                st.rerun()
        else:
            st.subheader("🔑 Login Karein")
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Enter Dashboard 🎀"):
                if u in st.session_state['users_db'] and st.session_state['users_db'][u] == p:
                    st.session_state['is_logged_in'] = True
                    st.rerun()
                else: st.error("Ghalat Username ya Password!")
            if st.button("Account Nahi Hai? Yahan Click Karein"):
                st.session_state['show_signup'] = True
                st.rerun()

# --- 5. DASHBOARD (Asli Kaam Yahan Hota Hai) ---
def dashboard():
    local_css()
    # Sidebar Settings
    st.sidebar.title("Settings ⚙️")
    if st.sidebar.button("Logout 🚪"):
        st.session_state['is_logged_in'] = False
        st.rerun()

    # Viva Tip: Yahan se Selection Criteria badalte hain
    st.sidebar.subheader("🎯 Selection Rules")
    min_score = st.sidebar.slider("Passing Score (%)", 0, 100, 50)
    skills_in = st.sidebar.text_area("Zaroori Skills", "Python, SQL, React")
    REQUIRED_SKILLS = [s.strip() for s in skills_in.split(",") if s.strip()]

    st.markdown("<h1 style='color: #d63384;'>💖 Recruitment Dashboard</h1>", unsafe_allow_html=True)
    
    # File Upload karne ka section
    uploaded_files = st.file_uploader("CVs Upload Karein (PDF Only)", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        data = []
        for file in uploaded_files:
            try:
                reader = PyPDF2.PdfReader(file)
                text = "".join([p.extract_text() or "" for p in reader.pages])
                email, phone = extract_contact_info(text)
                # Score check karne ka formula
                score = (len([s for s in REQUIRED_SKILLS if s.lower() in text.lower()]) / len(REQUIRED_SKILLS)) * 100 if REQUIRED_SKILLS else 0
                data.append({
                    "Name": file.name, "Score": round(score, 1),
                    "Status": "✅ Selected" if score >= min_score else "❌ Rejected",
                    "Email": email, "Phone": phone
                })
            except Exception as e:
                st.error(f"Error reading {file.name}")

        df = pd.DataFrame(data)
        
        # Graphs dikhane ke liye
        st.plotly_chart(px.bar(df, x="Name", y="Score", color="Status", 
                               color_discrete_map={"✅ Selected": "#d63384", "❌ Rejected": "#ff9a9e"}))
        
        # Table dikhane ke liye
        st.dataframe(df, use_container_width=True)

        # --- OUTREACH SECTION (Mail aur WhatsApp) ---
        st.divider()
        st.subheader("✉️ Candidate ko Contact Karein")
        sel = st.selectbox("Candidate Select Karein", df["Name"].unique())
        user = df[df["Name"] == sel].iloc[0]
        
        c1, c2 = st.columns(2)
        with c1:
            target_email = st.text_input("Email", user["Email"])
            target_phone = st.text_input("WhatsApp", user["Phone"])
        with c2:
            msg = f"Hi {sel}, we have processed your CV and you are {user['Status']}."
            final_msg = st.text_area("Message Preview", msg)
            
            b1, b2 = st.columns(2)
            with b1:
                # WhatsApp ka direct link
                st.link_button("📱 WhatsApp", f"https://wa.me/{target_phone.replace('+', '')}?text={quote(final_msg)}")
            with b2:
                # Email ka direct link
                st.link_button("📧 Email", f"mailto:{target_email}?subject=Job Update&body={quote(final_msg)}")

# --- APP START ---
if st.session_state['is_logged_in']:
    dashboard()
else:
    auth_page()
