python -m pip install streamlit vsdx sentence-transformerspip install streamlit vsdx sentence-transformers torch pip install streamlit vsdx sentence-transformers torchpimport streamlit as st
from vsdx import VisioFile
from sentence_transformers import SentenceTransformer, util
import os

# AI Model load ho raha hai (Ye text ka matlab samajhta hai)
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

st.title("🤖 AI-Based Visio Screening System")
st.markdown("Upload your Visio diagram to screen it against requirements.")

# Sidebar for requirements
st.sidebar.header("Screening Criteria")
requirements = st.sidebar.text_area("Enter key skills or components to look for:", 
                                   "Database, Cloud, Security, Python")

uploaded_file = st.file_uploader("Choose a Visio (.vsdx) file", type="vsdx")

if uploaded_file and requirements:
    # Temporary file save karna taake vsdx read kar sakay
    with open("temp_file.vsdx", "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        # 1. Text Extraction
        extracted_text = []
        with VisioFile("temp_file.vsdx") as vis:
            for page in vis.pages:
                for shape in page.all_shapes:
                    if shape.text:
                        extracted_text.append(shape.text.strip())
        
        combined_text = " ".join(extracted_text)

        # 2. AI Screening (Similarity Score)
        emb1 = model.encode(combined_text, convert_to_tensor=True)
        emb2 = model.encode(requirements, convert_to_tensor=True)
        cosine_score = util.cos_sim(emb1, emb2)
        score_pct = int(cosine_score.item() * 100)

        # 3. Results Display
        st.subheader("Results")
        st.metric(label="Match Score", value=f"{score_pct}%")

        if score_pct > 70:
            st.success("✅ High Match: This diagram meets most requirements.")
        elif score_pct > 40:
            st.warning("⚠️ Partial Match: Some components are missing.")
        else:
            st.error("❌ Low Match: Requirements not found in diagram.")

        with st.expander("Show Extracted Data"):
            st.write(combined_text)

    except Exception as e:
        st.error(f"Error: {e}")
    
    finally:
        if os.path.exists("temp_file.vsdx"):
            os.remove("temp_file.vsdx")
            