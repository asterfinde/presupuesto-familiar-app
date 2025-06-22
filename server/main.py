# main.py - Tu Servidor de Análisis con FastAPI (VERSIÓN DE DEPURACIÓN)

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import anthropic

# Cargar las variables de entorno (tu API key) del archivo .env
load_dotenv()

# --- 1. Definición de Modelos de Datos con Pydantic ---
class Gasto(BaseModel):
    categoria: str
    monto: float

class AnalisisRequest(BaseModel):
    gastos: list[Gasto]

# --- 2. Creación e inicialización de la App FastAPI ---
app = FastAPI(
    title="API de Análisis de Presupuesto",
    description="Un intermediario seguro para analizar gastos usando la IA de Anthropic."
)

# Inicializa el cliente de Anthropic una sola vez
try:
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    if not ANTHROPIC_API_KEY:
        raise ValueError("La variable de entorno ANTHROPIC_API_KEY no está configurada.")
    
    anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
except ValueError as e:
    print(f"Error de inicialización: {e}")
    anthropic_client = None


# --- 3. Creación del "Endpoint" de la API ---
@app.post("/analizar", summary="Analiza una lista de gastos")
async def analizar_gastos(request_data: AnalisisRequest):
    if not anthropic_client:
        raise HTTPException(status_code=500, detail="El servidor no está configurado correctamente con la API Key de Anthropic.")

    gastos_str = "\n".join([f"- {g.categoria}: ${g.monto:,.2f}" for g in request_data.gastos])
    prompt = f"""
    Eres un amigable asesor financiero peruano. Tu tarea es analizar una lista de gastos mensuales y generar un reporte en dos partes, usando formato HTML.
    La moneda es Soles (puedes usar el símbolo S/ o $).

    Aquí están los datos de gastos del mes:
    {gastos_str}

    Por favor, genera lo siguiente:

    PARTE 1: Un "Análisis Detallado de tu Presupuesto".
    - Comienza con un título `<h2>Análisis Detallado de tu Presupuesto</h2>`.
    - Escribe un párrafo introductorio.
    - Identifica las 3 a 5 categorías principales de gasto y su impacto porcentual.
    - Clasifica algunos gastos como "Necesidades vs. Deseos" o "Fijos vs. Variables", dando ejemplos concretos de la lista.
    - Ofrece una observación clave o un patrón que notes en los datos de este mes.
    - Usa etiquetas HTML como `<p>`, `<h3>` para subtítulos, `<ul>` y `<li>` para listas.

    ---SEPARADOR---

    PARTE 2: "Estrategias de Control".
    - Comienza con un título `<h2>Estrategias para Controlar Gastos Excesivos</h2>`.
    - Basado en los gastos más altos o variables, ofrece de 3 a 5 estrategias personalizadas y accionables para este usuario.
    - Usa etiquetas HTML, preferiblemente `<details>` y `<summary>` para que sea interactivo.

    No incluyas `<html>` o `<body>`. Solo el contenido para las secciones.
    """

    try:
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        
        respuesta_completa = message.content[0].text
        partes = respuesta_completa.split('---SEPARADOR---')

        if len(partes) != 2:
            raise HTTPException(status_code=500, detail="La respuesta de la IA no tuvo el formato esperado.")

        return {
            "analisis_detallado": partes[0].strip(),
            "estrategias_control": partes[1].strip()
        }

    except Exception as e:
        # --- LÍNEA DE DEPURACIÓN CRÍTICA ---
        # Imprimimos el error real en la consola del servidor para poder verlo.
        print(f"!!! ERROR INTERNO DETALLADO: Tipo: {type(e).__name__}, Mensaje: {e} !!!")
        # ---
        
        # Mantenemos el error 502 para el cliente.
        raise HTTPException(status_code=502, detail=f"Error al comunicarse con la API de Anthropic: {str(e)}")