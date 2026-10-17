# 🌿 AgriMoksh — AI-Powered Agriculture Chatbot

> A smart farming assistant built with **Streamlit** and **Google Gemini AI**, designed to help South Indian farmers with crop recommendations, plant disease detection, and real-time weather-based advice.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🌤 **Live Weather** | Fetches real-time weather for your location and displays temperature, humidity & wind speed |
| 🌾 **Crop Recommendations** | Suggests the best crops to grow based on current temperature and humidity |
| 📷 **Disease Detection** | Upload a leaf photo to identify common plant diseases and get treatment advice |
| 🤖 **AI Chatbot** | Ask any agriculture question — powered by Google Gemini 1.5 Flash |
| 🎧 **Voice Input** | Speak your question instead of typing |
| 📥 **Chat Export** | Download your full chat history as a `.txt` file |
| 🌐 **Resource Links** | Quick links to machinery, drones, pesticides, and agri-info portals |

---

## 📁 Project Structure

```
AGRIMOKSH--Ai-powered-Agriculture-Chatbot/
│
├── APP.py              # Main Streamlit application (single entry point)
├── requirements.txt    # Python dependencies
├── .env                # Your secret API keys (not committed to git)
├── .env.example        # Template showing which keys are needed
├── .gitignore          # Files excluded from version control
└── README.md           # This file
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/your-username/AGRIMOKSH--Ai-powered-Agriculture-Chatbot.git
cd AGRIMOKSH--Ai-powered-Agriculture-Chatbot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

> **Note:** `pyaudio` (needed for voice input) can be tricky on Windows.
> If you see an error, install it with:
> ```bash
> pip install pipwin
> pipwin install pyaudio
> ```

### 3. Set up API keys
Copy the example file and fill in your keys:
```bash
cp .env.example .env
```
Then open `.env` and replace the placeholders:
```
GOOGLE_API_KEY=your_google_generative_ai_key
WEATHER_API_KEY=your_openweathermap_key
```

- **Google Generative AI key** → [Google AI Studio](https://aistudio.google.com/app/apikey)
- **OpenWeatherMap key** → [openweathermap.org](https://openweathermap.org/api)

### 4. Run the app
```bash
streamlit run APP.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 🧠 How It Works

```
User Input (text / voice / image)
        │
        ▼
   APP.py (Streamlit UI)
        │
        ├── Weather API  →  OpenWeatherMap
        ├── Crop logic   →  Rule-based (temp + humidity ranges)
        ├── Disease AI   →  Demo classifier (random from disease DB)
        └── Chat AI      →  Google Gemini 1.5 Flash
```

> **Disease Detection Note:** The current classifier is a demonstration using a
> curated disease database. In a production build, replace it with a trained
> vision model (e.g., fine-tuned on the PlantVillage dataset).

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | Web UI framework |
| `google-generativeai` | Gemini AI chat responses |
| `requests` | Weather API calls |
| `SpeechRecognition` | Voice-to-text input |
| `Pillow` | Image handling for disease detection |
| `geocoder` | IP-based location detection |
| `python-dotenv` | Load API keys from `.env` |
| `pyaudio` | Microphone access for voice input |

---

## 🌾 Supported Crops (Recommendation Engine)

| Crop | Temp Range (°C) | Humidity Range (%) |
|---|---|---|
| Wheat | 10 – 25 | 40 – 60 |
| Rice | 20 – 35 | 60 – 80 |
| Maize | 18 – 27 | 50 – 70 |
| Cotton | 21 – 30 | 50 – 60 |
| Sugarcane | 21 – 35 | 60 – 80 |
| Pulses | 18 – 30 | 40 – 70 |
| Groundnut | 20 – 30 | 50 – 70 |

---

## 📞 Crop Helplines

| Crop | Contact Number |
|---|---|
| Chilli | 8551269743 |
| Pulses | 9874563210 |
| Cotton | 9874561230 |

*(These are appended automatically by the AI when you mention the crop.)*

---

## 🛠 Built By

**TECHMIGOES** — AI + Agriculture 🤝

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
