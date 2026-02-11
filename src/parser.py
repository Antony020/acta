import re

def parse_certificate_data(text):
    """
    Parses raw text to find key fields: Name, Date of Birth, Parents, Place.
    Returns a dictionary with the findings.
    """
    data = {
        "Nombre": None,
        "NUI": None,
        "Numero de Libro": None,
        "Fecha de Nacimiento": None,
        "Padre": None,
        "Cedula Padre": None,
        "Madre": None,
        "Cedula Madre": None,
        "Texto Completo": text[:500] + "..." # Preview
    }

    # Normalize text
    # 1. Extract NUI (Número Único de Identidad)
    # Reverting to robust global search + label preference
    nui_pattern = re.search(r"N[uú]mero [ÚúUu]nico de Identidad[:.\s]*(\d{3}-\d{7}-\d{1})", text, re.IGNORECASE)
    if nui_pattern:
        data["NUI"] = nui_pattern.group(1)
    else:
        # Fallback: finding purely the pattern if label is misread
        # Be careful not to pick up other IDs, but usually NUI is prominent
        nui_fallback = re.search(r"(\d{3}-\d{7}-\d{1})", text)
        if nui_fallback:
             data["NUI"] = nui_fallback.group(1)

    # 2. Extract Name (Nombre)
    # Reverting to global search for stars pattern **** NAME ****
    # This was the most stable version.
    
    name_match = re.search(r"(?:\*[\s]*){2,}([A-ZÑÁÉÍÓÚ\s]+)(?:\*[\s]*){2,}", text)
    if name_match:
         candidate = name_match.group(1).strip()
         if "NÚMERO" not in candidate and "IDENTIDAD" not in candidate:
            # Clean OCR artifacts
            candidate = re.sub(r'\btc\b', '', candidate, flags=re.IGNORECASE)  # Remove "tc"
            candidate = re.sub(r'\s+', ' ', candidate)  # Normalize spaces
            data["Nombre"] = candidate.strip()
    
    # Fallback: Look for "perteneciente a"
    if not data["Nombre"]:
        fallback_name = re.search(r"perteneciente\s+a[:\s]*\n*([A-ZÑÁÉÍÓÚ\s]+)", text, re.IGNORECASE)
        if fallback_name:
             candidate = fallback_name.group(1).strip().split('\n')[0]
             candidate = candidate.replace("*", "").strip()
             # Clean OCR artifacts
             candidate = re.sub(r'\btc\b', '', candidate, flags=re.IGNORECASE)
             candidate = re.sub(r'\s+', ' ', candidate)
             data["Nombre"] = candidate.strip()

    # 3. Extract Book Number
    libro_match = re.search(r"Libro\s*No\.?\s*(\d+)", text, re.IGNORECASE)
    if libro_match:
        data["Numero de Libro"] = libro_match.group(1)

    # 4. Extract Date of Birth
    # Priority: Date matches (DD/MM/YYYY) inside parentheses
    match_strict = re.search(r"\((\d{1,2}/\d{1,2}/\d{4})\)", text)
    
    # Priority 2: 'nacido' followed by a date
    match_nacido = re.search(r"nacid[oa].*?(\d{1,2}/\d{1,2}/\d{4})", text, re.IGNORECASE | re.DOTALL)

    if match_strict:
        data["Fecha de Nacimiento"] = match_strict.group(1)
    elif match_nacido:
        data["Fecha de Nacimiento"] = match_nacido.group(1)
    else:
        pass # Keep empty

    # 5. Extract Parents and IDs
    
    # PADRE - Pattern: "PADRE: APELLIDO, NOMBRE" 
    # Handle multi-line names (OCR may split across lines)
    padre_match = re.search(r"PADRE[:\.\s]+([A-ZÑÁÉÍÓÚ\s,\n]+?)\s*,\s*pa[ií]s", text, re.IGNORECASE | re.DOTALL)
    if padre_match:
        raw_padre = padre_match.group(1).strip()
        # Remove newlines and clean up extra spaces
        raw_padre = raw_padre.replace('\n', ' ').replace('\r', ' ')
        raw_padre = re.sub(r'\s+', ' ', raw_padre)
        data["Padre"] = raw_padre.strip(" ,")
        
    # MADRE - Pattern: "MADRE: APELLIDO, NOMBRE"
    # Handle multi-line names (OCR may split across lines)
    madre_match = re.search(r"MADRE[:\.\s]+([A-ZÑÁÉÍÓÚ\s,\n]+?)\s*,\s*pa[ií]s", text, re.IGNORECASE | re.DOTALL)
    if madre_match:
        raw_madre = madre_match.group(1).strip()
        # Remove newlines and clean up extra spaces
        raw_madre = raw_madre.replace('\n', ' ').replace('\r', ' ')
        raw_madre = re.sub(r'\s+', ' ', raw_madre)
        data["Madre"] = raw_madre.strip(" ,")

    # CEDULAS - Extract all ID patterns and assign based on position
    ids = re.findall(r"(\d{3}-\d{7}-\d{1})", text)
    
    # Find positions of PADRE and MADRE keywords
    idx_padre = text.upper().find("PADRE")
    idx_madre = text.upper().find("MADRE")
    
    # Assign IDs based on proximity to keywords
    if ids:
        for id_val in ids:
            # Skip if this is the NUI we already found
            if data["NUI"] == id_val:
                continue
                
            idx_id = text.find(id_val)
            
            # If ID appears after PADRE but before MADRE -> Father's ID
            if idx_padre != -1 and idx_id > idx_padre:
                if idx_madre == -1 or idx_id < idx_madre:
                    if not data["Cedula Padre"]:  # Only assign first match
                        data["Cedula Padre"] = id_val
            
            # If ID appears after MADRE -> Mother's ID (changed from elif to if)
            if idx_madre != -1 and idx_id > idx_madre:
                if not data["Cedula Madre"]:  # Only assign first match
                    data["Cedula Madre"] = id_val

    return data
