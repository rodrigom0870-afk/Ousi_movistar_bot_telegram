import os
import json
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
GIST_TOKEN = os.environ["GIST_TOKEN"]
GIST_ID = "6ceeabbf4a35ca7a257df9136c0220c3"

API = f"https://api.telegram.org/bot{TOKEN}"
GIST_API = f"https://api.github.com/gists/{GIST_ID}"

OFFSET_FILE = "telegram_offset.json"


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
                    "content": json.dumps(usuarios, indent=2)
                }
            }
        },
        timeout=20
    )
    r.raise_for_status()


def obtener_offset():
    try:
        r = requests.get(
            GIST_API,
            headers={
                "Authorization": f"Bearer {GIST_TOKEN}",
                "Accept": "application/vnd.github+json"
            },
            timeout=20
        )
        r.raise_for_status()

        data = r.json()

        if "telegram_offset.json" not in data["files"]:
            return None

        contenido = data["files"]["telegram_offset.json"]["content"]
        return json.loads(contenido).get("offset")

    except Exception:
        return None


def guardar_offset(offset):
    r = requests.patch(
        GIST_API,
        headers={
            "Authorization": f"Bearer {GIST_TOKEN}",
            "Accept": "application/vnd.github+json"
        },
        json={
            "files": {
                "telegram_offset.json": {
                    "content": json.dumps({"offset": offset})
                }
            }
        },
        timeout=20
    )
    r.raise_for_status()


def enviar(chat_id, texto):
    r = requests.post(
        f"{API}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": texto
        },
        timeout=20
    )
    r.raise_for_status()


print("🤖 Iniciando bot...")

usuarios = obtener_usuarios()
offset = obtener_offset()

print("👥 Usuarios registrados:", usuarios)
print("➡️ Offset actual:", offset)

params = {
    "timeout": 1,
    "allowed_updates": json.dumps(["message"])
}

if offset is not None:
    params["offset"] = offset


r = requests.get(
    f"{API}/getUpdates",
    params=params,
    timeout=10
)

if r.status_code == 409:
    print("❌ Telegram está siendo utilizado por otra ejecución.")
    exit(1)

r.raise_for_status()

updates = r.json().get("result", [])

print("📩 Mensajes nuevos:", len(updates))


for update in updates:

    update_id = update["update_id"]

    # Guardamos inmediatamente el siguiente offset.
    # Así este mensaje no vuelve a procesarse.
    guardar_offset(update_id + 1)

    message = update.get("message", {})

    texto = message.get("text", "").lower().strip()

    chat_id = str(
        message.get("chat", {}).get("id", "")
    )

    if not chat_id:
        continue

    print(f"📨 Mensaje: {texto} | Chat: {chat_id}")

    if texto == "/start":

        if chat_id not in usuarios:
            usuarios.append(chat_id)
            guardar_usuarios(usuarios)

            print("✅ Usuario agregado:", chat_id)

        else:
            print("ℹ️ Usuario ya registrado:", chat_id)

        enviar(
            chat_id,
            "✅ Te registraste correctamente.\n\n"
            "Recibirás alertas cuando se detecten "
            "entradas disponibles."
        )

    elif texto == "/stop":

        if chat_id in usuarios:
            usuarios.remove(chat_id)
            guardar_usuarios(usuarios)

            print("🛑 Usuario eliminado:", chat_id)

        enviar(
            chat_id,
            "🛑 Dejaste de recibir alertas."
        )


print("✅ Bot terminado.")
