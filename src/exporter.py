import pandas as pd
import io

def to_excel(data_list):
    """
    Converts a list of dictionaries to an Excel file in memory.
    Returns the bytes of the Excel file.
    """
    df = pd.DataFrame(data_list)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos Extraídos')
        
    return output.getvalue()
