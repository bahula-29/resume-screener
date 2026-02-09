# 📄 AI Resume Screener

A simple and practical **AI-powered Resume Screening web app** built using **Streamlit** and **Google Gemini API**.

This app helps recruiters or users quickly evaluate multiple resumes against a given job description and shortlist the most relevant candidates.
---
🌐 Live Demo

You can try the live version of this app here:

👉 Streamlit App Link: https://your-streamlit-app-link-here
---

## 🌟 What This Project Does

Instead of manually reading resumes, this app:

1. Takes a **job description** as input
2. Accepts **multiple resumes** (PDF, DOCX, TXT, or images)
3. Uses AI to:

   * Read resume content
   * Compare it with the job description
   * Assign a **match score (0–100)**
   * Extract basic candidate details
4. Displays ranked results and allows **Excel download**

---

## 🚀 Key Features

* Upload multiple resumes at once
* Supports PDF, DOCX, TXT, JPG, PNG
* AI-based resume vs job description matching
* Candidate details extraction:

  * Name
  * Email
  * Phone
  * Location
* Relevance score with short explanation
* Keyword matching
* Filter candidates by:

  * Location
  * Minimum score
* Download shortlisted candidates as Excel

---

## 🛠 Tech Stack

* Python
* Streamlit
* Google Gemini API
* PyMuPDF (PDF reading)
* python-docx
* Pandas
* OpenPyXL

---

## 📂 Supported Resume Formats

* `.pdf`
* `.docx`
* `.txt`
* `.png`, `.jpg`, `.jpeg` (image resumes using AI OCR)

---

## ⚙️ How to Run the Project

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/ai-resume-screener.git
cd ai-resume-screener
```

### 2️⃣ Install Required Libraries

```bash
pip install -r requirements.txt
```

### 3️⃣ Add Google API Key

Create this file:

```
.streamlit/secrets.toml
```

Add your API key:

```toml
GOOGLE_API_KEY = "your_google_gemini_api_key"
```

### 4️⃣ Run the App

```bash
streamlit run main.py
```

---

## 📊 Output You Get

* Ranked list of candidates
* Match score with reasoning
* Matching skills/keywords
* Downloadable Excel file of shortlisted candidates

---

## ⚠️ Notes

* Internet connection required (AI API)
* API usage depends on Gemini quota
* Designed mainly for demo and educational use

---

## 🌱 Future Improvements

* Login system for recruiters
* Resume database storage
* Skill-wise scoring
* Interview recommendation feature

---

## 👨‍💻 Author

Built with curiosity and learning mindset using Streamlit and Generative AI.

Feel free to fork, improve, and use this project 🚀
