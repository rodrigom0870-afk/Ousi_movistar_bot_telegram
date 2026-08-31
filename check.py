import os
import requests

URL = "https://www.movistararena.com.ar/show/949f1877-625b-479f-893a-1ae09da0f00f"

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]


def telegram(message):
    response = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": message,
            "disable_web_page_preview": False
        },
        timeout=20
    )
    response.raise_for_status()


response = requests.get(
    URL,
    headers={
        "User-Agent": "Mozilla/5.0"
    },
    timeout=30
)

response.raise_for_status()

content = response.text.lower()

# Palabras que pueden indicar que hay entradas disponibles
available_words = [
    "comprar",
    "comprá",
    "seleccionar entradas",
    "seleccionar sector",
    "tickets",
    "entradas disponibles",
    "disponible",
    "disponibles"
]

# Palabras que indican que está agotado
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
    )
