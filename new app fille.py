import streamlit as st
import PyPDF2
import pandas as pd
import re
import plotly.express as px
from urllib.parse import quote

# --- 1. SESSION STATE (Data storage) ---
if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {'admin': '12345'}
if 'is_logged_in' not in st.session_state:
    st.session_state['is_logged_in'] = False
if 'show_signup' not in st.session_state:
    st.session_state['show_signup'] = False

# --- 2. THEME SETUP (Pink Theme) ---
def local_css():
    st.markdown("""
    <style>
    .stApp { 
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); 
        color: #333333; 
    }
    div.stButton > button { 
        background-color: #d63384; color: white; border-radius: 15px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); border: none; font-weight: bold;
    }
    div.stButton > button:hover { transform: scale(1.02); background-color: #b8266d; }
    .stDataFrame { background: white; border-radius: 10px; padding: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA EXTRACTION (Email & Phone Fetching) ---
def extract_info(text):
    # Email dhoondne ka formula
    email_list = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    # Phone number dhoondne ka formula (Pakistan/International formats)
    phone_list = re.findall(r'(\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9})', text)
    
    email = email_list[0] if email_list else "Not Found"
    # WhatsApp ke liye phone number clean karna (sirf digits)
    phone = phone_list[0] if phone_list else ""
    clean_phone = re.sub(r'\D', '', phone) # Sirf numbers reh jayenge
    
    return email, clean_phone

# --- 4. LOGIN/SIGNUP PAGES ---
def auth_page():
    local_css()
    st.markdown("<h1 style='text-align: center; color: #d63384;'>🌸 AI Candidate Screener</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state['show_signup']:
            u = st.text_input("New Username")
            p = st.text_input("New Password", type="password")
            if st.button("Create Account"):
                st.session_state['users_db'][u] = p
                st.success("Success! Please Login.")
                st.session_state['show_signup'] = False
                st.rerun()
            if st.button("Back"):
                st.session_state['show_signup'] = False
                st.rerun()
        else:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Login 🚀"):
                if u in st.session_state['users_db'] and st.session_state['users_db'][u] == p:
                    st.session_state['is_logged_in'] = True
                    st.rerun()
                else: st.error("Ghalat password!")
            if st.button("Sign Up"):
                st.session_state['show_signup'] = True
                st.rerun()

# --- 5. MAIN DASHBOARD ---
def dashboard():
    local_css()
    st.sidebar.title("HR Settings ⚙️")
    if st.sidebar.button("Log Out 🚪"):
        st.session_state['is_logged_in'] = False
        st.rerun()

    pass_score = st.sidebar.slider("Min Selection Score (%)", 0, 100, 50)
    skills_in = st.sidebar.text_area("Keywords to Search", "Python, SQL, React")
    REQUIRED = [s.strip().lower() for s in skills_in.split(",") if s.strip()]

    st.markdown("<h1 style='color: #d63384;'>🎀 Admin Dashboard</h1>", unsafe_allow_html=True)
    
    files = st.file_uploader("Upload Resumes (PDF)", type="pdf", accept_multiple_files=True)

    if files:
        results = []
        for f in files:
            pdf = PyPDF2.PdfReader(f)
            text = "".join([p.extract_text() or "" for p in pdf.pages])
            email, phone = extract_info(text)
            
            # Scoring logic
            found = [s for s in REQUIRED if s in text.lower()]
            score = (len(found) / len(REQUIRED)) * 100 if REQUIRED else 0
            
            results.append({
                "Name": f.name, "Score": round(score, 1),
                "Status": "✅ Shortlisted" if score >= pass_score else "❌ Rejected",
                "Email": email, "Phone": phone, "Skills": ", ".join(found)
            })

        df = pd.DataFrame(results)
        st.plotly_chart(px.bar(df, x="Name", y="Score", color="Status", 
                               color_discrete_map={"✅ Shortlisted": "#d63384", "❌ Rejected": "#ff9a9e"}))
        st.dataframe(df, use_container_width=True)

        # --- OUTREACH (Email & WhatsApp) ---
        st.divider()
        st.subheader("✉️ Fast Outreach")
        sel_name = st.selectbox("Select Candidate to Contact", df["Name"].unique())
        user_row = df[df["Name"] == sel_name].iloc[0]

        col_a, col_b = st.columns(2)
        with col_a:
            target_mail = st.text_input("Email", user_row["Email"])
            target_wa = st.text_input("WhatsApp Number (with country code)", user_row["Phone"])
        with col_b:
            msg = f"Hi {sel_name}, you have been {user_row['Status']} for the next round."
            final_msg = st.text_area("Edit Message", msg)
            
            b1, b2 = st.columns(2)
            with b1:
                # WhatsApp Button
                st.link_button("📱 WhatsApp", f"https://wa.me/{target_wa}?text={quote(final_msg)}")
            with b2:
                # Email Button (Opens Gmail/Outlook)
                st.link_button("📧 Email", f"mailto:{target_mail}?subject=Job Update&body={quote(final_msg)}")

# --- START ---
if st.session_state['is_logged_in']:
    dashboard()
else:
    auth_page()
