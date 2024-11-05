import streamlit as st
import pandas as pd
import requests
import json
import uuid
import base64
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Shipping Codes Processor", layout="wide")

def process_shipping_code(code):
    try:
        # Credenciales y autenticación
        username = "manifest"
        password = "SsTfQASQnbvLOjyAkmn"
        auth_token = base64.b64encode(f"{username}:{password}".encode()).decode()
        
        # Preparar la llamada a la API
        url = f"https://cloud-apps-01-int.cttexpress.com/manifest/api/v2/shippings/republish/{code}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {auth_token}'
        }
        
        # Generar datos para la petición
        correlation_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'
        
        data = {
            "audit": {
                "process_code": "CUST-ADQ-WEB",
                "user_code": "ricardo@cttexpress.com"
            },
            "metadata": {
                "correlation_id": correlation_id,
                "interchange_id": correlation_id,
                "source": "incident-sf-service",
                "timestamp": timestamp
            }
        }
        
        # Hacer la petición
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        return {
            "shipping_code": code,
            "status": response.status_code,
            "success": response.status_code == 200,
            "message": "Success" if response.status_code == 200 else response.text
        }
        
    except Exception as e:
        return {
            "shipping_code": code,
            "status": "error",
            "success": False,
            "message": str(e)
        }

def main():
    st.title("Procesador de Shipping Codes")
    
    # Área de carga de archivo
    uploaded_file = st.file_uploader("Selecciona un archivo Excel", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        try:
            # Leer el Excel
            df = pd.read_excel(uploaded_file, header=None)
            shipping_codes = df.iloc[:, 0].dropna().tolist()
            
            if st.button("Procesar Códigos"):
                # Barra de progreso
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Tabla para resultados
                results_container = st.container()
                results = []
                
                # Procesar cada código
                for i, code in enumerate(shipping_codes):
                    status_text.text(f"Procesando código {i+1} de {len(shipping_codes)}")
                    result = process_shipping_code(code)
                    results.append(result)
                    progress_bar.progress((i + 1) / len(shipping_codes))
                
                # Mostrar resultados
                status_text.text("¡Procesamiento completado!")
                
                # Convertir resultados a DataFrame para mejor visualización
                results_df = pd.DataFrame(results)
                results_container.dataframe(
                    results_df[['shipping_code', 'status', 'success', 'message']],
                    use_container_width=True
                )
                
                # Opción para descargar resultados
                csv = results_df.to_csv(index=False)
                st.download_button(
                    "Descargar Resultados",
                    csv,
                    "shipping_results.csv",
                    "text/csv",
                    key='download-csv'
                )
                
        except Exception as e:
            st.error(f"Error procesando el archivo: {str(e)}")

if __name__ == "__main__":
    main()
