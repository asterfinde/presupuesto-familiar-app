# generador_reporte.py - VERSIÓN FINAL CON MANEJO DE ERRORES ROBUSTO

import pandas as pd
from jinja2 import Environment, FileSystemLoader
import json
import sys
import os
import requests

SERVER_URL = "https://presupuesto-familiar-app.vercel.app/analizar" 

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

EXCEL_FILE = 'gastos.xlsx' 
TEMPLATE_FILE_PATH = resource_path('plantilla_presupuesto.html')
OUTPUT_FILE = 'reporte_final.html'

# --- INICIO DE LA CORRECCIÓN: Función para pausar sin errores ---
def pausar_y_salir():
    """Espera a que el usuario presione Enter, ignorando Ctrl+C."""
    try:
        input("Presiona Enter para salir.")
    except KeyboardInterrupt:
        pass
# --- FIN DE LA CORRECCIÓN ---

try:
    print("Leyendo archivo de gastos...")
    df = pd.read_excel(EXCEL_FILE, sheet_name='Gastos')
    df_sorted = df.sort_values(by='Monto', ascending=False)
    datos_gastos_dict = df_sorted.rename(columns={'Categoria': 'categoria', 'Monto': 'monto'}).to_dict('records')
    datos_gastos_json = json.dumps(datos_gastos_dict, indent=4)

    print(f"Contactando a nuestro servidor en {SERVER_URL} para el análisis...")
    payload = {"gastos": datos_gastos_dict}
    response = requests.post(SERVER_URL, json=payload)
    response.raise_for_status() 
    
    ai_data = response.json()
    analisis_detallado = ai_data.get("analisis_detallado", "<p>Error: No se recibió análisis.</p>")
    estrategias_control = ai_data.get("estrategias_control", "<p>Error: No se recibieron estrategias.</p>")
    print("Análisis recibido exitosamente.")

    template_dir = os.path.dirname(TEMPLATE_FILE_PATH)
    template_file_name = os.path.basename(TEMPLATE_FILE_PATH)
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file_name)
    
    html_final = template.render(
        datos_gastos_json=datos_gastos_json,
        analisis_detallado=analisis_detallado,
        estrategias_control=estrategias_control
    )

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_final)

    print(f"\n¡Éxito! Se ha generado el archivo '{OUTPUT_FILE}'.")
    pausar_y_salir()

except FileNotFoundError:
    print(f"\nERROR: No se pudo encontrar el archivo '{EXCEL_FILE}'.")
    print("Asegúrate de que el archivo de Excel esté en la misma carpeta que el programa .exe.")
    pausar_y_salir()
except requests.exceptions.RequestException as e:
    print(f"\nERROR DE CONEXIÓN: No se pudo conectar con el servidor en {SERVER_URL}.")
    print(f"Asegúrate de tener una conexión a internet.")
    print(f"Detalle del error: {e}")
    pausar_y_salir()
except Exception as e:
    print(f"\nOcurrió un error inesperado: {e}")
    pausar_y_salir()