import os
import time
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

API = f"https://api.telegram.org/bot{TOKEN}"


def responder(mensaje):
    requests.post(
        f"{API}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": mensaje
        },
        timeout=20
    )


offset = None

print("🤖 Bot de prueba iniciado.")

while True:
    try:
        respuesta = requests.get(
            f"{API}/getUpdates",
            params={
                "offset": offset,
                "timeout": 20
            },
            timeout=30
        )

        datos = respuesta.json()

        for update in datos.get("result", []):
            offset = update["update_id"] + 1

            mensaje = update.get("message", {})
            texto = mensaje.get("text", "")
            chat_id = str(mensaje.get("chat", {}).get("id", ""))

            if chat_id != CHAT_ID:
                continue

            if texto.lower().strip() == "prueba":
                print("📩 Recibido: prueba")

                time.sleep(30)

                responder(
                    "✅ Prueba exitosa.\n\n"
                    "El bot recibió tu mensaje y respondió correctamente."
                )

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
