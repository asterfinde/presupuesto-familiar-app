# test_anthropic.py
import os
import anthropic
from dotenv import load_dotenv

print("Iniciando prueba de conexión directa con Anthropic...")

# Cargar la misma API key desde el archivo .env
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("ERROR: No se pudo encontrar la ANTHROPIC_API_KEY en el archivo .env")
else:
    try:
        print("API Key encontrada. Creando cliente de Anthropic...")
        client = anthropic.Anthropic(api_key=api_key)

        print("Enviando un mensaje de prueba a la API...")
        message = client.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=20,
            messages=[
                {
                    "role": "user",
                    "content": "Hola, esto es solo una prueba de conexión. Responde 'OK'."
                }
            ]
        )

        print("\n=============================================")
        print("¡ÉXITO! La conexión con Anthropic funciona.")
        print(f"Respuesta de la IA: {message.content[0].text}")
        print("=============================================")

    except anthropic.AuthenticationError as e:
        print("\n===================================================================")
        print("FALLO LA PRUEBA: Error de Autenticación (AuthenticationError).")
        print("Esto confirma que la API KEY es INCORRECTA o está INACTIVA.")
        print(f"Detalle del error: {e}")
        print("===================================================================")
    except Exception as e:
        print("\n===================================================================")
        print(f"FALLO LA PRUEBA: Ocurrió un error inesperado.")
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Detalle del error: {e}")
        print("===================================================================")