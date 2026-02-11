import streamlit as st
import pandas as pd
from src.ocr_engine import extract_text_from_image, extract_text_from_pdf
from src.parser import parse_certificate_data
from src.exporter import to_excel
from PIL import Image
import io

st.set_page_config(page_title="Extractor de Actas de Nacimiento", layout="wide")

st.title("📂 Extractor de Datos de Actas de Nacimiento")
st.markdown("""
Sube tus actas de nacimiento (Imagen o PDF) y la aplicación extraerá automáticamente los datos clave 
para exportarlos a Excel.
""")

# Sidebar for configuration
st.sidebar.header("Configuración")
uploaded_files = st.sidebar.file_uploader(
    "Cargar Archivos", 
    type=['png', 'jpg', 'jpeg', 'pdf', 'tiff'], 
    accept_multiple_files=True
)

if uploaded_files:
    st.write(f"### Procesando {len(uploaded_files)} archivo(s)...")
    
    all_data = []
    
    # Progress bar
    progress_bar = st.progress(0)
    
    for i, file in enumerate(uploaded_files):
        # Update progress
        progress_bar.progress((i + 1) / len(uploaded_files))
        
        file_details = {"Archivo": file.name, "Tipo": file.type}
        
        try:
            texts_to_process = []
            if file.type == "application/pdf":
                # Returns a list of texts (one per page)
                texts_to_process = extract_text_from_pdf(file)
            else:
                image = Image.open(file)
                # Returns a single string, wrap in list
                texts_to_process = [extract_text_from_image(image)]
            
            # Process each text block (page) as a separate certificate
            for idx, raw_text in enumerate(texts_to_process):
                extracted_data = parse_certificate_data(raw_text)
                
                # Check if we actually extracted anything relevant
                # Keys to check
                relevant_keys = ["Nombre", "NUI", "Numero de Libro", "Fecha de Nacimiento", "Padre", "Madre"]
                has_content = any(extracted_data.get(key) for key in relevant_keys)
                
                # Also if raw_text is extremely short, it's likely a blank page error
                if len(raw_text.strip()) < 10:
                    has_content = False

                if has_content:
                    # Add metadata
                    page_suffix = f" - Pag {idx+1}" if len(texts_to_process) > 1 else ""
                    extracted_data["Archivo Origen"] = f"{file.name}{page_suffix}"
                    all_data.append(extracted_data)
                    
                    # Debug Info
                    with st.expander(f"Ver texto extraído de {file.name}{page_suffix}"):
                        st.text(raw_text)
                else:
                    # Warn user
                    st.warning(f"No se detectaron datos válidos en {file.name} - Pag {idx+1}. Verifique la calidad o el formato.")
                    with st.expander(f"Ver texto crudo (No procesado) de {file.name} - Pag {idx+1}"):
                        st.text(raw_text)
            
        except Exception as e:
            st.error(f"FATAL ERROR procesando {file.name}: {str(e)}")
            st.code(str(e)) # Show full error to user
            
    progress_bar.empty()
    
    if all_data:
        st.success("¡Procesamiento completado!")
        
        # Display data
        df = pd.DataFrame(all_data)
        st.subheader("Vista Previa de Datos")
        st.dataframe(df)
        
        # Download button
        excel_data = to_excel(all_data)
        st.download_button(
            label="💾 Descargar Reporte Excel",
            data=excel_data,
            file_name="actas_procesadas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No se pudieron extraer datos.")
else:
    st.info("👈 Por favor, carga archivos usando el panel lateral.")

st.markdown("---")
st.markdown("*Nota: La precisión depende de la calidad de la imagen y el formato del acta.*")
