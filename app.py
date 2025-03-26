import streamlit as st
import os
from openai import OpenAI
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="Meeting Insight",
    page_icon="📟",
    layout="centered"
)

# Initialize OpenAI client
client = OpenAI(
    api_key=st.secrets["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com"
)

# Initialize session state
if 'transcript_text' not in st.session_state:
    st.session_state.transcript_text = ""
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

def reset_app():
    """Reset the app to initial state"""
    st.session_state.transcript_text = ""
    st.session_state.uploaded_file = None
    st.session_state.analysis_results = None
    st.cache_data.clear()
    for filename in os.listdir():
        if filename.endswith(".txt"):
            try:
                os.remove(filename)
            except:
                pass

def analyze_transcript(transcript, language):
    """Analyze transcript using DeepSeek API"""
    base_prompt = st.secrets["PROMPT"]
    full_prompt = f"{base_prompt}\n\nOutput Language: {language}\n\nTranscript:\n{transcript}"
    
    messages = [{"role": "user", "content": full_prompt}]
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            max_tokens=4000,
            temperature=1.3,
            top_p=0.9,
            stream=False  # Streaming disabled
        )
        
        # Store the result in session state
        st.session_state.analysis_results = {
            "final_answer": response.choices[0].message.content
        }
        
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"Error analyzing transcript: {str(e)}")
        return None

# App title and description
st.title("📟 Meeting Insight")
st.divider()
st.markdown("""**Analyze your call transcripts to extract:**
- Key discussion topics with timestamps
- Assigned tasks and responsible persons
- Important decisions and action items
- Mentioned tools and platforms
""")
st.divider()

# Language selection
language = st.selectbox(
    "Select output language",
    ("English", "Spanish", "Italian", "French", "German"),
    index=0
)

# Input method selection
input_method = st.radio(
    "How would you like to provide the transcript?",
    ("Paste text", "Upload TXT file"),
    horizontal=True
)

# Handle input based on selection
transcript = ""
if input_method == "Paste text":
    st.session_state.transcript_text = st.text_area(
        "Paste your transcript here",
        height=300,
        value=st.session_state.transcript_text
    )
    transcript = st.session_state.transcript_text
else:
    uploaded_file = st.file_uploader(
        "Upload a TXT file",
        type=["txt"],
        accept_multiple_files=False
    )
    
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        transcript = uploaded_file.getvalue().decode("utf-8")
        st.success("File uploaded successfully!")
        with st.expander("Preview uploaded file"):
            st.text(transcript[:1000] + ("..." if len(transcript) > 1000 else ""))

# Analysis button
if st.button("Analyze Transcript", disabled=not transcript.strip()):
    if not transcript.strip():
        st.warning("Please provide a transcript to analyze")
    else:
        with st.spinner(f"Analyzing transcript in {language}...", show_time=True):
            result = analyze_transcript(transcript, language)
            if result:
                st.markdown("### Analysis Results")
                st.markdown(result)
                st.success("Analysis complete!")

# Reset button
if st.button("New transcript"):
    reset_app()
    st.rerun()

# Footer
st.markdown("---")
st.markdown("❤️ Made with love by [Johnometalman](https://www.johnometalman.me)")
