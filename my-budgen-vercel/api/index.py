# api/index.py - VERSIÓN FINAL CON PARSEO ROBUSTO

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import anthropic

load_dotenv()

try:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("La variable de entorno ANTHROPIC_API_KEY no está configurada.")
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

app = FastAPI(title="API de Análisis de Presupuesto")

@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check():
    return {"status": "ok"}

@app.post("/analizar", summary="Analiza una lista de gastos")
async def analizar_gastos(request_data: AnalisisRequest):
    if not anthropic_client:
        raise HTTPException(status_code=503, detail="El servicio de análisis no está disponible.")

    gastos_str = "\n".join([f"- {g.categoria}: ${g.monto:,.2f}" for g in request_data.gastos])
    prompt = f"""
    Eres un amigable asesor financiero peruano. Tu tarea es analizar la siguiente lista de gastos mensuales y generar un reporte en dos partes, usando formato HTML. Los gastos a analizar son:\n{gastos_str}\nPor favor, estructura tu respuesta exactamente de la siguiente manera:\n\n**PARTE 1: ANÁLISIS DETALLADO**\nComienza con un saludo cordial y un resumen general de los gastos del mes. Luego, describe los gastos más significativos en formato de lista `<ul>` y `<li>`. Termina con una conclusión sobre la salud financiera general.\n\n---SEPARADOR---\n\n**PARTE 2: ESTRATEGIAS DE CONTROL**\nBasado en el análisis anterior, ofrece una lista de 3 a 5 estrategias claras y accionables para que el usuario pueda controlar o reducir sus gastos. Usa un tono motivador y presenta las estrategias en una lista ordenada `<ol>` y `<li>`.
    """
    
    try:
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        
        respuesta_completa = message.content[0].text
        
        # --- INICIO DE LA CORRECCIÓN: PARSEO ROBUSTO ---
        separador = '---SEPARADOR---'
        if separador in respuesta_completa:
            indice_separador = respuesta_completa.find(separador)
            analisis_detallado = respuesta_completa[:indice_separador].strip()
            estrategias_control = respuesta_completa[indice_separador + len(separador):].strip()
        else:
            # Si el separador no se encuentra, levanta el error 500 como antes.
            raise HTTPException(status_code=500, detail="La respuesta de la IA no tuvo el formato esperado (no se encontró el separador).")
        # --- FIN DE LA CORRECCIÓN ---

        return {
            "analisis_detallado": analisis_detallado,
            "estrategias_control": estrategias_control
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al comunicarse con la API de Anthropic: {str(e)}")