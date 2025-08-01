import streamlit as st
import pandas as pd
import os
from PyPDF2 import PdfReader
import docx

st.set_page_config(page_title="Fake Job Detector", layout="wide")
st.title("🛡️ Fake Job Detector")
st.markdown("Detect suspicious job postings from various document types.")

# Define suspicious keywords
SUSPICIOUS_KEYWORDS = [
    "100% placement", "guaranteed job", "urgent requirement", "money required",
    "registration fee", "training fee", "deposit", "pay to apply", "no interview",
    "earn from home", "easy money", "investment", "data entry work", "captcha work",
    "whatsapp group job", "telegram job", "bitcoin", "crypto"
]

def is_suspicious(text):
    text = text.lower()
    return any(keyword in text for keyword in SUSPICIOUS_KEYWORDS)

def read_pdf(file):
    pdf = PdfReader(file)
    text = ''
    for page in pdf.pages:
        text += page.extract_text() or ''
    return text

def read_docx(file):
    doc = docx.Document(file)
    return '\n'.join([para.text for para in doc.paragraphs])

def read_txt(file):
    return file.read().decode('utf-8', errors='ignore')

def extract_job_descriptions(uploaded_file):
    ext = os.path.splitext(uploaded_file.name)[-1].lower()
    if ext == '.csv':
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"CSV could not be read: {e}")
            return None
    elif ext == '.pdf':
        text = read_pdf(uploaded_file)
        df = pd.DataFrame({"job_description": [text]})
    elif ext == '.docx':
        text = read_docx(uploaded_file)
        df = pd.DataFrame({"job_description": [text]})
    elif ext == '.txt':
        text = read_txt(uploaded_file)
        df = pd.DataFrame({"job_description": [text]})
    else:
        st.error("Unsupported file format.")
        return None
    return df

# --- File Upload ---
uploaded_file = st.file_uploader("Upload job post document (.csv, .pdf, .docx, .txt)", type=["csv", "pdf", "docx", "txt"])

if uploaded_file:
    df = extract_job_descriptions(uploaded_file)
    if df is not None:
        st.subheader("📊 Dataset Preview")
        st.dataframe(df.head(), use_container_width=True)

        # --- Job Description Column Selector (if needed) ---
        if "job_description" not in df.columns:
            selected_col = st.selectbox("Select the column containing job descriptions", df.columns)
            df["job_description"] = df[selected_col]
        
        # --- Clean Data ---
        df["job_description"] = df["job_description"].astype(str)
        df = df[df["job_description"].str.strip() != ""]

        # --- Search Bar ---
        st.subheader("🔍 Search Job Descriptions")
        search_query = st.text_input("Enter keywords to search")

        # --- Suspicious Classification ---
        df["suspicious"] = df["job_description"].apply(is_suspicious)

        # --- Display Tables ---
        suspicious_df = df[df["suspicious"] == True]
        authentic_df = df[df["suspicious"] == False]

        if search_query:
            suspicious_df = suspicious_df[suspicious_df["job_description"].str.contains(search_query, case=False, na=False)]
            authentic_df = authentic_df[authentic_df["job_description"].str.contains(search_query, case=False, na=False)]

        st.subheader("🚨 Malicious Job Posts")
        if not suspicious_df.empty:
            st.dataframe(suspicious_df[["job_description"]], use_container_width=True)
        else:
            st.info("No suspicious job posts found.")

        st.subheader("✅ Authentic Job Posts")
        if not authentic_df.empty:
            st.dataframe(authentic_df[["job_description"]], use_container_width=True)
        else:
            st.info("No authentic job posts found.")

# --- Footer ---
st.markdown("---")
st.markdown("Made with ❤️ by [Krish Kashyap](https://github.com/kashyapkrish101)", unsafe_allow_html=True)
