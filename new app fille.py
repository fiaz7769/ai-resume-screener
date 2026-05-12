import streamlit as st
import PyPDF2
import pandas as pd
import re
import plotly.express as px
import base64
from urllib.parse import quote
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="HR Talent Portal",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. SESSION STATE ---
if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {'admin': '12345'}
if 'is_logged_in' not in st.session_state:
    st.session_state['is_logged_in'] = False
if 'show_signup' not in st.session_state:
    st.session_state['show_signup'] = False
if 'processing' not in st.session_state:
    st.session_state['processing'] = False

# --- 2. ADVANCED 3D CSS STYLING ---
def local_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Animated Gradient Background */
    .stApp {
        background: linear-gradient(
            135deg,
            rgba(255, 154, 158, 0.95) 0%,
            rgba(254, 207, 239, 0.95) 50%,
            rgba(255, 154, 158, 0.95) 100%
        );
        animation: gradientShift 10s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* 3D Glass Card Effect */
    .glass-card {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(12px);
        border-radius: 28px;
        padding: 2rem;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.1),
            0 0 0 1px rgba(255, 255, 255, 0.18),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        transform: translateY(0);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    .glass-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
    }
    
    /* 3D Button Styles */
    div.stButton > button {
        background: linear-gradient(135deg, #ff6b9d 0%, #ff4bb4 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        letter-spacing: 0.5px;
        box-shadow: 0 8px 20px rgba(255, 75, 180, 0.3);
        transition: all 0.3s ease;
        transform: translateY(0);
    }
    
    div.stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 30px rgba(255, 75, 180, 0.4);
        background: linear-gradient(135deg, #ff7bae 0%, #ff5bc4 100%);
    }
    
    div.stButton > button:active {
        transform: translateY(2px);
    }
    
    /* 3D Input Fields */
    .stTextInput > div > div > input {
        border-radius: 50px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        background: rgba(255, 255, 255, 0.9);
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #ff4bb4;
        box-shadow: 0 0 0 3px rgba(255, 75, 180, 0.2);
        transform: scale(1.02);
    }
    
    /* Sidebar 3D Effect */
    section[data-testid="stSidebar"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.1));
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 5px 0 30px rgba(0, 0, 0, 0.1);
    }
    
    /* Card Styles for Metrics */
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.8));
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.15);
    }
    
    /* Floating Animation for Headers */
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .floating-header {
        animation: float 3s ease-in-out infinite;
        text-align: center;
        background: linear-gradient(135deg, #d63384, #ff4bb4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
    }
    
    /* File Uploader Styling */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 1rem;
        border: 2px dashed rgba(255, 255, 255, 0.5);
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: #ff4bb4;
        background: rgba(255, 255, 255, 0.3);
    }
    
    /* Progress Bar 3D */
    .stProgress > div > div {
        background: linear-gradient(90deg, #ff4bb4, #ff9a9e);
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(255, 75, 180, 0.3);
    }
    
    /* Select Box Styling */
    .stSelectbox > div > div {
        border-radius: 50px;
        background: rgba(255, 255, 255, 0.9);
    }
    
    /* Alert Messages */
    .stAlert {
        border-radius: 15px;
        border-left: 4px solid #ff4bb4;
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
    }
    
    /* Dataframe Styling */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #ff4bb4;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #d63384;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC ---
def extract_contact_info(text):
    email = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    phone = re.findall(r'(?:\+?91[\s-]?)?[6-9]\d{9}|(?:\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}', text)
    return (email[0] if email else "N/A"), (phone[0] if phone else "N/A")

def extract_name_from_cv(text):
    lines = text.split('\n')
    for line in lines[:15]:
        line = line.strip()
        if len(line.split()) <= 4 and len(line) > 3 and line[0].isupper():
            if not any(keyword in line.lower() for keyword in ['resume', 'curriculum', 'vitae', 'cv', 'email', 'phone']):
                return line
    return "Candidate"

# --- 4. AUTHENTICATION ---
def auth_page():
    local_css()
    
    # 3D Background Effect
    st.markdown("""
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1;">
            <div style="position: absolute; width: 500px; height: 500px; background: radial-gradient(circle, rgba(255,75,180,0.3), transparent); top: -250px; right: -250px; border-radius: 50%;"></div>
            <div style="position: absolute; width: 400px; height: 400px; background: radial-gradient(circle, rgba(255,154,158,0.3), transparent); bottom: -200px; left: -200px; border-radius: 50%;"></div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<h1 class="floating-header">✨ HR Talent Portal ✨</h1>', unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; margin-bottom: 2rem;'>Next-Gen Recruitment Intelligence</p>", unsafe_allow_html=True)
        
        if st.session_state['show_signup']:
            st.markdown("<h3 style='text-align: center; color: #d63384;'>📝 Create New Account</h3>", unsafe_allow_html=True)
            username = st.text_input("✨ Username", key="signup_user", placeholder="Choose a unique username")
            password = st.text_input("🔒 Password", type="password", key="signup_pass", placeholder="Create a strong password")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🎉 Sign Up", use_container_width=True):
                    if username and password:
                        if username in st.session_state['users_db']:
                            st.error("❌ Username already exists! Please choose another.")
                        else:
                            st.session_state['users_db'][username] = password
                            st.success("✅ Account created successfully! Please login.")
                            time.sleep(1)
                            st.session_state['show_signup'] = False
                            st.rerun()
                    else:
                        st.error("❌ Please fill all fields!")
            
            with col_btn2:
                if st.button("← Back to Login", use_container_width=True):
                    st.session_state['show_signup'] = False
                    st.rerun()
        else:
            st.markdown("<h3 style='text-align: center; color: #d63384;'>🔐 Welcome Back</h3>", unsafe_allow_html=True)
            username = st.text_input("👤 Username", key="login_user", placeholder="Enter your username")
            password = st.text_input("🔑 Password", type="password", key="login_pass", placeholder="Enter your password")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🚀 Login", use_container_width=True):
                    if username in st.session_state['users_db'] and st.session_state['users_db'][username] == password:
                        st.session_state['is_logged_in'] = True
                        st.success("✅ Login successful! Redirecting...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password!")
            
            with col_btn2:
                if st.button("📝 Sign Up", use_container_width=True):
                    st.session_state['show_signup'] = True
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. MAIN DASHBOARD ---
def dashboard():
    local_css()
    
    # Sidebar with 3D styling
    st.sidebar.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h2 style="color: #d63384;">⚙️ Settings</h2>
            <div style="width: 50px; height: 3px; background: linear-gradient(90deg, #ff4bb4, #ff9a9e); margin: 0 auto; border-radius: 3px;"></div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state['is_logged_in'] = False
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 Selection Criteria")
    min_score = st.sidebar.slider("Minimum Score (%)", 0, 100, 65, help="Candidates with score above this will be selected")
    skills_in = st.sidebar.text_area("Required Skills", "Python, SQL, Machine Learning, React", help="Enter skills separated by commas")
    REQUIRED_SKILLS = [s.strip() for s in skills_in.split(",") if s.strip()]
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Stats")
    
    # Main content
    st.markdown("""
        <div style="position: relative;">
            <h1 class="floating-header">💎 Recruitment Intelligence Dashboard</h1>
            <p style="text-align: center; color: #666; margin-bottom: 2rem;">AI-Powered Candidate Screening & Analytics</p>
        </div>
    """, unsafe_allow_html=True)
    
    # File uploader with 3D effect
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📁 Upload Candidate CVs")
    st.markdown("*Supported format: PDF only*")
    uploaded_files = st.file_uploader("", type="pdf", accept_multiple_files=True, label_visibility="collapsed")
    
    if uploaded_files and not st.session_state.get('processing', False):
        st.session_state['processing'] = True
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        data = []
        for idx, file in enumerate(uploaded_files):
            status_text.text(f"Processing {file.name}...")
            try:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                
                email, phone = extract_contact_info(text)
                name = extract_name_from_cv(text)
                score = (len([s for s in REQUIRED_SKILLS if s.lower() in text.lower()]) / len(REQUIRED_SKILLS)) * 100 if REQUIRED_SKILLS else 0
                
                data.append({
                    "Name": name,
                    "Filename": file.name,
                    "Score": round(score, 1),
                    "Status": "✅ Selected" if score >= min_score else "❌ Rejected",
                    "Email": email,
                    "Phone": phone
                })
                progress_bar.progress((idx + 1) / len(uploaded_files))
            except Exception as e:
                st.error(f"⚠️ Error processing {file.name}: {str(e)}")
        
        status_text.text("✅ Processing complete!")
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        if data:
            df = pd.DataFrame(data)
            
            # Metrics Row
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                    <div class="metric-card">
                        <h3>📄 Total CVs</h3>
                        <h2 style="color: #d63384;">{len(df)}</h2>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                selected = len(df[df['Status'] == '✅ Selected'])
                st.markdown(f"""
                    <div class="metric-card">
                        <h3>✅ Selected</h3>
                        <h2 style="color: #28a745;">{selected}</h2>
                    </div>
                """, unsafe_allow_html=True)
            with col3:
                rejected = len(df[df['Status'] == '❌ Rejected'])
                st.markdown(f"""
                    <div class="metric-card">
                        <h3>❌ Rejected</h3>
                        <h2 style="color: #dc3545;">{rejected}</h2>
                    </div>
                """, unsafe_allow_html=True)
            with col4:
                avg_score = df['Score'].mean()
                st.markdown(f"""
                    <div class="metric-card">
                        <h3>📊 Avg Score</h3>
                        <h2 style="color: #ff4bb4;">{avg_score:.1f}%</h2>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Interactive 3D Chart
            st.markdown("### 📈 Performance Analytics")
            fig = px.bar(df, x="Name", y="Score", color="Status", 
                        color_discrete_map={"✅ Selected": "#ff4bb4", "❌ Rejected": "#ff9a9e"},
                        title="<b>Candidate Scores Overview</b>",
                        labels={"Score": "Score (%)", "Name": "Candidate Name"},
                        text="Score")
            fig.update_traces(textposition='outside', marker=dict(line=dict(width=2, color='white')))
            fig.update_layout(
                plot_bgcolor='rgba(255,255,255,0.1)',
                paper_bgcolor='rgba(255,255,255,0)',
                font=dict(family="Inter", size=12),
                title_font_size=20,
                title_x=0.5,
                bargap=0.2,
                hovermode='closest'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed Table
            st.markdown("### 📋 Candidate Details")
            st.dataframe(df[["Name", "Score", "Status", "Email", "Phone"]], use_container_width=True)
            
            # CSV Export
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Report (CSV)",
                data=csv,
                file_name=f"recruitment_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime='text/csv',
                use_container_width=True
            )
            
            # Outreach Section
            st.markdown("---")
            st.markdown("### 📬 Candidate Outreach")
            st.markdown("*Connect with candidates instantly*")
            
            col_left, col_right = st.columns([1, 1])
            with col_left:
                selected_candidate = st.selectbox("Select Candidate", df["Name"].unique())
                candidate_data = df[df["Name"] == selected_candidate].iloc[0]
                
                st.info(f"""
                    **📧 Email:** {candidate_data['Email']}
                    
                    **📱 Phone:** {candidate_data['Phone']}
                    
                    **⭐ Score:** {candidate_data['Score']}%
                    
                    **🏆 Status:** {candidate_data['Status']}
                """)
            
            with col_right:
                message_template = st.text_area(
                    "✏️ Message Template",
                    f"Dear {selected_candidate},\n\nThank you for applying to our organization. Based on your CV, you have been {candidate_data['Status']}.\n\nScore: {candidate_data['Score']}%\n\nBest regards,\nHR Team",
                    height=150
                )
                
                col_wa, col_email = st.columns(2)
                with col_wa:
                    if candidate_data['Phone'] != "N/A":
                        clean_phone = re.sub(r'[^\d+]', '', candidate_data['Phone'])
                        wa_link = f"https://wa.me/{clean_phone.lstrip('+')}?text={quote(message_template)}"
                        st.link_button("📱 Send WhatsApp", wa_link, use_container_width=True)
                    else:
                        st.button("📱 WhatsApp Unavailable", disabled=True, use_container_width=True)
                
                with col_email:
                    if candidate_data['Email'] != "N/A":
                        email_link = f"mailto:{candidate_data['Email']}?subject=Application Update&body={quote(message_template)}"
                        st.link_button("📧 Send Email", email_link, use_container_width=True)
                    else:
                        st.button("📧 Email Unavailable", disabled=True, use_container_width=True)
        
        st.session_state['processing'] = False
    elif uploaded_files:
        st.info("✨ Processing your CVs...")
    else:
        st.markdown("""
            <div style="text-align: center; padding: 3rem;">
                <h3 style="color: #d63384;">🌟 Ready to screen candidates?</h3>
                <p>Upload PDF CVs above to get started with AI-powered recruitment</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- APP START ---
if st.session_state['is_logged_in']:
    dashboard()
else:
    auth_page()
