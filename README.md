# 🔮 AI Multilingual Translator+

A lightweight, high-performance, and visually premium multilingual translation application built with **Python** and **Streamlit**. Optimized for local runs on Windows and production deployments on Streamlit Community Cloud or Render.

---

## ✨ Features

1. **Text Translation**: Instant translations with optional language **Auto Detect** powered by Google Translate. Includes a ⇄ Swap button and a custom HTML/JS copy button with visual checkmark animations.
2. **In-Place Image Translation (OCR)**: Extracts text from images (JPG, JPEG, PNG) using Tesseract OCR, masks the original text using local background color sampling, and overlays the translation directly in-context onto the image.
3. **Text-to-Speech (TTS)**: Synthesizes translated text into clear audio playback using `gTTS` with download options.
4. **Self-Healing Fonts**: Automatically downloads and caches required Google Noto fonts locally if the system lacks native Indic/Unicode script support (e.g. Hindi, Gujarati, Tamil, etc.).
5. **Session Logs & History**: Maintains a history log of translations. Allows detailed record views and batch log exports to **CSV**, **TXT**, or ReportLab-formatted **PDF** logs.
6. **Dark Mode Responsive UI**: Employs custom CSS styling integrated with Streamlit's official theme variables to adapt automatically to light and dark modes.

---

## 📁 Project Structure

```text
ai translator/
├── app.py                  # Streamlit frontend, layouts, and pages
├── translator_utils.py     # Translation, OCR, gTTS, and ReportLab PDF compilers
├── requirements.txt        # Python library dependencies
├── packages.txt            # System dependencies (for Streamlit Cloud Tesseract)
├── runtime.txt             # Target Python environment (for Render)
├── render.yaml             # Web service deployment configuration (for Render)
├── .fonts/                 # Cached Google Noto Unicode fonts (auto-downloaded)
└── README.md               # Product documentation and user guide
```

---

## 🚀 Setup and Local Run

### Prerequisites
* **Python**: Version 3.10 or 3.11.
* **Tesseract OCR (Windows Local)**: Install the binary from [UB Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki) and configure its path under the **Settings** tab in the app.

### Installation & Run
1. Clone or copy the project files to your directory.
2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the Streamlit server:
   ```bash
   streamlit run app.py
   ```
5. Open `http://localhost:8501` in your browser.

---

## ☁️ Deployment

### Option A: Streamlit Community Cloud (Recommended)
1. Push the code to a GitHub repository.
2. Log into [Streamlit Share](https://share.streamlit.io/).
3. Connect your repository and select `app.py` as the entrypoint.
4. Streamlit will read `packages.txt` to automatically install Tesseract OCR and run the app.

### Option B: Render
1. Connect your repository to Render.
2. Render will automatically read `render.yaml` to deploy it as a Python Web Service.
