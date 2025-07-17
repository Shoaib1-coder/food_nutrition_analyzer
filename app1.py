import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import os

# --- Set Gemini API Key ---

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
  # Replace with your actual API key

# --- Initialize Gemini model ---
model = genai.GenerativeModel("gemini-2.5-pro")

# --- Streamlit UI ---
st.set_page_config(page_title="Food Analyzer", layout="wide")

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
   
    }
    .spinner {
        color: #007BFF;
    }
    </style>
    <div class='title'>Fruit,Vegetable & Meat Analyzer</div>
    <div class='subtitle'>Upload an image containing fruits, vegetables, or meat to get detailed nutrition info.</div>
    """,
    unsafe_allow_html=True
)

# --- File Upload ---
uploaded_file = st.file_uploader("📤 Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
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
    st.markdown("<div class='result-box'><h4>🧾 Nutritional Analysis Result:</h4></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='result-box'><pre>{response.text}</pre></div>", unsafe_allow_html=True)

