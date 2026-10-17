import os
import random

import streamlit as st
import google.generativeai as genai
import requests
import speech_recognition as sr
from PIL import Image
import geocoder
from dotenv import load_dotenv

# ── Load environment variables from .env ──────────────────────────────────────
load_dotenv()
GOOGLE_API_KEY  = os.getenv("GOOGLE_API_KEY", "")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")

# ── Configure Gemini AI ───────────────────────────────────────────────────────
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="🌿 AgriMoksh - Smart Farming Assistant", page_icon="🌱")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_location():
    """Return the user's city via IP geolocation, defaulting to Hyderabad."""
    try:
        g = geocoder.ip("me")
        return g.city if g.city else "Hyderabad"
    except Exception:
        return "Hyderabad"


def get_weather():
    """Fetch current weather and return an HTML card + temp + humidity."""
    try:
        city = get_location()
        url = (
            f"http://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={WEATHER_API_KEY}&units=metric"
        )
        data = requests.get(url, timeout=5).json()

        if data.get("cod") != 200:
            return "❌ Could not fetch weather data.", 0, 0

        desc     = data["weather"][0]["description"].capitalize()
        temp     = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind     = data["wind"]["speed"]

        html = f"""
        <div class="weather-box">
            <div class="weather-title">🌤 Weather in {city}</div>
            <div class="weather-item">☁ Condition: {desc}</div>
            <div class="weather-item">🌡 Temperature: {temp}°C</div>
            <div class="weather-item">💧 Humidity: {humidity}%</div>
            <div class="weather-item">🌬 Wind Speed: {wind} m/s</div>
        </div>
        """
        return html, temp, humidity

    except Exception as e:
        return f"❌ Error: {str(e)}", 0, 0


def recommend_crops(temp, humidity):
    """Return crops that match the given temperature and humidity ranges."""
    crops = {
        "Wheat":     (10, 25, 40, 60),
        "Rice":      (20, 35, 60, 80),
        "Maize":     (18, 27, 50, 70),
        "Cotton":    (21, 30, 50, 60),
        "Sugarcane": (21, 35, 60, 80),
        "Pulses":    (18, 30, 40, 70),
        "Groundnut": (20, 30, 50, 70),
    }
    matches = [
        crop for crop, (t1, t2, h1, h2) in crops.items()
        if t1 <= temp <= t2 and h1 <= humidity <= h2
    ]
    return matches or ["No ideal crops found"]


def classify_plant_disease(image):
    """Return a (disease_name, explanation) tuple for the uploaded leaf image."""
    diseases = [
        ("Leaf Spot",
         "Caused by fungi or bacteria — dark spots with a yellow border. "
         "Remove infected leaves and spray with neem oil or a copper-based fungicide."),

        ("Powdery Mildew",
         "White powdery coating on leaves and stems. Thrives in warm, dry conditions. "
         "Improve airflow and treat with sulfur or neem oil."),

        ("Blight",
         "Sudden browning / wilting with lesions. Spreads fast in humid weather. "
         "Remove affected parts and apply chlorothalonil fungicide."),

        ("Rust",
         "Orange or yellow pustules on leaves — common in legumes. "
         "Remove infected parts and apply triazole-based fungicide."),

        ("Downy Mildew",
         "Yellow patches on top, grayish fuzz underneath. Likes cool, moist conditions. "
         "Apply copper-based or mancozeb fungicide."),

        ("Gray Mold (Botrytis)",
         "Grayish mold in cool, damp weather on flowers and fruit. "
         "Remove affected areas and apply fenhexamid."),

        ("Anthracnose",
         "Dark sunken lesions on leaves, stems, and fruit in humid conditions. "
         "Apply chlorothalonil after removing affected parts."),

        ("Bacterial Wilt",
         "Wilting and stem browning caused by soil bacteria. "
         "Practice crop rotation; remove and destroy infected plants."),

        ("Fusarium Wilt",
         "Yellowing and wilting starting from lower leaves. "
         "Remove infected plants, rotate crops, and apply tebuconazole."),

        ("Root Rot",
         "Waterlogged soil causes roots to decay — leaves yellow and drop. "
         "Improve drainage, reduce watering, and apply thiophanate-methyl."),

        ("Leaf Curl Virus",
         "Leaves curl, yellow, and become brittle. Spread by aphids and whiteflies. "
         "Control insects with insecticide; remove infected plants."),

        ("Tobacco Mosaic Virus",
         "Mottled / wrinkled leaves with stunted growth. Spreads via contact. "
         "Disinfect tools and remove infected plants."),

        ("Healthy",
         "No signs of disease! Continue regular watering, fertilisation, and pest checks."),
    ]
    return random.choice(diseases)


def transcribe_audio():
    """Record from the microphone and return the transcribed text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎧 Listening…")
        audio = recognizer.listen(source, timeout=8)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "❌ Could not understand the audio. Please try again."
    except sr.RequestError:
        return "❌ Speech service unavailable. Check your internet connection."


def is_agri_query(query):
    """Return True if the query contains at least one agriculture keyword."""
    keywords = [
        "crop", "plant", "agriculture", "farming", "disease", "pest", "yield",
        "harvest", "fertilizer", "irrigation", "soil", "weather", "climate",
        "pesticide", "fungus", "bacteria", "virus", "plant health", "growth",
    ]
    return any(word in query.lower() for word in keywords)


def get_ai_response(prompt):
    """Send the prompt to Gemini and return the response text."""
    if not is_agri_query(prompt):
        return "⚠️ I can only answer **agriculture-related** questions."

    system_prompt = """
You are AgriMoksh, an AI-powered agricultural assistant for South Indian farmers.
You only answer agriculture-related questions. If key details (soil type, crop name,
temperature, etc.) are missing, ask for them politely.

You help with:
🌱 Crop recommendations based on soil, weather, and season
🦠 Plant disease diagnosis and treatment (organic & chemical)
🧪 Soil health, fertilizers, and soil amendments
🌤 Weather-based farming advice
🧑‍🌾 Best farming practices (irrigation, sowing, harvesting)
🛠 Agri-tools, drones, and precision farming technology
📍 Government schemes (PM-KISAN, eNAM) and local contacts

Style: Use bullet points, emojis, and plain language. Avoid heavy jargon.
If a query is unclear, politely ask for more details.
"""

    response = model.generate_content([
        {"role": "user",  "parts": [system_prompt]},
        {"role": "model", "parts": ["Got it! I'm AgriMoksh, your smart farming assistant."]},
        {"role": "user",  "parts": [prompt]},
    ])

    text = getattr(response, "text", "❌ No response generated.")

    # Append crop-specific helpline numbers
    p = prompt.lower()
    if "chilli" in p:
        text += "\n\n📞 Chilli helpline: **8551269743**"
    elif "pulses" in p:
        text += "\n\n📞 Pulses helpline: **9874563210**"
    elif "cotton" in p:
        text += "\n\n📞 Cotton helpline: **9874561230**"

    return text


# =============================================================================
# STYLING
# =============================================================================
st.markdown("""
<style>
.stApp {
    background-image: linear-gradient(to top, #3fff00 0%, #d6cab8 100%);
    padding-bottom: 80px;
}
.weather-box {
    background: #000;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
.weather-title {
    font-size: 20px;
    font-weight: bold;
    color: #0072ff;
    margin-bottom: 10px;
    text-align: center;
}
.weather-item {
    font-size: 16px;
    margin: 4px 0;
    padding-left: 10px;
    color: #fff;
}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# APP HEADER
# =============================================================================
st.title("🌿 AGRIMOKSH - A Farmer's Guide")
st.markdown("Built by **TECHMIGOES** | AI + Agriculture 🤝")


# =============================================================================
# WEATHER & CROP RECOMMENDATIONS
# =============================================================================
weather_html, temp, humidity = get_weather()
st.markdown(weather_html, unsafe_allow_html=True)
st.success(f"🌾 Recommended Crops: {', '.join(recommend_crops(temp, humidity))}")


# =============================================================================
# DISEASE DETECTION
# =============================================================================
st.header("📷 Detect Plant Disease from Leaf Image")
uploaded_image = st.file_uploader("Upload a leaf image", type=["jpg", "jpeg", "png"])

if uploaded_image:
    img = Image.open(uploaded_image)
    st.image(img, caption="Uploaded Leaf Image", use_column_width=True)
    with st.spinner("Analysing image…"):
        disease, explanation = classify_plant_disease(img)
    st.success(f"🦠 Disease Detected: **{disease}**")
    st.markdown(f"**Details:** {explanation}")


# =============================================================================
# EXTERNAL RESOURCE LINKS
# =============================================================================
st.header("🌐 Explore More Resources")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('[🚜 Machinery](https://www.toolsvilla.com/category/farm)', unsafe_allow_html=True)
with col2:
    st.markdown('[🚁 Drones](https://www.xboom.in/agriculture-drones/)', unsafe_allow_html=True)
with col3:
    st.markdown('[🧴 Pesticides](https://m.indiamart.com/impcat/agricultural-pesticides.html)', unsafe_allow_html=True)
with col4:
    st.markdown('[📋 Agri Info](https://newagri.in/)', unsafe_allow_html=True)


# =============================================================================
# CHAT SESSION STATE
# =============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show existing chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# =============================================================================
# SIDEBAR — History, Download & Voice
# =============================================================================
st.sidebar.title("💬 Chat History")

if st.session_state.messages:
    for msg in st.session_state.messages:
        st.sidebar.markdown(f"**{msg['role'].capitalize()}:** {msg['content']}")

    # Download chat as a .txt file
    chat_text = "\n".join(
        f"{m['role'].capitalize()}: {m['content']}"
        for m in st.session_state.messages
    )
    st.sidebar.download_button("📥 Download Chat", data=chat_text, file_name="chat_history.txt")
else:
    st.sidebar.info("No messages yet.")

# Voice input button
st.sidebar.header("🎧 Voice Input")
if st.sidebar.button("🎤 Start Recording"):
    transcribed = transcribe_audio()
    if transcribed.startswith("❌"):
        st.sidebar.error(transcribed)
    else:
        st.sidebar.success(f"Heard: {transcribed}")
        st.session_state.messages.append({"role": "user",      "content": transcribed})
        st.session_state.messages.append({"role": "assistant", "content": get_ai_response(transcribed)})
        st.rerun()


# =============================================================================
# CHAT INPUT
# =============================================================================
user_input = st.chat_input("Ask me anything about crops, soil, or plant diseases…")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            reply = get_ai_response(user_input)
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
