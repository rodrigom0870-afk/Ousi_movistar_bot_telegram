import os
import requests
from playwright.sync_api import sync_playwright

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


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page(
        user_agent="Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36"
    )

    try:
        page.goto(URL, wait_until="networkidle", timeout=60000)
    except Exception:
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)

    page.wait_for_timeout(5000)

    content = page.locator("body").inner_text()

    print("========== TEXTO QUE VE EL BOT ==========")
    print(content)
    print("========== FIN DEL TEXTO ==========")

    browser.close()
