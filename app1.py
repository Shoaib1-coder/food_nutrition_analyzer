import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import os

# --- Set Gemini API Key ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Replace with your actual API key in your environment variables or secrets

# --- Initialize Gemini model ---
model = genai.GenerativeModel("gemini-2.5-pro")

# --- Streamlit UI Configuration ---
st.set_page_config(page_title="Food Analyzer", layout="wide")

# --- Custom HTML and CSS ---
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
    <div class='title'>Fruit, Vegetable & Meat Analyzer</div>
    <div class='subtitle'>Upload or capture an image to get detailed nutrition info.</div>
    """,
    unsafe_allow_html=True
)

# --- Upload or Photo Capture UI ---
st.markdown("### 📤 Upload from gallery or take a new photo")

upload_option = st.radio("Select image source:", ["📁 Upload from Gallery", "📸 Take a Photo"])

image_file = None

if upload_option == "📁 Upload from Gallery":
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png", "webp", "bmp", "tiff", "gif", "jfif"])
    if uploaded_file is not None:
        image_file = uploaded_file

elif upload_option == "📸 Take a Photo":
    if 'camera_triggered' not in st.session_state:
        st.session_state.camera_triggered = False

    if not st.session_state.camera_triggered:
        if st.button("📸 Take a Photo Now"):
            st.session_state.camera_triggered = True
            st.experimental_rerun()
    else:
        camera_file = st.camera_input("📸 Capture your food image:")
        if camera_file is not None:
            image_file = camera_file


# --- Process the image if available ---
if image_file is not None:
    try:
        image = Image.open(image_file)
        if image.mode != "RGB":
            image = image.convert("RGB")

        st.image(image, caption="📸 Uploaded Image", use_container_width=True)

        # Convert image to bytes
        image_bytes_io = io.BytesIO()
        image.save(image_bytes_io, format='PNG')
        image_bytes = image_bytes_io.getvalue()

        # --- Prompt for Gemini ---
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
- Calculate the **combined calories per 100g** (estimate based on items)
- List **all vitamins combined**
- Present the information in a clear, readable format
"""

        # --- Get Gemini Response ---
        with st.spinner("🔍 Analyzing image with Gemini..."):
            response = model.generate_content(
                contents=[
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/png", "data": image_bytes}}
                ],
                generation_config={"temperature": 0.4}
            )

        # --- Display Results ---
        st.markdown("### 🧾 Nutritional Analysis Result")
        st.markdown(f"<div class='result-box'>{response.text}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error: {e}")
