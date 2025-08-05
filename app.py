import streamlit as st
import google.generativeai as genai
import io
import fitz  # PyMuPDF
import docx
import json  # Import the json library to handle the AI's response
import pandas as pd  # Import pandas for Excel export

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="📄",
    layout="wide"
)


# --- Helper Functions ---

def get_file_text(uploaded_file):
    """
    Reads an uploaded file (PDF, DOCX, TXT, PNG, JPG) and returns its text content.
    For images, it uses Gemini to perform OCR.
    """
    text = ""
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()

        if file_extension == "pdf":
            pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            for page in pdf_document:
                text += page.get_text()
            pdf_document.close()

        elif file_extension == "docx":
            doc = docx.Document(io.BytesIO(uploaded_file.read()))
            for para in doc.paragraphs:
                text += para.text + "\n"

        elif file_extension == "txt":
            text = uploaded_file.read().decode("utf-8")

        elif file_extension in ["png", "jpg", "jpeg"]:
            model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")
            image_parts = [{"mime_type": uploaded_file.type, "data": uploaded_file.getvalue()}]
            prompt = "You are an expert OCR (Optical Character Recognition) service. Extract all text from the following image of a resume."
            response = model.generate_content([prompt, image_parts[0]])
            text = response.text

    except Exception as e:
        st.error(f"Error reading {uploaded_file.name}: {e}")
        return None

    return text


def get_jd_match_from_gemini(job_description, resume_text):
    """
    Calls the Gemini API to get a relevance score, justification, and contact info.
    """
    prompt = f"""
    You are an expert HR professional and data extraction specialist.
    Your task is to analyze the following resume against the provided job description.

    Job Description:
    ---
    {job_description}
    ---

    Resume:
    ---
    {resume_text}
    ---

    Based on your analysis, provide the following in JSON format:
    1. "name": The full name of the candidate. If not found, return "Not Found".
    2. "email": The candidate's email address. If not found, return "Not Found".
    3. "phone": The candidate's phone number. If not found, return "Not Found".
    4. "score": A relevance score from 0 to 100 compared to the job description.
    5. "justification": A brief, one-sentence justification for the score.
    6. "location": The candidate's location (City and State, if available). If not found, return "Not Found".
    7. "matching_keywords": A list of the top 3-5 keywords from the job description found in the resume.
    """

    generation_config = {
        "response_mime_type": "application/json",
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "name": {"type": "STRING"},
                "email": {"type": "STRING"},
                "phone": {"type": "STRING"},
                "score": {"type": "NUMBER"},
                "justification": {"type": "STRING"},
                "location": {"type": "STRING"},
                "matching_keywords": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"}
                }
            },
            "required": ["name", "email", "phone", "score", "justification", "location", "matching_keywords"]
        }
    }

    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-preview-05-20",
            generation_config=generation_config
        )
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        st.error(f"An error occurred with the AI model: {e}")
        return None


# --- Streamlit App UI ---

st.title("📄 AI Resume Screener")
st.markdown("Evaluate multiple resumes against a job description to find the best candidates.")
st.divider()

# Initialize session state for results
if 'results' not in st.session_state:
    st.session_state.results = []

# --- API Key Configuration ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    st.error("🚨 **API Key Not Found!** Please add your GOOGLE_API_KEY to the secrets.toml file.")
    st.stop()

# --- Sidebar for Inputs ---
with st.sidebar:
    st.subheader("1. Enter Details")
    job_description = st.text_area("Paste the Job Description", height=200, placeholder="Seeking a Python developer...")

    st.subheader("2. Upload Resumes")
    uploaded_files = st.file_uploader(
        "Choose resume files",
        type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
        accept_multiple_files=True
    )

    if st.button("Evaluate Resumes", type="primary", use_container_width=True):
        if job_description and uploaded_files:
            with st.spinner(f"Evaluating {len(uploaded_files)} resume(s)..."):
                new_results = []
                # Added more verbose feedback during the loop
                for file in uploaded_files:
                    st.info(f"Processing: {file.name}")
                    resume_text = get_file_text(file)
                    if resume_text:
                        analysis = get_jd_match_from_gemini(job_description, resume_text)
                        if analysis:
                            new_results.append({"filename": file.name, "analysis": analysis})
                            st.success(f"Successfully evaluated: {file.name}")
                        else:
                            st.error(f"Could not get AI analysis for: {file.name}")
                    else:
                        st.warning(f"Could not extract text from: {file.name}")
                st.session_state.results = new_results
        else:
            st.warning("Please provide a job description and upload at least one resume.")

st.subheader("3. Screening Evaluation")

# --- Filtering and Display Logic ---
if st.session_state.results:
    # --- Filtering Controls ---
    st.markdown("#### Filter Your Results")
    col1, col2 = st.columns(2)
    with col1:
        target_location = st.text_input("Filter by Location", placeholder="e.g., Hyderabad")
    with col2:
        min_score = st.number_input("Minimum Match Score", min_value=0, max_value=100, value=70, step=5)

    # --- Filtering Logic ---
    filtered_results = st.session_state.results

    if target_location:
        filtered_results = [
            result for result in filtered_results
            if target_location.lower() in result['analysis'].get('location', '').lower()
        ]

    filtered_results = [
        result for result in filtered_results
        if result['analysis'].get('score', 0) >= min_score
    ]

    sorted_results = sorted(filtered_results, key=lambda x: x['analysis'].get('score', 0), reverse=True)

    # --- Display Results ---
    if sorted_results:
        # --- Excel Download Button ---
        export_data = []
        for result in sorted_results:
            analysis = result['analysis']
            export_data.append({
                "Name": analysis.get('name', 'N/A'),
                "Email": analysis.get('email', 'N/A'),
                "Phone": analysis.get('phone', 'N/A'),
                "Score": analysis.get('score', 0),
                "Location": analysis.get('location', 'N/A'),
                "Filename": result['filename']
            })
        df = pd.DataFrame(export_data)


        # Function to convert DataFrame to Excel in memory
        @st.cache_data
        def to_excel(df):
            output = io.BytesIO()
            # Note: You might need to run 'pip install openpyxl'
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Screening Results')
            processed_data = output.getvalue()
            return processed_data


        excel_data = to_excel(df)

        st.download_button(
            label="📥 Download Results as Excel",
            data=excel_data,
            file_name="resume_screening_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.divider()
        # --- End of Download Button Logic ---

        st.success(f"Displaying {len(sorted_results)} matching candidate(s).")
        for result in sorted_results:
            analysis_data = result['analysis']
            score = analysis_data.get('score', 0)
            location = analysis_data.get('location', 'Not Found')

            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{result['filename']}**")
                    st.markdown(f"📍 **Location:** {location}")
                with col2:
                    st.metric("Match Score", f"{score}%")

                st.markdown(f"**Justification:** *{analysis_data.get('justification', 'N/A')}*")

                keywords = analysis_data.get("matching_keywords", [])
                if keywords:
                    st.markdown("**Matching Keywords Found:**")
                    keywords_html = "".join([
                                                f"<span style='background-color:#E0E0E0; color:#333; border-radius:5px; padding: 2px 8px; margin: 2px;'>{kw}</span>"
                                                for kw in keywords])
                    st.markdown(keywords_html, unsafe_allow_html=True)
    else:
        st.warning("No resumes match your current filter criteria.")
else:
    st.info("Your evaluation results will appear here after you upload resumes and click 'Evaluate'.")
