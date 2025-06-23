# main.py - VERSIÓN FINAL CON CLIENTE GLOBAL

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import anthropic

# --- PASO 1: Cargar variables de entorno al inicio ---
load_dotenv()

# --- PASO 2: Crear el cliente de Anthropic UNA SOLA VEZ ---
# Se inicializa cuando el servidor arranca, no en cada petición.
try:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        # Si la clave no existe al arrancar, la app no podrá funcionar.
        # Es mejor que falle aquí que en una petición del usuario.
        raise ValueError("La variable de entorno ANTHROPIC_API_KEY no está configurada. La aplicación no puede iniciar.")
    
    # Cliente global que será reutilizado
    anthropic_client = anthropic.Anthropic(api_key=api_key)
    print("Cliente de Anthropic inicializado exitosamente al arrancar.")

except Exception as e:
    # Si la inicialización falla, lo sabremos por los logs de Render al desplegar.
    print(f"ERROR CRÍTICO AL INICIAR: No se pudo crear el cliente de Anthropic. {e}")
    anthropic_client = None


# --- Definición de la App y Modelos Pydantic (sin cambios) ---
class Gasto(BaseModel):
    categoria: str
    monto: float

class AnalisisRequest(BaseModel):
    gastos: list[Gasto]

app = FastAPI(
    title="API de Análisis de Presupuesto",
    description="Un intermediario seguro para analizar gastos usando la IA de Anthropic."
)

# --- Endpoints ---

@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check():
    return {"status": "ok"}

@app.post("/analizar", summary="Analiza una lista de gastos")
async def analizar_gastos(request_data: AnalisisRequest):
    """
    Recibe gastos, los formatea y usa el cliente GLOBAL de Anthropic
    para obtener el análisis.
    """
    # --- PASO 3: Usar el cliente que ya existe ---
    if not anthropic_client:
        raise HTTPException(status_code=503, detail="El servicio de análisis no está disponible por un error de configuración inicial.")

    gastos_str = "\n".join([f"- {g.categoria}: ${g.monto:,.2f}" for g in request_data.gastos])
    prompt = f"""
    Eres un amigable asesor financiero peruano. Tu tarea es analizar una lista 
    de gastos mensuales y generar un reporte en dos partes, usando formato HTML.
    ---SEPARADOR---
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
        # Este error ahora es por un fallo en la comunicación, no en la inicialización.
        raise HTTPException(status_code=502, detail=f"Error al comunicarse con la API de Anthropic: {str(e)}")