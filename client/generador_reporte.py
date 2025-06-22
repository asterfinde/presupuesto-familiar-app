# generador_reporte.py - El Cliente de Escritorio

import pandas as pd
from jinja2 import Environment, FileSystemLoader
import json
import sys
import os
import requests # <--- ¡Nueva importación!

# --- CONSTANTES ---
# Esta es la URL de tu servidor FastAPI. 
# Para pruebas locales, es esta. Para producción, será tu URL pública.
SERVER_URL = "http://127.0.0.1:8000/analizar" 

# La función resource_path() no cambia.
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- ARCHIVOS ---
EXCEL_FILE = 'gastos.xlsx'
TEMPLATE_FILE = 'plantilla_presupuesto.html'
OUTPUT_FILE = 'reporte_final.html'

# --- SCRIPT PRINCIPAL ---
try:
    # 1. Leer y procesar datos de Excel (sin cambios)
    print("Leyendo archivo de gastos...")
    df = pd.read_excel(EXCEL_FILE, sheet_name='Gastos')
    df_sorted = df.sort_values(by='Monto', ascending=False)
    datos_gastos_dict = df_sorted.rename(columns={'Categoria': 'categoria', 'Monto': 'monto'}).to_dict('records')
    datos_gastos_json = json.dumps(datos_gastos_dict, indent=4)

    # 2. Llamar a nuestro Servidor para obtener el análisis (NUEVA LÓGICA)
    print(f"Contactando a nuestro servidor en {SERVER_URL} para el análisis...")
    
    # Preparamos los datos en el formato que nuestra API espera (definido en Pydantic)
    payload = {"gastos": datos_gastos_dict}
    
    # Hacemos la petición POST a nuestro servidor FastAPI
    response = requests.post(SERVER_URL, json=payload)
    
    # Verificamos si la petición fue exitosa
    response.raise_for_status() 
    
    # Extraemos los análisis del JSON de respuesta
    ai_data = response.json()
    analisis_detallado = ai_data.get("analisis_detallado", "<p>Error: No se recibió análisis.</p>")
    estrategias_control = ai_data.get("estrategias_control", "<p>Error: No se recibieron estrategias.</p>")
    print("Análisis recibido exitosamente.")

    # 3. Renderizar la plantilla HTML (actualizado)
    env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))))
    template = env.get_template(TEMPLATE_FILE)
    
    html_final = template.render(
        datos_gastos_json=datos_gastos_json,
        analisis_detallado=analisis_detallado,
        estrategias_control=estrategias_control
    )

    # 4. Guardar el reporte final (sin cambios)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_final)

    print(f"\n¡Éxito! Se ha generado el archivo '{OUTPUT_FILE}'.")
    input("Presiona Enter para salir.")

except requests.exceptions.RequestException as e:
    print(f"\nERROR DE CONEXIÓN: No se pudo conectar con el servidor en {SERVER_URL}.")
    print(f"Asegúrate de que el servidor (uvicorn main:app --reload) esté corriendo.")
    print(f"Detalle del error: {e}")
    input("Presiona Enter para salir.")
except Exception as e:
    print(f"\nOcurrió un error inesperado: {e}")
    input("Presiona Enter para salir.")