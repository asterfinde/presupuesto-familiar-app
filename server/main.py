# main.py - Tu Servidor de Análisis (Versión con Lazy Initialization)

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import anthropic

load_dotenv()

class Gasto(BaseModel):
    categoria: str
    monto: float

class AnalisisRequest(BaseModel):
    gastos: list[Gasto]

app = FastAPI(
    title="API de Análisis de Presupuesto",
    description="Un intermediario seguro para analizar gastos usando la IA de Anthropic."
)

# NOTA: Hemos quitado la inicialización del cliente de Anthropic de aquí.

@app.post("/analizar", summary="Analiza una lista de gastos")
async def analizar_gastos(request_data: AnalisisRequest):
    """
    Recibe una lista de gastos, la formatea y la envía a la API de Anthropic
    para obtener un análisis detallado y estrategias de control.
    """
    
    # --- INICIALIZACIÓN DEL CLIENTE DENTRO DEL ENDPOINT ---
    # El cliente de Anthropic ahora se crea solo cuando se llama a esta función.
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("La variable de entorno ANTHROPIC_API_KEY no está configurada.")
        
        anthropic_client = anthropic.Anthropic(api_key=api_key)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Error de configuración en el servidor: {e}")
    # --- FIN DE LA INICIALIZACIÓN ---

    gastos_str = "\n".join([f"- {g.categoria}: ${g.monto:,.2f}" for g in request_data.gastos])
    prompt = f"""
    Eres un amigable asesor financiero peruano...
    ... (El resto del prompt se mantiene igual) ...
    """

    try:
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514", # Usando tu modelo validado
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