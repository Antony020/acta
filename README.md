# Birth Certificate Data Processor

Aplicación web para extraer datos de actas de nacimiento dominicanas usando OCR (Reconocimiento Óptico de Caracteres).

## Características

- ✅ Extracción automática de datos de certificados de nacimiento
- ✅ Soporte para imágenes (JPG, PNG) y PDFs
- ✅ Procesamiento de múltiples páginas
- ✅ Exportación a Excel
- ✅ Interfaz web intuitiva con Streamlit

## Campos Extraídos

- Nombre completo
- NUI (Número Único de Identidad)
- Número de Libro
- Fecha de Nacimiento
- Nombre del Padre y Cédula
- Nombre de la Madre y Cédula

## Instalación Local

### Requisitos Previos

1. **Python 3.8+**
2. **Tesseract OCR** - [Descargar aquí](https://github.com/UB-Mannheim/tesseract/wiki)
3. **Poppler** - [Descargar aquí](https://github.com/oschwartz10612/poppler-windows/releases/)

### Pasos de Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/birth-certificate-processor.git
cd birth-certificate-processor

# 2. Instalar dependencias de Python
pip install -r requirements.txt

# 3. Ejecutar la aplicación
streamlit run app.py
```

### Configuración de Rutas (Solo Windows)

Si Tesseract y Poppler no están en tu PATH, edita `src/ocr_engine.py` líneas 16-17:

```python
RUTA_TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
RUTA_POPPLER = r"C:\tu\ruta\a\poppler\Library\bin"
```

## Uso

1. Abre la aplicación en tu navegador (normalmente `http://localhost:8501`)
2. Arrastra y suelta imágenes o PDFs de certificados
3. Haz clic en "Procesar Certificados"
4. Descarga los resultados en formato Excel

## Deployment en la Nube

Ver [deployment_guide.md](deployment_guide.md) para instrucciones detalladas sobre cómo desplegar en:
- Streamlit Community Cloud (Recomendado - Gratis)
- Hugging Face Spaces
- Railway
- Render

## Estructura del Proyecto

```
birth_certificate_processor/
├── app.py                 # Aplicación principal Streamlit
├── requirements.txt       # Dependencias de Python
├── packages.txt          # Dependencias del sistema (para deployment)
├── src/
│   ├── __init__.py
│   ├── ocr_engine.py     # Motor de OCR
│   └── parser.py         # Lógica de parsing de datos
└── README.md
```

## Tecnologías Utilizadas

- **Streamlit** - Framework web
- **Tesseract OCR** - Reconocimiento de texto
- **OpenCV** - Procesamiento de imágenes
- **Pandas** - Manipulación de datos
- **pdf2image** - Conversión de PDF a imágenes

## Licencia

MIT License - Siéntete libre de usar y modificar este proyecto.

## Soporte

Para reportar problemas o sugerencias, abre un issue en GitHub.
