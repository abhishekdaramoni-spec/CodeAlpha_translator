import io
import datetime
import os
from PIL import Image, ImageDraw, ImageFont
import pytesseract
from deep_translator import GoogleTranslator
from gtts import gTTS
from langdetect import detect, LangDetectException

# Import ReportLab components for professional PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Fallback languages dictionary in case dynamic fetch fails
FALLBACK_LANGUAGES = {
    "Afrikaans": "af", "Albanian": "sq", "Amharic": "am", "Arabic": "ar", "Armenian": "hy",
    "Azerbaijani": "az", "Basque": "eu", "Belarusian": "be", "Bengali": "bn", "Bosnian": "bs",
    "Bulgarian": "bg", "Catalan": "ca", "Cebuano": "ceb", "Chichewa": "ny", "Chinese (Simplified)": "zh-CN",
    "Chinese (Traditional)": "zh-TW", "Corsican": "co", "Croatian": "hr", "Czech": "cs", "Danish": "da",
    "Dutch": "nl", "English": "en", "Esperanto": "eo", "Estonian": "et", "Filipino": "tl",
    "Finnish": "fi", "French": "fr", "Frisian": "fy", "Galician": "gl", "Georgian": "ka",
    "German": "de", "Greek": "el", "Gujarati": "gu", "Haitian Creole": "ht", "Hausa": "ha",
    "Hawaiian": "haw", "Hebrew": "iw", "Hindi": "hi", "Hmong": "hmn", "Hungarian": "hu",
    "Icelandic": "is", "Igbo": "ig", "Indonesian": "id", "Irish": "ga", "Italian": "it",
    "Japanese": "ja", "Javanese": "jw", "Kannada": "kn", "Kazakh": "kk", "Khmer": "km",
    "Kinyarwanda": "rw", "Korean": "ko", "Kurdish (Kurmanji)": "ku", "Kyrgyz": "ky", "Lao": "lo",
    "Latin": "la", "Latvian": "lv", "Lithuanian": "lt", "Luxembourgish": "lb", "Macedonian": "mk",
    "Malagasy": "mg", "Malay": "ms", "Malayalam": "ml", "Maltese": "mt", "Maori": "mi",
    "Marathi": "mr", "Mongolian": "mn", "Myanmar (Burmese)": "my", "Nepali": "ne", "Norwegian": "no",
    "Odia (Oriya)": "or", "Pashto": "ps", "Persian": "fa", "Polish": "pl", "Portuguese": "pt",
    "Punjabi": "pa", "Romanian": "ro", "Russian": "ru", "Samoan": "sm", "Scots Gaelic": "gd",
    "Serbian": "sr", "Sesotho": "st", "Shona": "sn", "Sindhi": "sd", "Sinhala": "si",
    "Slovak": "sk", "Slovenian": "sl", "Somali": "so", "Spanish": "es", "Sundanese": "su",
    "Swahili": "sw", "Swedish": "sv", "Tajik": "tg", "Tamil": "ta", "Tatar": "tt",
    "Telugu": "te", "Thai": "th", "Turkish": "tr", "Turkmen": "tk", "Ukrainian": "uk",
    "Urdu": "ur", "Uyghur": "ug", "Uzbek": "uz", "Vietnamese": "vi", "Welsh": "cy",
    "Xhosa": "xh", "Yiddish": "yi", "Yoruba": "yo", "Zulu": "zu"
}

def get_languages():
    """
    Fetches the supported languages dictionary dynamically from deep-translator.
    Returns:
        dict: A sorted dictionary mapping Title Case language names to language codes.
    """
    try:
        raw_langs = GoogleTranslator().get_supported_languages(as_dict=True)
        # Convert keys to Title Case for visual representation, e.g. "english" -> "English"
        formatted_langs = {k.title(): v for k, v in raw_langs.items()}
        return dict(sorted(formatted_langs.items()))
    except Exception as e:
        # Fallback to hardcoded list in case of network issues or deep-translator updates
        return dict(sorted(FALLBACK_LANGUAGES.items()))

def translate_text(text, src_lang_code, dest_lang_code):
    """
    Translates text from source language to target language.
    Implements a robust retry mechanism for connection drops.
    """
    if not text or not text.strip():
        return ""
    
    import time
    max_retries = 3
    last_exception = None
    for attempt in range(max_retries):
        try:
            translator = GoogleTranslator(source=src_lang_code, target=dest_lang_code)
            translated = translator.translate(text)
            return translated
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                time.sleep(1)
                
    raise RuntimeError(
        f"Connection failed: {str(last_exception)}. "
        "Please try again shortly."
    )

def detect_language(text):
    """
    Detects the 2-letter language code of the input text.
    """
    if not text or not text.strip():
        return None
    try:
        return detect(text)
    except LangDetectException:
        # Fallback using deep-translator auto detection if langdetect fails
        try:
            # We perform a tiny translation to trigger deep-translator auto-detect mechanism
            # or simply return None if we want to rely on the translation pipeline itself
            return None
        except Exception:
            return None

def extract_text_from_image(image_file, tesseract_cmd_path=None):
    """
    Extracts text from an uploaded image using pytesseract.
    """
    try:
        # Configure Tesseract path if provided (vital for Windows setups)
        if tesseract_cmd_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd_path
        
        # Load image via PIL
        img = Image.open(image_file)
        
        # Perform OCR
        extracted_text = pytesseract.image_to_string(img)
        return extracted_text.strip()
    except pytesseract.TesseractNotFoundError:
        raise RuntimeError(
            "Tesseract OCR executable not found. "
            "Please install Tesseract OCR on your machine and set the executable path in the 'Settings' tab."
        )
    except Exception as e:
        raise RuntimeError(f"Failed to process image: {str(e)}")

def generate_audio(text, lang_code):
    """
    Generates text-to-speech audio bytes using gTTS.
    Implements a robust retry mechanism for transient network/connection issues.
    """
    import time
    
    tts_lang = lang_code
    if tts_lang == "zh-CN":
        tts_lang = "zh-cn"
    elif tts_lang == "zh-TW":
        tts_lang = "zh-tw"
    elif "-" in tts_lang:
        tts_lang = tts_lang.split("-")[0]
        
    max_retries = 3
    last_exception = None
    for attempt in range(max_retries):
        try:
            tts = gTTS(text=text, lang=tts_lang, slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp.read()
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                time.sleep(1)
                
    # If all attempts fail, raise a helpful runtime exception
    raise RuntimeError(
        f"Network connection failed: {str(last_exception)}. "
        "Please check your connection or try again."
    )

def export_history_pdf(history_list):
    """
    Generates a beautifully styled ReportLab PDF containing translation history.
    Uses flowing paragraphs to ensure long records split across pages without crashes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=45, leftMargin=45,
        topMargin=45, bottomMargin=45
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles for Premium Look
    title_style = ParagraphStyle(
        'PDFTitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=colors.HexColor('#0F172A'), # Slate 900
        spaceAfter=10,
        alignment=0
    )
    
    subtitle_style = ParagraphStyle(
        'PDFSubTitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#64748B'), # Slate 500
        spaceAfter=25
    )
    
    record_header_style = ParagraphStyle(
        'RecordHeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor('#1E293B'), # Slate 800
        spaceBefore=14,
        spaceAfter=6
    )
    
    label_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.HexColor('#475569'), # Slate 600
        spaceAfter=2
    )
    
    content_style = ParagraphStyle(
        'ContentStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        textColor=colors.HexColor('#0F172A'), # Slate 900
        leading=13,
        spaceAfter=10
    )
    
    divider_style = ParagraphStyle(
        'DividerStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.HexColor('#CBD5E1'), # Light slate
        spaceAfter=8,
        alignment=1 # Centered
    )

    story = []
    
    # Title & Metadata
    story.append(Paragraph("AI Multilingual Translator+ History Log", title_style))
    current_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    story.append(Paragraph(f"Exported on: {current_time_str} | Total Translations: {len(history_list)}", subtitle_style))
    story.append(Spacer(1, 10))
    
    for i, record in enumerate(history_list):
        ts = record.get("timestamp", "")
        lang_flow = f"{record.get('source_lang', 'Auto')} ➜ {record.get('target_lang', '')}"
        orig = record.get("original_text", "")
        trans = record.get("translated_text", "")
        
        # Header for the record card
        story.append(Paragraph(f"Record #{i+1} | {ts} | {lang_flow}", record_header_style))
        
        # Original Text
        story.append(Paragraph("Original Text:", label_style))
        story.append(Paragraph(orig.replace('\n', '<br/>'), content_style))
        
        # Translated Text
        story.append(Paragraph("Translated Text:", label_style))
        story.append(Paragraph(trans.replace('\n', '<br/>'), content_style))
        
        # Visual divider line
        story.append(Paragraph("—" * 65, divider_style))
        
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# Map of language codes to Noto Sans font files and raw GitHub download URLs
FONTS_URL_MAP = {
    # Devanagari (Hindi, Marathi, Nepali)
    'hi': ('NotoSansDevanagari-Regular.ttf', 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf'),
    'mr': ('NotoSansDevanagari-Regular.ttf', 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf'),
    'ne': ('NotoSansDevanagari-Regular.ttf', 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf'),
    # Gujarati
    'gu': ('NotoSansGujarati-Regular.ttf', 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansGujarati/NotoSansGujarati-Regular.ttf'),
    # Bengali
    'bn': ('NotoSansBengali-Regular.ttf', 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansBengali/NotoSansBengali-Regular.ttf'),
    # Tamil
    'ta': ('NotoSansTamil-Regular.ttf', 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansTamil/NotoSansTamil-Regular.ttf'),
    # Telugu
    'te': ('NotoSansTelugu-Regular.ttf', 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansTelugu/NotoSansTelugu-Regular.ttf'),
    # Kannada
    'kn': ('NotoSansKannada-Regular.ttf', 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansKannada/NotoSansKannada-Regular.ttf'),
    # Malayalam
    'ml': ('NotoSansMalayalam-Regular.ttf', 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansMalayalam/NotoSansMalayalam-Regular.ttf')
}

def get_font_for_language(lang_code, font_size):
    """
    Returns a PIL ImageFont object suited for the given language code,
    supporting Indic, CJK, Arabic and Western scripts on Windows/Linux.
    Auto-downloads Google Noto fonts if system-level files are missing.
    """
    # 1. First check if the language is in our auto-download map (Indic scripts)
    if lang_code in FONTS_URL_MAP:
        filename, url = FONTS_URL_MAP[lang_code]
        # Resolve path to .fonts folder inside the project directory
        fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".fonts")
        os.makedirs(fonts_dir, exist_ok=True)
        local_path = os.path.join(fonts_dir, filename)
        
        # Download font if not already cached
        if not os.path.exists(local_path):
            try:
                import urllib.request
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=15) as response:
                    with open(local_path, "wb") as f:
                        f.write(response.read())
            except Exception as e:
                # Log error silently and fall back to system checking
                pass
                
        if os.path.exists(local_path):
            try:
                return ImageFont.truetype(local_path, font_size)
            except Exception:
                pass

    # 2. Fallback to Windows system directories
    windows_font_map = {
        'hi': 'Nirmala.ttf', 'gu': 'Nirmala.ttf', 'mr': 'Nirmala.ttf', 'bn': 'Nirmala.ttf',
        'ta': 'Nirmala.ttf', 'te': 'Nirmala.ttf', 'kn': 'Nirmala.ttf', 'ml': 'Nirmala.ttf',
        'ne': 'Nirmala.ttf', 'pa': 'Nirmala.ttf', 'or': 'Nirmala.ttf',
        'zh-CN': 'msyh.ttc', 'zh-TW': 'msyh.ttc', 'zh': 'msyh.ttc',
        'ja': 'msgothic.ttc',
        'ko': 'malgun.ttf',
        'ar': 'tahoma.ttf', 'ur': 'tahoma.ttf', 'fa': 'tahoma.ttf'
    }
    
    linux_font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/fonts-deva-extra/sahadeva.ttf",
        "/usr/share/fonts/truetype/lohit-gujarati/Lohit-Gujarati.ttf"
    ]
    
    font_path = None
    
    if os.name == 'nt': # Windows
        fonts_dir = r"C:\Windows\Fonts"
        specific_font = windows_font_map.get(lang_code)
        if specific_font:
            path = os.path.join(fonts_dir, specific_font)
            if os.path.exists(path):
                font_path = path
        
        if not font_path:
            for fallback in ["arial.ttf", "segoeui.ttf"]:
                path = os.path.join(fonts_dir, fallback)
                if os.path.exists(path):
                    font_path = path
                    break
    else: # Linux / Cloud Deployment
        for path in linux_font_paths:
            if os.path.exists(path):
                font_path = path
                break
                
    try:
        if font_path:
            return ImageFont.truetype(font_path, font_size)
    except Exception:
        pass
        
    return ImageFont.load_default()

def overlay_translation_on_image(image_file, target_lang_code, tesseract_cmd_path=None):
    """
    Performs OCR, translates lines of text, and draws them directly onto the image,
    returning a new PIL Image with the translated text overlay.
    """
    try:
        # Configure Tesseract path if provided
        if tesseract_cmd_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd_path
            
        img = Image.open(image_file).convert("RGB")
        draw = ImageDraw.Draw(img)
        
        # Get OCR data with details
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        n_boxes = len(data['text'])
        
        # Group words by block and line to translate line-by-line
        lines = {}
        for i in range(n_boxes):
            text = data['text'][i].strip()
            if not text:
                continue
            block = data['block_num'][i]
            line = data['line_num'][i]
            key = (block, line)
            if key not in lines:
                lines[key] = []
            lines[key].append({
                'text': text,
                'left': data['left'][i],
                'top': data['top'][i],
                'width': data['width'][i],
                'height': data['height'][i]
            })
            
        # Batch translate all lines to prevent rate limiting / SSL termination blocks
        line_keys = list(lines.keys())
        line_texts = []
        for key in line_keys:
            words = lines[key]
            line_text = " ".join(w['text'] for w in words)
            line_texts.append(line_text)
            
        translations = {}
        if line_texts:
            import time
            try:
                # Send all lines in a single request, joined by newlines
                batch_text = "\n".join(line_texts)
                translated_batch = translate_text(batch_text, "auto", target_lang_code)
                translated_lines = translated_batch.split("\n")
                
                if len(translated_lines) == len(line_texts):
                    for idx, key in enumerate(line_keys):
                        translations[key] = translated_lines[idx].strip()
                else:
                    # Fallback to line-by-line translation with a small rate-limiting delay
                    for idx, key in enumerate(line_keys):
                        translations[key] = translate_text(line_texts[idx], "auto", target_lang_code)
                        time.sleep(0.3)
            except Exception:
                # Generic fallback if batch fails
                for idx, key in enumerate(line_keys):
                    translations[key] = translate_text(line_texts[idx], "auto", target_lang_code)
                    time.sleep(0.3)
                    
        # Render and overlay the translated lines
        for key, words in lines.items():
            if key not in translations or not translations[key]:
                continue
            translated = translations[key]
            
            # Get line bounding box
            left = min(w['left'] for w in words)
            top = min(w['top'] for w in words)
            right = max(w['left'] + w['width'] for w in words)
            bottom = max(w['top'] + w['height'] for w in words)
            width = right - left
            height = bottom - top
            
            # Sample background color near the text block to mask original text cleanly
            try:
                sample_x = max(0, left - 2)
                sample_y = max(0, top - 2)
                bg_color = img.getpixel((sample_x, sample_y))
            except Exception:
                bg_color = (255, 255, 255) # default white
                
            # Calculate brightness to choose text color
            brightness = 0.299*bg_color[0] + 0.587*bg_color[1] + 0.114*bg_color[2]
            text_color = (0, 0, 0) if brightness > 127 else (255, 255, 255)
            
            # Draw background box to mask original text
            padding = 2
            draw.rectangle(
                [left - padding, top - padding, right + padding, bottom + padding],
                fill=bg_color
            )
            
            # Calculate font size safely, handling vertical/rotated text blocks
            if height > width:
                font_size = max(8, int(width * 0.85))
            else:
                font_size = max(8, int(height * 0.85))
                
            font_size = min(font_size, 40)
            font = get_font_for_language(target_lang_code, font_size)
                
            # Draw translated text
            draw.text((left, top - padding), translated, fill=text_color, font=font)
            
        return img
    except Exception as e:
        raise RuntimeError(f"Failed to generate in-place image translation: {str(e)}")
