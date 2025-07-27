import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import os

# ------------------ CONFIGURATION ------------------

# Set page configuration
st.set_page_config(page_title="Food Analyzer", layout="wide")

# Configure Gemini API Key (from environment or Streamlit secrets)
api_key = os.getenv("GEMINI_API_KEY", st.secrets.get("GEMINI_API_KEY", ""))
if not api_key:
    st.error("🚨 Gemini API key not found. Set it in environment variables or Streamlit secrets.")
    st.stop()
genai.configure(api_key=api_key)

# Initialize Gemini model
model = genai.GenerativeModel("gemini-2.5-pro")

# ------------------ STYLES & HEADERS ------------------

st.markdown(
    """
    <style>
    .title {
        font-weight: bold;
        font-size: 6vh;
        color: #4CAF50;
        text-align: center;
        margin-top: 20px;
    }
    .subtitle {
        text-align: center;
        margin-bottom: 30px;
        font-size: 4vh;
        color: #555;
    }
    .result-box {
        background-color: #f9f9f9;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #ccc;
        font-family: monospace;
        white-space: pre-wrap;
    }
    </style>
    <div class='title'>🥦 Fruit, Vegetable & Meat Analyzer122</div>
    <div class='subtitle'>Upload an image to get detailed nutrition info</div>
    """,
    unsafe_allow_html=True
)

# ------------------ IMAGE UPLOAD ------------------

st.markdown("### 📤 Upload an image")

uploaded_file = st.file_uploader(
    "Choose an image",
    type=["jpg", "jpeg", "png", "webp", "bmp", "tiff", "gif", "jfif"]
)

# ------------------ IMAGE ANALYSIS ------------------

if uploaded_file:
    try:
        # Load and display image
        image = Image.open(uploaded_file)
        if image.mode != "RGB":
            image = image.convert("RGB")
        st.image(image, caption="📸 Uploaded Image", use_container_width=True)

        # Convert image to bytes
        image_bytes_io = io.BytesIO()
        image.save(image_bytes_io, format='PNG')
        image_bytes = image_bytes_io.getvalue()

        # Prompt for Gemini
        prompt = """
You are a nutrition expert.

Analyze this image and:
- Detect and list **all fruits, vegetables, and meat items** in the image.
- For **each item**, provide:
  - Name
  - Taste description
  - Calories per 100g
  - Vitamins present
  - Key nutritional benefits

Then:
- Count the **total number of unique items**
- Calculate the **combined calories per 100g**
- List **all vitamins combined**
- Present the information in a clear, readable format
"""

        # Request Gemini response
        with st.spinner("🔍 Analyzing image with Gemini..."):
            response = model.generate_content(
                contents=[
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/png", "data": image_bytes}}
                ],
                generation_config={"temperature": 0.4}
            )

        # Display response
        st.markdown("### 🧾 Nutritional Analysis Result")
        st.markdown(f"<div class='result-box'>{response.text}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Failed to process image: {e}")

