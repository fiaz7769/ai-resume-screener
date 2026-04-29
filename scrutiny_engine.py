import streamlit as st
import PyPDF2
import pandas as pd
import plotly.express as px

# --- FUNCTION: Detailed Text Search & Highlighting ---
def get_analysis(text, skills):
    text_lower = text.lower()
    analysis = {}
    for skill in skills:
        count = text_lower.count(skill.lower())
        analysis[skill] = count
    return analysis

# --- UI CONFIGURATION ---
st.set_page_config(page_title="AI Resume Intelligence", layout="wide")

# Styling
st.markdown("""
    <style>
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #4facfe 0%, #00f2fe 100%); }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 AI Resume Intelligence Dashboard")

# SIDEBAR
st.sidebar.header("🎯 Recruitment Criteria")
skills_input = st.sidebar.text_input("Skills to scan (comma separated)", "Python, SQL, Communication")
REQUIRED_SKILLS = [s.strip() for s in skills_input.split(",") if s.strip()]

# MAIN SECTION
uploaded_files = st.file_uploader("Upload Resumes (Multiple PDFs)", type="pdf", accept_multiple_files=True)

if uploaded_files:
    all_data = []
    
    for file in uploaded_files:
        # Extract Text
        reader = PyPDF2.PdfReader(file)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() or ""
            
        # Analyze
        skill_counts = get_analysis(full_text, REQUIRED_SKILLS)
        found_skills = [s for s, count in skill_counts.items() if count > 0]
        score = (len(found_skills) / len(REQUIRED_SKILLS)) * 100 if REQUIRED_SKILLS else 0
        
        all_data.append({
            "Candidate": file.name,
            "Score %": round(score, 1),
            "Skills Found": ", ".join(found_skills),
            "Skill Count": sum(skill_counts.values()),
            "Full Text": full_text
        })
    
    df = pd.DataFrame(all_data)
    
    # --- VISUALS ---
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("🏆 Candidate Leaderboard")
        # Top candidates filter
        st.dataframe(df[["Candidate", "Score %", "Skills Found", "Skill Count"]].sort_values(by="Score %", ascending=False), use_container_width=True)

    with col2:
        st.subheader("📊 Performance Analytics")
        fig = px.funnel(df.sort_values(by="Score %"), x="Score %", y="Candidate", title="Hiring Funnel")
        st.plotly_chart(fig, use_container_width=True)

    # --- ADVANCED: INDIVIDUAL ANALYSIS ---
    st.divider()
    st.subheader("🔍 Deep Dive - Candidate Review")
    selected_candidate = st.selectbox("Select a candidate to see their resume text", df["Candidate"].unique())
    
    if selected_candidate:
        candidate_info = df[df["Candidate"] == selected_candidate].iloc[0]
        st.write(f"**Found Skills:** {candidate_info['Skills Found']}")
        
        # Simple Highlighting Simulation
        display_text = candidate_info['Full Text']
        st.text_area("Resume Content", display_text[:2000], height=300)

else:
    st.info("Awaiting file uploads... Use the uploader above.")
    