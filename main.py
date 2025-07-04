import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import os

# توکن ربات را از BotFather جایگذاری کنید
TOKEN = '7696647315:AAHkPyJEJHqaGxiN9BhMq_fxA50U_IheMKg'  # توکن رباتت رو اینجا بذار
bot = telebot.TeleBot(TOKEN)

# لینک‌های Dropbox برای جزوه‌ها و تکالیف
NOTES = {
    'biology': 'YOUR_BIOLOGY_NOTES_LINK?dl=1',  # لینک Dropbox جزوه بیولوژی
    'math': 'https://www.dropbox.com/scl/fi/9jcttq9hcjokxbpib1xbx/.pdf?rlkey=psib9funf66abflj96dlwfoms&st=0nwyjwrw&dl=1',        # لینک Dropbox جزوه ریاضی
    'literature': 'YOUR_LITERATURE_NOTES_LINK?dl=1'  # لینک Dropbox جزوه ادبیات
}

ASSIGNMENTS = {
    'biology': 'YOUR_BIOLOGY_ASSIGNMENTS_LINK?dl=1',  # لینک Dropbox تکالیف بیولوژی
    'math': 'YOUR_MATH_ASSIGNMENTS_LINK?dl=1',        # لینک Dropbox تکالیف ریاضی
    'literature': 'YOUR_LITERATURE_ASSIGNMENTS_LINK?dl=1'  # لینک Dropbox تکالیف ادبیات
}

# تابع دانلود فایل از Dropbox
def download_file(url, file_name):
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(response.content)
        return True
    return False

# تابع ساخت منوی اصلی
def main_menu():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📚 جزوه‌ها", callback_data='notes'))
    keyboard.add(InlineKeyboardButton("📝 تکالیف", callback_data='assignments'))
    keyboard.add(InlineKeyboardButton("ℹ️ درباره ربات", callback_data='about'))
    return keyboard

# تابع ساخت منوی دروس
def subjects_menu(category):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🧬 بیولوژی", callback_data=f'{category}_biology'))
    keyboard.add(InlineKeyboardButton("➕ ریاضی", callback_data=f'{category}_math'))
    keyboard.add(InlineKeyboardButton("📖 ادبیات", callback_data=f'{category}_literature'))
    return keyboard

# هندلر دستور /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🎓 به ربات ورودی دانشگاه ۱۴۰۳ خوش آمدید!\nلطفاً گزینه موردنظر را انتخاب کنید:", reply_markup=main_menu())

# هندلر دستور /notes
@bot.message_handler(commands=['notes'])
def send_notes(message):
    bot.reply_to(message, "📚 لطفاً درس موردنظر را انتخاب کنید:", reply_markup=subjects_menu('notes'))

# هندلر دستور /assignments
@bot.message_handler(commands=['assignments'])
def send_assignments(message):
    bot.reply_to(message, "📝 لطفاً درس موردنظر را انتخاب کنید:", reply_markup=subjects_menu('assignments'))

# هندلر دکمه‌های اینلاین
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'notes':
        bot.edit_message_text("📚 لطفاً درس موردنظر را انتخاب کنید:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=subjects_menu('notes'))
    elif call.data == 'assignments':
        bot.edit_message_text("📝 لطفاً درس موردنظر را انتخاب کنید:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=subjects_menu('assignments'))
    elif call.data == 'about':
        bot.edit_message_text("ℹ️ این ربات برای ورودی‌های دانشگاه (بهمن ۱۴۰۳) طراحی شده و جزوه‌ها و تکالیف دروس را ارائه می‌دهد.", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=main_menu())
    elif call.data.startswith('notes_') or call.data.startswith('assignments_'):
        subject = call.data.split('_')[1]
        is_notes = call.data.startswith('notes_')
        link = NOTES.get(subject) if is_notes else ASSIGNMENTS.get(subject)
        if not link:
            bot.edit_message_text("لینکی یافت نشد!", chat_id=call.message.chat.id, message_id=call.message.message_id)
            return

        # نام فایل برای ذخیره موقت
        file_name = f"{subject}_{'notes' if is_notes else 'assignments'}.pdf"
        
        # دانلود فایل از Dropbox
        if download_file(link, file_name):
            try:
                with open(file_name, 'rb') as file:
                    bot.send_document(chat_id=call.message.chat.id, document=file, caption=f"{'جزوه' if is_notes else 'تکلیف'} {subject}")
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            except Exception as e:
                bot.edit_message_text(f"خطا در ارسال فایل: {str(e)}", chat_id=call.message.chat.id, message_id=call.message.message_id)
            finally:
                # حذف فایل موقت
                if os.path.exists(file_name):
                    os.remove(file_name)
        else:
            bot.edit_message_text("خطا در دانلود فایل!", chat_id=call.message.chat.id, message_id=call.message.message_id)

# حذف Webhook قبل از شروع Polling
bot.delete_webhook()

# شروع ربات
bot.polling()