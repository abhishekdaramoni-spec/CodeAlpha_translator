import streamlit as st
import pandas as pd
import datetime
import os
import importlib
import translator_utils
importlib.reload(translator_utils)

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Multilingual Translator+",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DETECT TESSERACT DEFAULT PATHS (WINDOWS) ---
def detect_default_tesseract():
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        # Add portable/local workspace path check
        r"tesseract.exe"
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path
    return ""

# --- SESSION STATE INITIALIZATION ---
if "history" not in st.session_state:
    st.session_state.history = []

if "tesseract_path" not in st.session_state:
    st.session_state.tesseract_path = detect_default_tesseract()

if "text_input" not in st.session_state:
    st.session_state.text_input = ""

if "translated_output" not in st.session_state:
    st.session_state.translated_output = ""

if "src_lang" not in st.session_state:
    st.session_state.src_lang = "Auto Detect"

if "target_lang" not in st.session_state:
    st.session_state.target_lang = "Spanish"

if "last_detected_lang" not in st.session_state:
    st.session_state.last_detected_lang = None

# --- CUSTOM CSS FOR PREMIUM AESTHETICS ---
st.markdown("""
<style>
    /* Main Layout styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header styling */
    .app-header {
        background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
        padding: 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.3);
    }
    
    .app-header h1 {
        color: white !important;
        margin: 0;
        font-weight: 700;
        font-size: 2.5rem;
    }
    
    .app-header p {
        color: rgba(255, 255, 255, 0.9);
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        font-weight: 300;
    }
    
    /* Sleek card containers */
    .premium-card {
        background-color: var(--secondary-background-color);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.15);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 1.5rem;
    }
    
    .badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        font-size: 0.8rem;
        font-weight: 600;
        border-radius: 50px;
        background-color: rgba(79, 70, 229, 0.15);
        color: #4f46e5;
        border: 1px solid rgba(79, 70, 229, 0.3);
    }
    
    /* Customize buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
        color: white;
        border: none;
        padding: 0.6rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
    }
    
    div.stButton > button:hover {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(79, 70, 229, 0.3);
        color: white;
    }
    
    /* Custom secondary button style (e.g. Swap) */
    div[data-testid="column"] button[key*="swap"] {
        background: transparent;
        color: var(--text-color);
        border: 1px solid rgba(128, 128, 128, 0.3);
        box-shadow: none;
    }
    
    div[data-testid="column"] button[key*="swap"]:hover {
        background: rgba(128, 128, 128, 0.1);
        color: var(--text-color);
    }
</style>
""", unsafe_allow_html=True)

# --- LANGUAGE SETUP ---
languages_dict = translator_utils.get_languages()
language_names = list(languages_dict.keys())
source_options = ["Auto Detect"] + language_names
target_options = language_names

# Invert dictionary to find name from code
code_to_name = {v: k for k, v in languages_dict.items()}

# --- SIDEBAR BRANDING ---
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <span style="font-size: 4rem;">🔮</span>
        <h2 style="margin: 10px 0 0 0; font-weight: 700;">Translator+</h2>
        <p style="font-size: 0.9rem; opacity: 0.8; font-weight: 300;">Lightweight AI Translation Engine</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📊 Status & Info")
    st.info("⚡ Powered by Google Translate & Tesseract OCR")
    
    # Quick statistics in sidebar
    history_count = len(st.session_state.history)
    st.metric(label="Translations Session History", value=history_count)
    
    # Show active configurations
    st.markdown("---")
    st.markdown("### 🛠️ OCR Configuration")
    if st.session_state.tesseract_path:
        st.success("✅ Tesseract OCR Connected")
    else:
        st.warning("⚠️ OCR Disabled (Needs Setup)")

# --- MAIN APP LAYOUT ---
st.markdown("""
<div class="app-header">
    <h1>🔮 AI Multilingual Translator+</h1>
    <p>Perform premium, instant text translations, OCR image translation, and export your translation history log.</p>
</div>
""", unsafe_allow_html=True)

# Setup Navigation Tabs
tabs = st.tabs([
    "📝 Text Translation",
    "🖼️ Image Translation",
    "📜 Translation History",
    "⚙️ Settings & Guide"
])

# ==========================================
# TAB 1: TEXT TRANSLATION
# ==========================================
with tabs[0]:
    # Language Selection Panel
    col1, col_swap, col2 = st.columns([4, 1, 4])
    
    with col1:
        src_lang_select = st.selectbox(
            "Source Language",
            options=source_options,
            key="src_lang"
        )
        
    with col_swap:
        st.write("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        # Disable swap if source language is Auto Detect and we don't have a last detected language
        swap_disabled = (src_lang_select == "Auto Detect" and st.session_state.last_detected_lang is None)
        
        if st.button("⇄ Swap", key="swap_btn", disabled=swap_disabled, use_container_width=True):
            current_src = st.session_state.src_lang
            current_target = st.session_state.target_lang
            
            if current_src == "Auto Detect":
                # Swap the last detected language to target, and target to source
                detected_name = code_to_name.get(st.session_state.last_detected_lang)
                if detected_name:
                    st.session_state.src_lang = current_target
                    st.session_state.target_lang = detected_name
            else:
                # Direct swap
                st.session_state.src_lang = current_target
                st.session_state.target_lang = current_src
            st.rerun()

    with col2:
        target_lang_select = st.selectbox(
            "Target Language",
            options=target_options,
            key="target_lang"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Text Inputs Panel
    in_col, out_col = st.columns(2)
    
    with in_col:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        text_input = st.text_area(
            "Enter Text to Translate",
            value=st.session_state.text_input,
            height=200,
            placeholder="Type or paste your text here...",
            key="text_input_area"
        )
        
        # Track word and character counts
        word_count = len(text_input.split()) if text_input else 0
        char_count = len(text_input) if text_input else 0
        st.markdown(f"<p style='font-size: 0.8rem; opacity: 0.7; text-align: right;'>Words: {word_count} | Characters: {char_count}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with out_col:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.write("**Translated Output**")
        
        # Placeholder or Output
        if st.session_state.translated_output:
            # Add premium visual border/container around the output
            st.markdown(
                f"<div style='border: 1px solid rgba(128,128,128,0.2); border-radius: 8px; padding: 12px; min-height: 160px; background-color: rgba(128,128,128,0.05); white-space: pre-wrap; font-size: 1rem;'>{st.session_state.translated_output}</div>", 
                unsafe_allow_html=True
            )
            
            # Show detected language if auto-detect was used
            if src_lang_select == "Auto Detect" and st.session_state.last_detected_lang:
                detected_name = code_to_name.get(st.session_state.last_detected_lang, st.session_state.last_detected_lang)
                st.markdown(f"<span class='badge' style='margin-top: 10px;'>Detected: {detected_name}</span>", unsafe_allow_html=True)
            
            # Custom Copy Button Injection
            escaped_text = st.session_state.translated_output.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$').replace('"', '\\"')
            copy_html = f"""
            <div style="display: flex; justify-content: flex-end; margin-top: 10px;">
                <button id="copy-btn" style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); color: white; border: none; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 500; display: flex; align-items: center; gap: 6px; transition: all 0.2s; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                    Copy Translation
                </button>
            </div>
            <script>
            document.getElementById('copy-btn').addEventListener('click', function() {{
                const textToCopy = `{escaped_text}`;
                const textarea = document.createElement('textarea');
                textarea.value = textToCopy;
                document.body.appendChild(textarea);
                textarea.select();
                try {{
                    document.execCommand('copy');
                    const btn = document.getElementById('copy-btn');
                    btn.innerHTML = '✓ Copied!';
                    btn.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
                    setTimeout(() => {{
                        btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg> Copy Translation';
                        btn.style.background = 'linear-gradient(135deg, #1e293b 0%, #334155 100%)';
                    }}, 2000);
                }} catch (err) {{
                    console.error('Failed to copy', err);
                }}
                document.body.removeChild(textarea);
            }});
            </script>
            """
            st.components.v1.html(copy_html, height=45)
        else:
            st.markdown(
                "<div style='border: 1px dashed rgba(128,128,128,0.3); border-radius: 8px; padding: 20px; min-height: 160px; display: flex; align-items: center; justify-content: center; color: gray;'>Your translation will appear here.</div>", 
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # Translate Action Trigger
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    if st.button("🔮 Translate Text", use_container_width=True):
        if not text_input.strip():
            st.warning("⚠️ Please enter some text to translate.")
        else:
            with st.spinner("Processing translation..."):
                try:
                    # Resolve language codes
                    src_code = "auto" if src_lang_select == "Auto Detect" else languages_dict[src_lang_select]
                    target_code = languages_dict[target_lang_select]
                    
                    # Language detection if auto is requested
                    detected_code = None
                    if src_code == "auto":
                        detected_code = translator_utils.detect_language(text_input)
                        st.session_state.last_detected_lang = detected_code
                    
                    # Translation call
                    translation = translator_utils.translate_text(text_input, src_code, target_code)
                    st.session_state.translated_output = translation
                    
                    # Log source name
                    source_log_name = src_lang_select
                    if src_code == "auto" and detected_code:
                        source_log_name = f"Auto ({code_to_name.get(detected_code, detected_code)})"
                    
                    # Save to Session History
                    record = {
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "original_text": text_input,
                        "translated_text": translation,
                        "source_lang": source_log_name,
                        "target_lang": target_lang_select
                    }
                    st.session_state.history.append(record)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error during translation: {str(e)}")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- TEXT-TO-SPEECH (TTS) SECTION ---
    if st.session_state.translated_output:
        st.markdown("---")
        st.subheader("🔊 Text-to-Speech Player")
        with st.spinner("Generating speech audio..."):
            try:
                target_code = languages_dict[target_lang_select]
                audio_bytes = translator_utils.generate_audio(st.session_state.translated_output, target_code)
                
                audio_col1, audio_col2 = st.columns([3, 1])
                with audio_col1:
                    st.audio(audio_bytes, format="audio/mp3")
                with audio_col2:
                    st.download_button(
                        label="📥 Download MP3 Audio",
                        data=audio_bytes,
                        file_name=f"translation_{target_code}_{datetime.date.today()}.mp3",
                        mime="audio/mp3",
                        use_container_width=True
                    )
            except Exception as e:
                st.warning(f"⚠️ Text-to-Speech is not fully supported for language '{target_lang_select}' ({str(e)}).")

# ==========================================
# TAB 2: IMAGE TRANSLATION (OCR)
# ==========================================
with tabs[1]:
    st.subheader("📸 Extract & Translate Text from Image")
    st.markdown("Upload a document, receipt, banner, or any image file containing readable text to automatically extract and translate it.")
    
    # OCR Settings Warning
    if not st.session_state.tesseract_path:
        st.warning("⚠️ **Tesseract OCR not configured.** Image extraction will fail. Please go to the **Settings** tab to supply your Tesseract path.")
        
    ocr_col1, ocr_col2 = st.columns([1, 1])
    
    with ocr_col1:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        uploaded_image = st.file_uploader(
            "Upload Image (PNG, JPG, JPEG)", 
            type=["png", "jpg", "jpeg"], 
            key="ocr_uploader"
        )
        
        # Display image preview
        if uploaded_image:
            st.image(uploaded_image, caption="Uploaded Document/Image", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with ocr_col2:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        ocr_target_lang = st.selectbox(
            "Translate Extracted Text To",
            options=target_options,
            key="ocr_target",
            index=target_options.index(st.session_state.target_lang) if st.session_state.target_lang in target_options else 0
        )
        
        ocr_trigger = st.button("🔍 Extract & Translate", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    if uploaded_image and ocr_trigger:
        if not st.session_state.tesseract_path and os.name == 'nt':
            st.error("❌ Tesseract executable path is not configured. Please supply a valid path in Settings.")
        else:
            with st.spinner("Extracting text from image (OCR)..."):
                try:
                    # Run OCR
                    extracted_text = translator_utils.extract_text_from_image(
                        uploaded_image, 
                        st.session_state.tesseract_path if os.name == 'nt' else None
                    )
                    
                    if not extracted_text:
                        st.warning("⚠️ OCR complete, but no readable text could be found in the image.")
                    else:
                        st.success("✅ OCR successfully completed!")
                        
                        # Translate
                        with st.spinner("Translating OCR text..."):
                            target_code = languages_dict[ocr_target_lang]
                            translated_ocr = translator_utils.translate_text(extracted_text, "auto", target_code)
                            
                            # Language detection for logs
                            detected_src_code = translator_utils.detect_language(extracted_text)
                            detected_src_name = "Auto (OCR)"
                            if detected_src_code:
                                detected_src_name = f"Auto ({code_to_name.get(detected_src_code, detected_src_code)})"
                            
                            # Add to History
                            record = {
                                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "original_text": f"[OCR Extraction]\n{extracted_text}",
                                "translated_text": translated_ocr,
                                "source_lang": detected_src_name,
                                "target_lang": ocr_target_lang
                            }
                            st.session_state.history.append(record)
                            
                            # Display Side-by-Side Images
                            st.markdown("---")
                            st.write("🖼️ **Visual In-Place Image Translation**")
                            img_col1, img_col2 = st.columns(2)
                            with img_col1:
                                st.image(uploaded_image, caption="Original Image", use_container_width=True)
                            with img_col2:
                                with st.spinner("Generating image overlay..."):
                                    try:
                                        translated_img = translator_utils.overlay_translation_on_image(
                                            uploaded_image,
                                            target_code,
                                            st.session_state.tesseract_path if os.name == 'nt' else None
                                        )
                                        st.image(translated_img, caption="Translated Image (Overlay)", use_container_width=True)
                                    except Exception as img_err:
                                        st.warning(f"Could not generate visual overlay: {str(img_err)}")

                            # Display Text Results below
                            st.markdown("<br>", unsafe_allow_html=True)
                            res_col1, res_col2 = st.columns(2)
                            
                            with res_col1:
                                st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
                                st.write("📝 **Extracted Text**")
                                st.code(extracted_text, language=None)
                                st.markdown("</div>", unsafe_allow_html=True)
                                
                            with res_col2:
                                st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
                                st.write("🔮 **Translated Text**")
                                st.code(translated_ocr, language=None)
                                st.markdown("</div>", unsafe_allow_html=True)
                            
                            # OCR TTS Playback
                            st.markdown("### 🔊 Translated Speech Player")
                            try:
                                audio_bytes = translator_utils.generate_audio(translated_ocr, target_code)
                                audio_col1, audio_col2 = st.columns([3, 1])
                                with audio_col1:
                                    st.audio(audio_bytes, format="audio/mp3")
                                with audio_col2:
                                    st.download_button(
                                        label="📥 Download Audio File",
                                        data=audio_bytes,
                                        file_name=f"ocr_translation_{target_code}.mp3",
                                        mime="audio/mp3",
                                        use_container_width=True
                                    )
                            except Exception as e:
                                st.warning(f"⚠️ Speech playback could not be generated: {str(e)}")
                                
                except Exception as e:
                    st.error(f"❌ OCR processing failed: {str(e)}")

# ==========================================
# TAB 3: TRANSLATION HISTORY
# ==========================================
with tabs[2]:
    st.subheader("📜 Translation History Log")
    
    if not st.session_state.history:
        st.info("No translations logged in this session yet. Translate some text to see logs here!")
    else:
        # Action Bar
        hist_col1, hist_col2, hist_col3, hist_col4 = st.columns([2, 1, 1, 1])
        
        # Build history dataframe
        history_df = pd.DataFrame(st.session_state.history)
        # Re-order columns for clean viewing
        history_df = history_df[["timestamp", "source_lang", "target_lang", "original_text", "translated_text"]]
        
        with hist_col1:
            st.write(f"Logged translations: **{len(history_df)}**")
        with hist_col2:
            # Export CSV
            csv_data = history_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📁 Export to CSV",
                data=csv_data,
                file_name=f"translator_history_{datetime.date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with hist_col3:
            # Export TXT
            txt_content = ""
            for idx, r in history_df.iterrows():
                txt_content += f"[{r['timestamp']}] {r['source_lang']} ➜ {r['target_lang']}\n"
                txt_content += f"Original:\n{r['original_text']}\n"
                txt_content += f"Translation:\n{r['translated_text']}\n"
                txt_content += "="*50 + "\n\n"
            
            st.download_button(
                label="📄 Export to TXT",
                data=txt_content.encode('utf-8'),
                file_name=f"translator_history_{datetime.date.today()}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with hist_col4:
            # Export PDF
            with st.spinner("Compiling PDF..."):
                try:
                    pdf_data = translator_utils.export_history_pdf(st.session_state.history)
                    st.download_button(
                        label="📕 Export to PDF",
                        data=pdf_data,
                        file_name=f"translator_history_{datetime.date.today()}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"PDF Export Error: {str(e)}")
                    
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Display Grid View
        st.markdown("#### 🔍 Batch Log View")
        st.dataframe(history_df, use_container_width=True, height=250)
        
        # Display Expandable Cards
        st.markdown("<br>#### 🧐 Detailed Log Cards", unsafe_allow_html=True)
        # Display from newest to oldest
        for i, item in enumerate(reversed(st.session_state.history)):
            index = len(st.session_state.history) - i - 1
            with st.expander(f"Record #{index + 1} | {item['timestamp']} | {item['source_lang']} ➜ {item['target_lang']}"):
                exp_col1, exp_col2 = st.columns(2)
                with exp_col1:
                    st.write("**Original Text:**")
                    st.info(item['original_text'])
                with exp_col2:
                    st.write("**Translated Text:**")
                    st.success(item['translated_text'])
                    
                    # Copy item
                    escaped_hist_text = item['translated_text'].replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$').replace('"', '\\"')
                    item_copy_html = f"""
                    <div style="display: flex; justify-content: flex-end; margin-top: 5px;">
                        <button id="copy-btn-{index}" style="background-color: #334155; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-family: 'Inter', sans-serif; font-size: 12px; display: flex; align-items: center; gap: 4px; transition: all 0.2s;">
                            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                            Copy
                        </button>
                    </div>
                    <script>
                    document.getElementById('copy-btn-{index}').addEventListener('click', function() {{
                        const textToCopy = `{escaped_hist_text}`;
                        const textarea = document.createElement('textarea');
                        textarea.value = textToCopy;
                        document.body.appendChild(textarea);
                        textarea.select();
                        try {{
                            document.execCommand('copy');
                            const btn = document.getElementById('copy-btn-{index}');
                            btn.innerHTML = '✓ Copied!';
                            btn.style.backgroundColor = '#10b981';
                            setTimeout(() => {{
                                btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg> Copy';
                                btn.style.backgroundColor = '#334155';
                            }}, 2000);
                        }} catch (err) {{
                            console.error('Failed to copy', err);
                        }}
                        document.body.removeChild(textarea);
                    }});
                    </script>
                    """
                    st.components.v1.html(item_copy_html, height=35)
                    
        # Clear log button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Clear Translation History Log", use_container_width=True):
            st.session_state.history = []
            st.success("Translation history log cleared!")
            st.rerun()

# ==========================================
# TAB 4: SETTINGS & GUIDE
# ==========================================
with tabs[3]:
    st.subheader("⚙️ System Settings & Path Setup")
    
    st.markdown("""
    Customize your local environment settings to enable advanced features like Image Text Translation (OCR). 
    """)
    
    tess_path_input = st.text_input(
        "Tesseract OCR Executable Path (Windows only)",
        value=st.session_state.tesseract_path,
        placeholder="e.g. C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
        help="Specify the full path to tesseract.exe. For deployment on Streamlit Community Cloud (Linux), this is handled automatically via packages.txt."
    )
    
    if st.button("💾 Save Path Settings"):
        # Validate path existence if not empty
        if tess_path_input and not os.path.exists(tess_path_input):
            st.error(f"❌ File does not exist at path: '{tess_path_input}'. Please check and try again.")
        else:
            st.session_state.tesseract_path = tess_path_input
            st.success("✅ Tesseract OCR Path updated and verified successfully!")
            st.rerun()
            
    st.markdown("---")
    
    st.subheader("📖 Quick User & Features Guide")
    st.markdown("""
    Welcome to the **AI Multilingual Translator+**! Here is a brief guide on how to utilize all features:
    
    1. **Text Translation**:
       - Select source and target languages. Use **Auto Detect** if you are unsure of the source language.
       - Enter the text and press **Translate Text**.
       - Listen to the translation by using the built-in audio player or download it as an MP3.
       - Use the custom **Copy Translation** button to save the output text directly to your clipboard.
       - You can easily swap languages using the **⇄ Swap** button.
       
    2. **Image Translation (OCR)**:
       - Upload any clear image (JPG, JPEG, or PNG format).
       - Select the language you want to translate the extracted text into.
       - Click **Extract & Translate** to pull textual data from the image and see the side-by-side comparison.
       
    3. **Translation History**:
       - View all translations processed in this session.
       - Export your historical logs into **CSV**, **TXT**, or a beautifully formatted **PDF** document.
       
    4. **Deployment Info**:
       - Optimized for deployment on **Streamlit Community Cloud** with a total container footprint under 500 MB (avoiding heavy PyTorch/TensorFlow dependencies).
    """)
