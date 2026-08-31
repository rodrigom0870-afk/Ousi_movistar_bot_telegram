import os
import requests
import hashlib

URL = "https://www.movistararena.com.ar/show/949f1877-625b-479f-893a-1ae09da0f00f"

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def telegram(message):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": message,
            "disable_web_page_preview": False
        },
        timeout=20
    )

response = requests.get(
    URL,
    headers={
        "User-Agent": "Mozilla/5.0"
    },
    timeout=30
)

response.raise_for_status()

content = response.text.lower()

# Buscamos indicios de disponibilidad
available_words = [
    "comprar",
    "seleccionar entradas",
    "seleccionar sector",
    "disponible"
]

sold_out_words = [
    "agotado",
    "agotadas",
    "sold out"
]

available = any(word in content for word in available_words)
sold_out = any(word in content for word in sold_out_words)

if available and not sold_out:
    telegram(
        "🚨 ¡ATENCIÓN!\n\n"
        "Puede haber entradas disponibles para el show.\n\n"
        f"{URL}"
        telegram("✅ Prueba del bot: Telegram funciona correctamente.")
    )
