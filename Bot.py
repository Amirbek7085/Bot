import telebot
import json
import os 

# **TOKEN va ADMIN ID**
TOKEN = "8184132416:AAHAgZ5FCuDoiD3dTA8caaeZtIavFI6w4ko"  # <<< BU YERGA TOKENINGIZNI QO‘YING
ADMIN_ID = 1330483263  # <<< BU YERGA ADMIN ID-INGIZNI YOZING 

bot = telebot.TeleBot(TOKEN, parse_mode="HTML") 

# **Fayllar**
MOVIES_FILE = "movies.json"
VIEWS_FILE = "views.json"
CHANNELS_FILE = "channels.json" 

# **Ma'lumotlarni yuklash**
def load_data(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default 

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f) 

movies = load_data(MOVIES_FILE, {})
views = load_data(VIEWS_FILE, {})
channels = load_data(CHANNELS_FILE, []) 

# **START - Obunani tekshirish**
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    if not check_subscription(user_id):
        send_subscription_message(user_id)
        return
    bot.send_message(user_id, "✅ <b>Salom! Kinolar botiga xush kelibsiz.</b>\n🔑 <i>Iltimos, kodni kiriting.</i>") 

def send_subscription_message(user_id):
    text = "🚀 Botdan foydalanish uchun quyidagi kanallarga a'zo bo‘ling:\n\n"
    for ch in channels:
        text += f"🔹 <a href='https://t.me/{ch}'>{ch}</a>\n"
    text += "\n✅ A’zo bo‘lgandan keyin pastdagi tugma orqali tekshiring." 

    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("🔄 Tekshirish", callback_data="check_subscription")) 

    bot.send_message(user_id, text, reply_markup=keyboard, disable_web_page_preview=True) 

def check_subscription(user_id):
    for ch in channels:
        try:
            status = bot.get_chat_member(f"@{ch}", user_id).status
            if status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True 

@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def verify_subscription(call):
    if check_subscription(call.message.chat.id):
        bot.send_message(call.message.chat.id, "✅ Siz barcha kanallarga a'zo bo‘lgansiz! Endi botdan foydalanishingiz mumkin.")
    else:
        send_subscription_message(call.message.chat.id) 

# **KANALLARNI BOSHQARISH (/channels)**
@bot.message_handler(commands=['channels'])
def manage_channels(message):
    if message.chat.id == ADMIN_ID:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("➕ Kanal qo‘shish", "❌ Kanal o‘chirish", "📋 Kanallar ro‘yxati")
        bot.send_message(message.chat.id, "📢 <b>Homiy kanallarni boshqarish</b>", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "❌ Bu buyruq faqat adminlar uchun.") 

@bot.message_handler(func=lambda message: message.text in ["➕ Kanal qo‘shish", "❌ Kanal o‘chirish", "📋 Kanallar ro‘yxati"])
def channel_operations(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Bu buyruq faqat adminlar uchun.")
        return 

    if message.text == "➕ Kanal qo‘shish":
        bot.send_message(message.chat.id, "🆕 Qo‘shmoqchi bo‘lgan kanal usernameni kiriting (@ belgisisiz):")
        bot.register_next_step_handler(message, add_channel)
    elif message.text == "❌ Kanal o‘chirish":
        bot.send_message(message.chat.id, "🚫 O‘chirmoqchi bo‘lgan kanal usernameni kiriting:")
        bot.register_next_step_handler(message, remove_channel)
    elif message.text == "📋 Kanallar ro‘yxati":
        if channels:
            text = "📌 <b>Homiy kanallar:</b>\n\n" + "\n".join([f"🔹 {ch}" for ch in channels])
        else:
            text = "❌ Hech qanday homiy kanal qo‘shilmagan."
        bot.send_message(message.chat.id, text) 

def add_channel(message):
    ch = message.text.strip()
    if ch in channels:
        bot.send_message(message.chat.id, "❌ Bu kanal allaqachon ro‘yxatda bor.")
        return
    channels.append(ch)
    save_data(CHANNELS_FILE, channels)
    bot.send_message(message.chat.id, f"✅ @{ch} kanali homiylar ro‘yxatiga qo‘shildi.") 

def remove_channel(message):
    ch = message.text.strip()
    if ch not in channels:
        bot.send_message(message.chat.id, "❌ Bunday kanal ro‘yxatda yo‘q.")
        return
    channels.remove(ch)
    save_data(CHANNELS_FILE, channels)
    bot.send_message(message.chat.id, f"✅ @{ch} kanali homiylar ro‘yxatidan o‘chirildi.") 

# **BOTNI ISHLATISH**
print("🤖 Bot ishlamoqda...")
bot.polling(none_stop=True)
