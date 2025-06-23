# api/index.py - VERSIÓN FINAL CORREGIDA

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import anthropic

load_dotenv()

try:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("La variable de entorno ANTHROPIC_API_KEY no está configurada. La aplicación no puede iniciar.")
    
    anthropic_client = anthropic.Anthropic(api_key=api_key)
    print("Cliente de Anthropic inicializado exitosamente al arrancar.")

except Exception as e:
    print(f"ERROR CRÍTICO AL INICIAR: No se pudo crear el cliente de Anthropic. {e}")
    anthropic_client = None

class Gasto(BaseModel):
    categoria: str
    monto: float

class AnalisisRequest(BaseModel):
    gastos: list[Gasto]

app = FastAPI(
    title="API de Análisis de Presupuesto",
    description="Un intermediario seguro para analizar gastos usando la IA de Anthropic."
)

@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check():
    return {"status": "ok"}

@app.post("/analizar", summary="Analiza una lista de gastos")
async def analizar_gastos(request_data: AnalisisRequest):
    if not anthropic_client:
        raise HTTPException(status_code=503, detail="El servicio de análisis no está disponible por un error de configuración inicial.")

    gastos_str = "\n".join([f"- {g.categoria}: ${g.monto:,.2f}" for g in request_data.gastos])
    
    # --- INICIO DE LA CORRECCIÓN ---
    # Este es el prompt detallado y completo que la IA necesita.
    prompt = f"""
    Eres un amigable asesor financiero peruano. Tu tarea es analizar la siguiente lista de gastos mensuales y generar un reporte en dos partes, usando formato HTML.

    Los gastos a analizar son:
    {gastos_str}

    Por favor, estructura tu respuesta exactamente de la siguiente manera:

    **PARTE 1: ANÁLISIS DETALLADO**
    Comienza con un saludo cordial y un resumen general de los gastos del mes. Luego, describe los gastos más significativos en formato de lista `<ul>` y `<li>`. Termina con una conclusión sobre la salud financiera general.

    ---SEPARADOR---

    **PARTE 2: ESTRATEGIAS DE CONTROL**
    Basado en el análisis anterior, ofrece una lista de 3 a 5 estrategias claras y accionables para que el usuario pueda controlar o reducir sus gastos. Usa un tono motivador y presenta las estrategias en una lista ordenada `<ol>` y `<li>`.
    """
    # --- FIN DE LA CORRECCIÓN ---

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
        raise HTTPException(status_code=502, detail=f"Error al comunicarse con la API de Anthropic: {str(e)}")