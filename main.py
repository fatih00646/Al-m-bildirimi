import json
import os
import requests
from bs4 import BeautifulSoup

# Telegram Ayarları (Senin Bilgilerin)
TOKEN = "8979084549:AAEaMSbFuJ7MKPgGaS4OWRP-jA8AoDzoo1c"
CHAT_ID = "1380317134"

# Taranacak Kaynak (Kamu İlan Portalı)
URL = "https://kamuilan.sbb.gov.tr/"
SEEN_FILE = "seen_ads.json"


def send_telegram_message(text):
  url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
  payload = {
      "chat_id": CHAT_ID,
      "text": text,
      "parse_mode": "HTML",
      "disable_web_page_preview": True,
  }
  try:
    response = requests.post(url, json=payload, timeout=10)
    return response.json()
  except Exception as e:
    print(f"Telegram mesajı gönderilemedi: {e}")


def load_seen_ads():
  if os.path.exists(SEEN_FILE):
    try:
      with open(SEEN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      return []
  return []


def save_seen_ads(seen_ads):
  with open(SEEN_FILE, "w", encoding="utf-8") as f:
    json.dump(seen_ads[-200:], f, ensure_ascii=False, indent=4)  # Son 200 ilanı sakla


def check_announcements():
  print("Kamu ilanları taranıyor...")
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }

  try:
    response = requests.get(URL, headers=headers, timeout=15)
    if response.status_code != 200:
      print(f"Siteye ulaşılamadı. Kod: {response.status_code}")
      return

    soup = BeautifulSoup(response.text, "html.parser")
    seen_ads = load_seen_ads()
    new_ads_found = False

    # İlan kartlarını veya linklerini yakalama (SBB altyapısına uyumlu seçiciler)
    # Sitedeki ilan öğelerini tarıyoruz
    items = soup.find_all("a", href=True)

    for item in items:
      href = item.get("href", "")
      title = item.get_text(strip=True)

      # İlan linki kriterlerine uyan metinleri filtrele
      if (
          len(title) > 20
          and ("ilan" in href.lower() or "duyuru" in href.lower() or "memur" in title.lower() or "alım" in title.lower())
      ):
        ad_id = href + title

        if ad_id not in seen_ads:
          # Yeni ilan tespit edildi!
          full_link = href if href.startswith("http") else f"https://kamuilan.sbb.gov.tr/{href}"
          msg = (
              f"🚨 <b>YENİ KAMU PERSONELİ ALIMI!</b>\n\n"
              f"📌 <b>{title}</b>\n\n"
              f"🔗 <a href='{full_link}'>İlan Detayına Git</a>"
          )

          print(f"Yeni ilan bulundu: {title}")
          send_telegram_message(msg)
          seen_ads.append(ad_id)
          new_ads_found = True

    save_seen_ads(seen_ads)
    if not new_ads_found:
      print("Yeni ilan bulunamadı, sistem güncel.")

  except Exception as e:
    print(f"Tarama sırasında hata oluştu: {e}")


if __name__ == "__main__":
  check_announcements()
