import streamlit as st
from backend import process_video

st.set_page_config(page_title="Accent Classifier", page_icon="🗣️", layout="centered")

# --- HEADER ---
st.markdown(
    """
    <h1 style='text-align: center; color: #4F8BF9;'>🗣️ Accent Classifier App</h1>
    <p style='text-align: center; font-size:18px;'>Upload or link a video file and we'll analyze the speaker's English accent.</p>
    """,
    unsafe_allow_html=True
)

# --- INPUT METHOD ---
st.sidebar.header("Choose Input Method")
input_method = st.sidebar.radio("Select input type:", ("🌐 Video URL (.mp4)", "📁 Upload local .mp4 file"))

# --- USER INPUT ---
video_url = None
uploaded_file = None

with st.container():
    if input_method == "🌐 Video URL (.mp4)":
        st.markdown("#### 🔗 Paste a public video URL")
        video_url = st.text_input("Please provide a public video URL (e.g. Loom or direct MP4 link)")
    else:
        st.markdown("#### 📤 Upload a local video file")
        uploaded_file = st.file_uploader("Choose a .mp4 file", type=["mp4"])

# --- SUBMIT BUTTON ---
if st.button("🚀 Submit", use_container_width=True, disabled=st.session_state.get("processing", False)):
    if input_method == "🌐 Video URL (.mp4)":
        if not video_url:
            st.error("❌ Please provide a valid video URL.")
        else:
            with st.spinner("🔍 Processing video... please wait"):
                try:
                    result = process_video(video_url)
                    if "error" in result:
                        st.error(f"🚫 {result['error']}")
                    else:
                        st.success(f"🎯 **Accent:** `{result['accent']}`")
                        st.success(f"📊 **Confidence:** `{result['confidence']}%`")
                        st.info(f"📝 **Summary:** {result['summary']}")
                except Exception as e:
                    st.error("⚠️ Internal error during processing.")
                    st.exception(e)  # Dev mode
    else:
        if uploaded_file is None:
            st.error("❌ Please upload a video file.")
        else:
            # Save locally
            with open("temp_video.mp4", "wb") as f:
                f.write(uploaded_file.getbuffer())

            with st.spinner("🔍 Processing uploaded file... please wait"):
                try:
                    result = process_video("temp_video.mp4")
                    if "error" in result:
                        st.error(f"🚫 {result['error']}")
                    else:
                        st.success(f"🎯 **Accent:** `{result['accent']}`")
                        st.success(f"📊 **Confidence:** `{result['confidence']}%`")
                        st.info(f"📝 **Summary:** {result['summary']}")
                except Exception as e:
                    st.error(f"⚠️ Processing failed: {e}")

            # Cleanup
            import os
            if os.path.exists("temp_video.mp4"):
                os.remove("temp_video.mp4")

# --- FOOTER ---
st.markdown(
    """
    <hr>
    <div style='text-align: center; font-size:14px; color:gray'>
        Built by Md Zeeshan Faiz
    </div>
    """,
    unsafe_allow_html=True
)
