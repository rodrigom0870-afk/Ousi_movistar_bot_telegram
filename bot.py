import os
import requests
import time

TOKEN = os.environ["TELEGRAM_TOKEN"]
GIST_TOKEN = os.environ["GIST_TOKEN"]
GIST_ID = "6ceeabbf4a35ca7a257df9136c0220c3"

API = f"https://api.telegram.org/bot{TOKEN}"
GIST_API = f"https://api.github.com/gists/{GIST_ID}"


def obtener_usuarios():
    response = requests.get(
        GIST_API,
        headers={
            "Authorization": f"Bearer {GIST_TOKEN}",
            "Accept": "application/vnd.github+json"
        },
        timeout=20
    )
    response.raise_for_status()

    data = response.json()
    contenido = data["files"]["users.json"]["content"]

    import json
    return json.loads(contenido)


def guardar_usuarios(usuarios):
    import json

    response = requests.patch(
        GIST_API,
        headers={
            "Authorization": f"Bearer {GIST_TOKEN}",
            "Accept": "application/vnd.github+json"
        },
        json={
            "files": {
                "users.json": {
                    "content": json.dumps(usuarios)
                }
            }
        },
        timeout=20
    )
    response.raise_for_status()


offset = None

print("🤖 Bot de alertas iniciado.")

while True:
    try:
        response = requests.get(
            f"{API}/getUpdates",
            params={
                "offset": offset,
                "timeout": 20
            },
            timeout=30
        )

        data = response.json()

        for update in data.get("result", []):
            offset = update["update_id"] + 1

            message = update.get("message", {})
            text = message.get("text", "").lower().strip()
            chat_id = str(message.get("chat", {}).get("id", ""))

            if not chat_id:
                continue

            usuarios = obtener_usuarios()

            if text == "/start":
                if chat_id not in usuarios:
                    usuarios.append(chat_id)
                    guardar_usuarios(usuarios)

                requests.post(
                    f"{API}/sendMessage",
                    data={
                        "chat_id": chat_id,
                        "text": "✅ Te registraste correctamente.\n\n"
                                "Recibirás una alerta cuando se detecten "
                                "entradas disponibles."
                    },
                    timeout=20
                )

            elif text == "/stop":
                if chat_id in usuarios:
                    usuarios.remove(chat_id)
                    guardar_usuarios(usuarios)

                requests.post(
                    f"{API}/sendMessage",
                    data={
                        "chat_id": chat_id,
                        "text": "🛑 Dejaste de recibir alertas."
                    },
                    timeout=20
                )

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
