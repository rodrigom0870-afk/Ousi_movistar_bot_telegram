import os
import json
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
GIST_TOKEN = os.environ["GIST_TOKEN"]
GIST_ID = "6ceeabbf4a35ca7a257df9136c0220c3"

API = f"https://api.telegram.org/bot{TOKEN}"
GIST_API = f"https://api.github.com/gists/{GIST_ID}"


def obtener_usuarios():
    r = requests.get(
        GIST_API,
        headers={
            "Authorization": f"Bearer {GIST_TOKEN}",
            "Accept": "application/vnd.github+json"
        },
        timeout=20
    )
    r.raise_for_status()

    contenido = r.json()["files"]["users.json"]["content"]
    return json.loads(contenido)


def guardar_usuarios(usuarios):
    r = requests.patch(
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
    r.raise_for_status()


usuarios = obtener_usuarios()

r = requests.get(
    f"{API}/getUpdates",
    params={"timeout": 1},
    timeout=10
)

r.raise_for_status()

updates = r.json().get("result", [])

for update in updates:
    message = update.get("message", {})
    texto = message.get("text", "").lower().strip()
    chat_id = str(message.get("chat", {}).get("id", ""))

    if not chat_id:
        continue

    if texto == "/start":
        if chat_id not in usuarios:
            usuarios.append(chat_id)
            guardar_usuarios(usuarios)

        requests.post(
            f"{API}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": "✅ Te registraste correctamente.\n\n"
                        "Recibirás una alerta cuando se detecten entradas."
            },
            timeout=20
        )

    elif texto == "/stop":
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
