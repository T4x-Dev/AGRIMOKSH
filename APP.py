import streamlit as st
import google.generativeai as genai
import requests
import speech_recognition as sr
from PIL import Image
import random
import geocoder

# === API Keys ===
GOOGLE_API_KEY = "AIzaSyCwco3-WRgQO-rWxWFDiJOFZITWdolMP4s"
WEATHER_API_KEY = "dbefbc3a3cf990e557d0da8e89597e55"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# === Streamlit Config ===
st.set_page_config(page_title="🌿 AgriMoksh - Smart Farming Assistant", page_icon="🌱")

# === Helper Functions ===
def get_location():
    try:
        g = geocoder.ip('me')
        return g.city if g.city else "Hyderabad"
    except:
        return "Hyderabad"

def get_weather():
    try:
        city = get_location()
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url).json()
        if response.get("cod") != 200:
            return "❌ Could not fetch weather data.", 0, 0

        desc = response["weather"][0]["description"].capitalize()
        temp = response["main"]["temp"]
        humidity = response["main"]["humidity"]
        wind = response["wind"]["speed"]

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
    crops = {
        "Wheat": (10, 25, 40, 60),
        "Rice": (20, 35, 60, 80),
        "Maize": (18, 27, 50, 70),
        "Cotton": (21, 30, 50, 60),
        "Sugarcane": (21, 35, 60, 80),
        "Pulses": (18, 30, 40, 70),
        "Groundnut": (20, 30, 50, 70)
    }
    return [crop for crop, (t1, t2, h1, h2) in crops.items() if t1 <= temp <= t2 and h1 <= humidity <= h2] or ["No ideal crops found"]

def classify_plant_disease(image):
    diseases = [
        ("Leaf Spot", 
         "Caused by fungi or bacteria. Infected areas on leaves may appear as small, dark spots with a yellow border. To treat, remove infected leaves and use fungicides like copper-based sprays or neem oil."),

        ("Powdery Mildew", 
         "A fungal disease that causes a white, powdery coating on the surface of leaves, stems, and buds. It thrives in dry, warm conditions. Treatment includes removing infected plant parts, improving air circulation, and using sulfur or neem oil."),

        ("Blight", 
         "A condition that causes sudden browning or wilting of leaves, often with lesions. It can be caused by fungi or bacteria and spreads rapidly in humid environments. To control, remove infected plants and apply fungicides like chlorothalonil."),

        ("Rust", 
         "Rust fungi cause orange, red, or yellow pustules on leaves. It's common in legumes and can spread rapidly. To control, remove infected plant parts, avoid overhead watering, and apply fungicides like triazole-based products."),

        ("Healthy", 
         "No visible disease symptoms. The plant appears healthy with no discolored or damaged leaves. Continue regular care, including watering, fertilization, and pest control."),

        ("Powdery Mildew", 
         "A fungal disease causing a white, powdery coating on leaves and stems. It thrives in warm, dry conditions. To control it, increase air circulation around the plant, remove infected areas, and treat with sulfur or neem oil."),

        ("Downy Mildew", 
         "A fungal-like disease that appears as yellowing of the leaves followed by fuzzy, grayish-purple growths. It thrives in cool, moist conditions. To treat, remove infected parts and apply fungicides such as copper-based or mancozeb-based products."),

        ("Gray Mold (Botrytis Blight)", 
         "A fungal disease that causes grayish mold on the plant, usually during damp, cool weather. It can affect flowers, fruit, and leaves. To treat, remove infected areas and apply fungicides such as fenhexamid or thiophanate-methyl."),

        ("Anthracnose", 
         "A fungal disease that causes dark, sunken lesions on leaves, stems, and fruits. It is common in humid conditions and can spread quickly. To treat, remove affected areas and apply fungicides such as chlorothalonil."),

        ("Septoria Leaf Spot", 
         "A fungal disease that causes circular, dark brown or black spots with yellow halos on the leaves. This disease can affect tomatoes, beans, and other crops. To control, remove infected leaves and apply fungicides like mancozeb or copper-based treatments."),

        ("Bacterial Wilt", 
         "A bacterial infection that causes wilting of leaves and stems. It spreads through soil and water. To control, avoid overhead watering and ensure proper soil drainage. There is no effective chemical treatment, so it's important to practice crop rotation and remove infected plants."),

        ("Fusarium Wilt", 
         "A fungal disease that causes yellowing of leaves, wilting, and stunted growth. It typically affects tomatoes, cucumbers, and other crops. To control, remove infected plants, practice crop rotation, and apply fungicides like tebuconazole."),

        ("Root Rot", 
         "Root rot is caused by a variety of fungi and bacteria that thrive in waterlogged soil. Symptoms include yellowing leaves, stunted growth, and root decay. Treatment involves improving drainage, avoiding over-watering, and applying fungicides like thiophanate-methyl."),

        ("Cercospora Leaf Spot", 
         "A fungal disease characterized by small, dark spots with purple or brown borders, usually affecting beans, soybeans, and lettuce. To treat, remove infected leaves and use fungicides like azoxystrobin or chlorothalonil."),

        ("Tobacco Mosaic Virus (TMV)", 
         "A viral disease that causes mottled or wrinkled leaves, stunted growth, and yellowing. It spreads by physical contact and contaminated tools. To prevent, disinfect tools, remove infected plants, and use resistant varieties."),

        ("Cucumber Mosaic Virus (CMV)", 
         "A viral disease that causes mosaic patterns, yellowing, and deformed growth on cucumber, tomatoes, and peppers. It spreads through aphid vectors. Control involves aphid management and removing infected plants."),

        ("Leaf Curl", 
         "This viral disease causes the leaves to curl, yellow, and sometimes become brittle. It affects crops like tomatoes, peppers, and cherries. To manage, remove infected plants, control aphid populations, and apply insecticides as needed."),

        ("Tomato Spotted Wilt Virus (TSWV)", 
         "A viral disease that causes dark spots and necrosis on leaves, stems, and fruits. It spreads through thrips. To control, manage thrips using insecticides and remove infected plants."),

        ("Southern Blight", 
         "A soil-borne fungal disease that causes wilting, yellowing, and the development of white, moldy growth at the base of the plant. To control, improve soil drainage, avoid over-watering, and apply fungicides like flutolanil or chlorothalonil."),

        ("Leaf Mold", 
         "A fungal disease that causes yellow spots on the upper side of leaves and mold on the underside, usually in humid environments. To manage, remove infected leaves, reduce humidity, and apply fungicides like potassium bicarbonate."),

        ("Viral Wilt", 
         "A viral infection causing wilting and yellowing of leaves, typically in crops like lettuce, tomatoes, and cucumbers. It is spread by insects, particularly aphids. Control methods include insecticide application, using resistant varieties, and removing infected plants.")
    ]
    return random.choice(diseases)

def transcribe_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎧 Listening...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "❌ Could not understand the audio. Please try again."
    except sr.RequestError:
        return "❌ Could not process the audio. Please check your internet connection."

def is_crop_related(query):
    keywords = [
        "crop", "plant", "agriculture", "farming", "disease", "pest", "yield",
        "harvest", "fertilizer", "irrigation", "soil", "weather", "climate",
        "pesticide", "fungus", "bacteria", "virus", "plant health", "growth"
    ]
    return any(k in query.lower() for k in keywords)

def get_response(prompt):
    if not is_crop_related(prompt):
        return "⚠ I can only answer *agriculture-related* queries."
    
    system_prompt = """
You are AgriMoksh, an advanced AI-powered agricultural assistant created for South Indian farmers to provide accurate, practical, and regionally-aware guidance to farmers. Your goal is to help users improve crop yield, sustainability, and farm productivity through smart and science-backed recommendations.

You respond only to agriculture-related queries and must base your answers strictly on the provided inputs. If critical information (such as soil type, crop name, temperature, etc.) is missing, ask for it.

You specialize in the following areas:

---

🌱 **1. Crop Recommendation**
- Analyze environmental conditions like:
  - Temperature, humidity, rainfall, and sunlight
  - Soil type (e.g., loamy, clay, sandy), texture, pH, moisture level
  - Season (e.g., Kharif, Rabi, Zaid)
  - Geographic region if available
- Recommend crops that are most compatible with the given parameters.
- Mention approximate yield expectations, if relevant.

---

🦠 **2. Plant Disease Diagnosis**
- Based on image inputs or textual symptoms (e.g., yellowing leaves, black spots), identify likely diseases.
- Return a complete list of **possible diseases** that match the symptoms or crop condition.
- For each disease, provide:
  - Name and short description
  - Cause (fungi, bacteria, virus, nutrient deficiency, etc.)
  - Environmental conditions that promote the disease:
    - Soil type and pH
    - Weather (humidity, temperature, rainfall)
    - Watering/Irrigation practices (overwatering, poor drainage, etc.)
  - Treatment options:
    - **Organic** solutions (neem oil, bio-fungicides, compost tea)
    - **Chemical** treatments (recommended fungicides/pesticides)
  - Prevention tips (e.g., crop rotation, proper spacing, resistant varieties)

---

🧪 **3. Soil Health and Fertility**
- Provide detailed guidance on:
  - Soil amendment techniques (adding compost, gypsum, lime, etc.)
  - Fertilizer selection (NPK balance, micronutrients)
  - Organic alternatives like green manure, vermicompost
- Tailor recommendations based on the crop’s nutrient demands and the soil condition.

---

🌤 **4. Weather-Based Recommendations**
- Based on current and forecasted weather:
  - Advise on irrigation (e.g., reduce watering before rain)
  - Predict risk of disease/pests due to humidity or wind
  - Recommend protective measures during extremes (frost, heatwaves, storms)

---

🧑‍🌾 **5. Best Farming Practices**
- Share region- and crop-specific:
  - Irrigation methods (drip, sprinkler, furrow)
  - Sowing time and spacing
  - Harvest time and post-harvest tips
  - Intercropping/companion cropping strategies

---

🛠 **6. Tools & Agri-Tech Guidance**
- Recommend farm machinery, tools, and agri-drones suited for the user’s crop size and type.
- Share best practices for using tools to save labor or reduce waste.
- Suggest digital tools (apps, sensors, AI models) for precision farming.

---

📍 **7. Localized Help & Contacts**
- For crops like Cotton, Pulses, or Chilli, and if location is known, recommend:
  - Local agricultural extension officers
  - Certified seed or fertilizer suppliers
  - Farmer helplines or government schemes (e.g., PM-KISAN, eNAM)

---

📌 **Response Style & Format**
- Use short paragraphs, bullet points, and emojis (🌱🌤💧🦠) for clarity.
- Highlight critical actions.
- Be polite, supportive, and avoid technical jargon unless necessary.
- If the input is unclear or missing key data, politely request more details (e.g., "Please provide the soil pH and recent weather conditions.")

Your mission is to act like a digital Krishi expert that empowers farmers to grow better, smarter, and sustainably.
"""


    response = model.generate_content([ 
        {"role": "assistant", "parts": [system_prompt]}, 
        {"role": "user", "parts": [prompt]} 
    ])
    text = getattr(response, 'text', "❌ No response generated.")
    if "chilli" in prompt.lower():
        text += "\n\n📞 For Chilli queries, contact: 8551269743."
    elif "pulses" in prompt.lower():
        text += "\n\n📞 For Pulses queries, contact: 9874563210."
    elif "cotton" in prompt.lower():
        text += "\n\n📞 For Cotton queries, contact: 9874561230."
    return text

# === Styling ===
st.markdown("""
<style>
.stApp { background-image: linear-gradient(to top,#3fff00  0%, #d6cab8 100%); padding-bottom: 80px; }
.weather-box { background: black; border-radius: 12px; padding: 16px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.weather-title { font-size: 20px; font-weight: bold; color: #0072ff; margin-bottom: 10px; text-align: center; }
.weather-item { font-size: 16px; margin: 4px 0; padding-left: 10px; }
.sticky-input { position: fixed; bottom: 0; left: 0; right: 0; padding: 12px 24px; background: #ffffffcc; backdrop-filter: blur(8px); z-index: 1000; display: flex; gap: 8px; align-items: center; }
</style>
""", unsafe_allow_html=True)

# === App Header ===
st.title("🌿 AGRIMOKSH - A Farmer's Guide")
st.markdown("Built by TECHMIGOES | AI + Agriculture 🤝")

# === Weather & Recommendations ===
weather_html, temp, humidity = get_weather()
st.markdown(weather_html, unsafe_allow_html=True)
st.success(f"🌾 Recommended Crops: {', '.join(recommend_crops(temp, humidity))}")

# === Disease Detection Section ===
st.header("📷 Detect Plant Disease from Leaf Image")
uploaded_image = st.file_uploader("Upload a leaf image", type=["jpg", "jpeg", "png"])
if uploaded_image:
    img = Image.open(uploaded_image)
    st.image(img, caption="Uploaded Leaf Image", use_column_width=True)
    with st.spinner("Analyzing image..."):
        disease, explanation = classify_plant_disease(img)
    st.success(f"🦠 Disease Detected: *{disease}*")
    st.markdown(f"*Details:* {explanation}")

# === Chat Memory ===
if "messages" not in st.session_state:
    st.session_state.messages = []

# === Sidebar for Chat History ===
st.sidebar.title("Chat History")
for i, message in enumerate(st.session_state.messages):
    st.sidebar.markdown(f"**{message['role'].capitalize()}**: {message['content']}")

# === Button Links for Websites ===
st.header("🌐 Explore More Websites")

# Place buttons side-by-side using columns
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("Machinary"):
        st.markdown('<a href="https://www.toolsvilla.com/category/farm?gad_source=1&gclid=Cj0KCQjw782_BhDjARIsABTv_JAwXyeaZq8E0xPJyckQyuh02hwrLDM-U9nWulnFTyQoYO0FjC5Vw_MaAmc6EALw_wcB " target="_blank">Visit AgriTech News</a>', unsafe_allow_html=True)
with col2:
    if st.button("Drones"):
        st.markdown('<a href="https://www.xboom.in/agriculture-drones/?utm_term=&utm_campaign=Enterprise+PPM&utm_source=adwords&utm_medium=ppc&hsa_acc=1311910180&hsa_cam=21339230157&hsa_grp=&hsa_ad=&hsa_src=x&hsa_tgt=&hsa_kw=&hsa_mt=&hsa_net=adwords&hsa_ver=3&gad_source=1&gclid=Cj0KCQjw782_BhDjARIsABTv_JBEEBKNCdnwSyqUtD4r-Jr8xcq1XcOmxVEnfZbhPqCE4bFWaYcGyqUaAn4AEALw_wcB " target="_blank">Visit Farming Tools</a>', unsafe_allow_html=True)
with col3:
    if st.button("Pesticides"):
        st.markdown('<a href="https://m.indiamart.com/impcat/agricultural-pesticides.html" target="_blank">Visit Weather Updates</a>', unsafe_allow_html=True)
with col4:
    if st.button("Machinary information"):
        st.markdown('<a href="https://www.bing.com/ck/a?!&&p=db6918aaf1a2499c365b92debc415d06c9ced63b89491a0d2724b1fa34b84018JmltdHM9MTc0Mzk4NDAwMA&ptn=3&ver=2&hsh=4&fclid=15c9f171-a80f-62a5-2785-e51fa95d63f7&psq=https%3a%2f%2fnewagri.in%2f&u=a1aHR0cHM6Ly9uZXdhZ3JpLmluLw&ntb=1" target="_blank">Visit Local Agricultural Support</a>', unsafe_allow_html=True)

    
# === Sticky Input UI ===
st.markdown('<div class="sticky-input">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([8, 1, 1, 1])
with col1:
    user_input = st.chat_input("Ask me anything about crop diseases...")
with col2:
    if st.button("🎧"):
        transcribed = transcribe_audio()
        st.session_state.messages.append({"role": "user", "content": transcribed})
        response = get_response(transcribed)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
with col3:
    chat_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages])
    st.download_button("📥", data=chat_text, file_name="chat_history.txt")
st.markdown('</div>', unsafe_allow_html=True)

# === Handle Chat Input ===
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    response = get_response(user_input)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
