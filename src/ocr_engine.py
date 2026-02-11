import pytesseract
from PIL import Image
from pdf2image import convert_from_path, convert_from_bytes
import cv2
import numpy as np
import io
import os
import platform

# --- CONFIGURACIÓN DE RUTAS (SOLO PARA WINDOWS) ---
# En servidores Linux (Streamlit Cloud, etc.), Tesseract y Poppler se instalan automáticamente en el PATH
# Estas rutas solo se usan si estás ejecutando en Windows

# Detectar sistema operativo
IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    # Rutas para Windows (ajusta según tu instalación local)
    RUTA_TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    RUTA_POPPLER = r"C:\Release-24.02.0-0\poppler-24.02.0\Library\bin"
    
    # Configurar Tesseract
    if os.path.exists(RUTA_TESSERACT):
        pytesseract.pytesseract.tesseract_cmd = RUTA_TESSERACT
    
    # Añadir Poppler al PATH
    if os.path.exists(RUTA_POPPLER):
        os.environ["PATH"] += os.pathsep + RUTA_POPPLER
else:
    # En Linux/Mac, Tesseract y Poppler están en el PATH por defecto
    RUTA_TESSERACT = None
    RUTA_POPPLER = None


def preprocess_image(image):
    """
    Applies advanced preprocessing to the image to improve OCR accuracy on low quality inputs.
    Includes: Rescaling, Grayscale, Denoising, and Adaptive Thresholding.
    """
    # Convert PIL Image to OpenCV format
    img = np.array(image)
    
    # Convert to grayscale if needed
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray = img
    
    # Simple upscaling only (helps with small text)
    height, width = gray.shape
    gray = cv2.resize(gray, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)
    
    # Very light denoising
    denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
    
    return Image.fromarray(denoised)

def extract_text_from_image(image_file):
    """
    Extracts text from a single image file (PIL Image or bytes).
    """
    try:
        if isinstance(image_file, bytes):
            image = Image.open(io.BytesIO(image_file))
        else:
            image = image_file

        # Configure Tesseract with language and PSM
        # --psm 6: Assume a single uniform block of text.
        # --psm 3: Fully automatic page segmentation (default).
        # We generally stick to default or 3 for full pages.
        # We explicitly add 'spa' (Spanish) to language.
        custom_config = r'--oem 3 --psm 3 -l spa+eng'

        # Strategy 1: Try ORIGINAL image first (preprocessing might sometimes hurt quality)
        text = pytesseract.image_to_string(image, config=custom_config)
        
        # Fallback: If original yields poor results (e.g., very little text), try preprocessed version
        # The threshold of 50 characters is arbitrary and can be adjusted.
        if len(text.strip()) < 50:
            processed_image = preprocess_image(image)
            text_preprocessed = pytesseract.image_to_string(processed_image, config=custom_config)
            
            # Use whichever result has more text
            if len(text_preprocessed) > len(text):
                text = text_preprocessed
            
        return text
    except Exception as e:
        return f"Error OCR: {e}"

def extract_text_from_pdf(pdf_file):
    """
    Converts PDF to images and extracts text from each page.
    Returns a list of strings, where each string is the text of a page.
    """
    # Let exceptions propagate to the main app for proper error display
    if IS_WINDOWS and RUTA_POPPLER:
        images = convert_from_bytes(pdf_file.read(), poppler_path=RUTA_POPPLER)
    else:
        # En Linux, poppler está en el PATH
        images = convert_from_bytes(pdf_file.read())
            
    pages_text = []
    for image in images:
        text = extract_text_from_image(image)
        pages_text.append(text)
    return pages_text
