import os
import json
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
GIST_TOKEN = os.environ["GIST_TOKEN"]
GIST_ID = "6ceeabbf4a35ca7a257df9136c0220c3"

API = f"https://api.telegram.org/bot{TOKEN}"
GIST_API = f"https://api.github.com/gists/{GIST_ID}"


def obtener_usuarios():
    print("📂 Leyendo users.json...")

    r = requests.get(
        GIST_API,
        headers={
            "Authorization": f"Bearer {GIST_TOKEN}",
            "Accept": "application/vnd.github+json"
        },
        timeout=20
    )

    print("Gist status:", r.status_code)

    r.raise_for_status()

    data = r.json()
    contenido = data["files"]["users.json"]["content"]

    usuarios = json.loads(contenido)

    print("👥 Usuarios actuales:", usuarios)

    return usuarios


def guardar_usuarios(usuarios):
    print("💾 Guardando usuarios:", usuarios)

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

    print("Guardar Gist status:", r.status_code)

    if r.status_code != 200:
        print("Respuesta de GitHub:", r.text)

    r.raise_for_status()


def enviar(chat_id, texto):
    print(f"📤 Enviando mensaje a {chat_id}")

    r = requests.post(
        f"{API}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": texto
        },
        timeout=20
    )

    print("Telegram status:", r.status_code)

    r.raise_for_status()


print("🤖 Iniciando bot...")

usuarios = obtener_usuarios()


# Obtener mensajes pendientes
r = requests.get(
    f"{API}/getUpdates",
    params={
        "timeout": 1,
        "allowed_updates": json.dumps(["message"])
    },
    timeout=10
)

print("Telegram getUpdates status:", r.status_code)

if r.status_code == 409:
    print("❌ ERROR 409: otra ejecución está usando Telegram.")
    print(r.text)
    exit(1)

r.raise_for_status()

updates = r.json().get("result", [])

print("📩 Mensajes encontrados:", len(updates))


for update in updates:

    message = update.get("message", {})

    texto = message.get("text", "").lower().strip()

    chat_id = str(
        message.get("chat", {}).get("id", "")
    )

    print(
        f"Mensaje recibido: '{texto}' "
        f"de chat_id: {chat_id}"
    )

    if not chat_id:
        continue


    if texto == "/start":

        if chat_id not in usuarios:

            usuarios.append(chat_id)

            guardar_usuarios(usuarios)

            print("✅ Usuario agregado.")

        else:

            print("ℹ️ El usuario ya estaba registrado.")


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

            print("🛑 Usuario eliminado.")

        else:

            print("ℹ️ El usuario no estaba registrado.")


        enviar(
            chat_id,
            "🛑 Dejaste de recibir alertas."
        )


print("✅ Bot terminado correctamente.")
print("👥 Usuarios finales:", usuarios)
