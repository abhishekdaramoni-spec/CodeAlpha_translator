# 🔮 AI Multilingual Translator+ 

Welcome to the **AI Multilingual Translator+** repository! This project contains **two separate, fully functional translation applications** designed for different deployment and run environments:

1.  **Python & Streamlit Web App**: An advanced, full-featured translation dashboard with text-to-speech audio downloads, dynamic translation history logs (CSV/TXT/PDF), and in-place image OCR translation.
2.  **HTML/CSS/JS Single-Page Web App**: A lightweight, self-contained, instant-loading web page that can be opened on any browser or hosted statically on services like GitHub Pages.

---

## 📁 Repository Structure

Here is how the project files are organized:

```text
CodeAlpha_translator/
├── frontend/
│   └── index.html          # Self-contained HTML/CSS/JS single-page web app
├── app.py                  # Streamlit dashboard frontend, layout, and UI state
├── translator_utils.py     # Python translation engine, OCR overlay, and PDF compiler
├── requirements.txt        # Python package dependencies
├── packages.txt            # Linux system packages (Tesseract OCR for Streamlit Cloud)
├── runtime.txt             # Python runtime environment specification (for Render)
├── render.yaml             # Web Service deployment blueprint (for Render)
├── .fonts/                 # Pre-cached Google Noto Unicode fonts (for script rendering)
└── README.md               # Repository documentation and guide
```

---

## 🚀 How to Run the Applications

### 🌐 1. The HTML Single-Page Web App (Instant Run)
This version is completely self-contained, meaning it does not require Python, local servers, or installation.
*   **Requirements**: None (except an internet connection).
*   **How to Run**:
    1. Open the [frontend/index.html](frontend/index.html) file.
    2. Double-click it to open it directly in Chrome, Firefox, Safari, or Edge.
    3. Type your text, select the target language, and click **Translate** (uses the built-in translation API key and supports speech synthesizers).

---

### 🔮 2. The Python & Streamlit Web App (Full-Featured)
This version runs a local Python server and supports OCR image translation, history logs, and file exports.

#### Prerequisites
*   **Python**: Version 3.10 or 3.11.
*   **Tesseract OCR (For Windows Local Image Translation)**:
    1. Download and install Tesseract OCR from the [UB Mannheim Wiki](https://github.com/UB-Mannheim/tesseract/wiki).
    2. Save its executable path (e.g. `C:\Program Files\Tesseract-OCR\tesseract.exe`) and configure it in the app's **Settings** tab.

#### Installation & Local Launch
1. Open your terminal or Command Prompt in the repository folder.
2. Set up a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the Streamlit web server:
   ```bash
   streamlit run app.py
   ```
5. Open **[http://localhost:8501](http://localhost:8501)** in your web browser.

---

## ☁️ Cloud Deployment Guides

### A. Deploying the Streamlit Web App (Streamlit Community Cloud)
1. Push this repository to your GitHub account.
2. Log into [Streamlit Share](https://share.streamlit.io/).
3. Connect your repository and select `app.py` as the main file.
4. Streamlit will automatically read [packages.txt](packages.txt) to install Tesseract OCR on the server and deploy your application.

### B. Deploying the Streamlit Web App (Render)
1. Link your GitHub repository to [Render](https://render.com/).
2. Render will automatically read the [render.yaml](render.yaml) file to compile the dependencies and run the service.

### C. Deploying the HTML App (GitHub Pages)
1. Go to your GitHub Repository **Settings** -> **Pages**.
2. Set the Source build to **Deploy from a branch**.
3. Choose the `main` branch and specify `/frontend` (or copy `/frontend/index.html` to the root directory to host it at the main domain).
4. Save to deploy your static website for free.
