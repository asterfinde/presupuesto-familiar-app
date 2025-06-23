# generador_reporte.py - El Cliente de Escritorio (Versión Final)

import pandas as pd
from jinja2 import Environment, FileSystemLoader
import json
import sys
import os
import requests

SERVER_URL = "https://my-budgen.onrender.com/analizar" 

# La función resource_path() es para encontrar archivos empaquetados DENTRO del .exe
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- ARCHIVOS ---
# El Excel es un archivo EXTERNO, lo buscamos en la carpeta actual. No usamos resource_path.
EXCEL_FILE = 'gastos.xlsx' 
# La plantilla es un recurso INTERNO, empaquetado, usamos resource_path para encontrarla.
TEMPLATE_FILE_PATH = resource_path('plantilla_presupuesto.html')
OUTPUT_FILE = 'reporte_final.html'

# --- SCRIPT PRINCIPAL ---
try:
    print("Leyendo archivo de gastos...")
    # 1. Leer y procesar datos de Excel (sin cambios, leerá el archivo externo)
    df = pd.read_excel(EXCEL_FILE, sheet_name='Gastos')
    df_sorted = df.sort_values(by='Monto', ascending=False)
    datos_gastos_dict = df_sorted.rename(columns={'Categoria': 'categoria', 'Monto': 'monto'}).to_dict('records')
    datos_gastos_json = json.dumps(datos_gastos_dict, indent=4)

    # 2. Llamar a nuestro Servidor para obtener el análisis (sin cambios)
    print(f"Contactando a nuestro servidor en {SERVER_URL} para el análisis...")
    payload = {"gastos": datos_gastos_dict}
    response = requests.post(SERVER_URL, json=payload)
    response.raise_for_status() 
    
    ai_data = response.json()
    analisis_detallado = ai_data.get("analisis_detallado", "<p>Error: No se recibió análisis.</p>")
    estrategias_control = ai_data.get("estrategias_control", "<p>Error: No se recibieron estrategias.</p>")
    print("Análisis recibido exitosamente.")

    # 3. Renderizar la plantilla HTML (ajustado para máxima compatibilidad)
    template_dir = os.path.dirname(TEMPLATE_FILE_PATH)
    template_file_name = os.path.basename(TEMPLATE_FILE_PATH)
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file_name)
    
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

except FileNotFoundError:
    print(f"\nERROR: No se pudo encontrar el archivo '{EXCEL_FILE}'.")
    print("Asegúrate de que el archivo de Excel esté en la misma carpeta que el programa .exe.")
    input("Presiona Enter para salir.")
except requests.exceptions.RequestException as e:
    print(f"\nERROR DE CONEXIÓN: No se pudo conectar con el servidor en {SERVER_URL}.")
    print(f"Asegúrate de tener una conexión a internet.")
    print(f"Detalle del error: {e}")
    input("Presiona Enter para salir.")
except Exception as e:
    print(f"\nOcurrió un error inesperado: {e}")
    input("Presiona Enter para salir.")