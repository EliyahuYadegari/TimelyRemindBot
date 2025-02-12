import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
from config import TOKEN, VALID_CATEGORIES
from database import add_deadline, get_deadlines

bot = telebot.TeleBot(TOKEN)
user_sessions = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Welcome message for new users."""
    print(f"Your Chat ID is: {message.chat.id}")
    bot.reply_to(message, "Welcome! Use /add to create a reminder or /show to view reminders.")
    print(f"Your Chat ID is: {message.chat.id}")

@bot.message_handler(commands=['add'])
def add_reminder(message):
    """Start the interactive reminder creation."""
    user_sessions[message.chat.id] = {}
    bot.send_message(message.chat.id, "Enter the date and time (YYYY-MM-DD HH:MM):")

@bot.message_handler(func=lambda message: message.chat.id in user_sessions and 'date_time' not in user_sessions[message.chat.id])
def receive_date_time(message):
    """Receive date and time from user."""
    try:
        datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        user_sessions[message.chat.id]['date_time'] = message.text

        # Show category options
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for category in VALID_CATEGORIES:
            markup.add(KeyboardButton(category))

        bot.send_message(message.chat.id, "Select a category:", reply_markup=markup)
    except ValueError:
        bot.send_message(message.chat.id, "Invalid format! Use YYYY-MM-DD HH:MM.")

@bot.message_handler(func=lambda message: message.chat.id in user_sessions and 'category' not in user_sessions[message.chat.id])
def receive_category(message):
    """Receive category from user."""
    if message.text not in VALID_CATEGORIES:
        bot.send_message(message.chat.id, f"Invalid category! Choose from: {', '.join(VALID_CATEGORIES)}")
        return

    user_sessions[message.chat.id]['category'] = message.text
    bot.send_message(message.chat.id, "Enter a description for your reminder:")

@bot.message_handler(func=lambda message: message.chat.id in user_sessions and 'description' not in user_sessions[message.chat.id])
def receive_description(message):
    """Receive description from user and save the reminder."""
    user_id = message.chat.id
    user_sessions[user_id]['description'] = message.text

    date, time = user_sessions[user_id]['date_time'].split()
    category = user_sessions[user_id]['category']
    description = user_sessions[user_id]['description']

    print(f"Saving reminder: {date} {time} | {category} | {description}")  # בדיקה

    add_deadline(user_id, date, time, description, category)
    del user_sessions[user_id]

    bot.send_message(user_id, f"Reminder saved: {description} on {date} at {time} under {category}.")


@bot.message_handler(commands=['show'])
def show_menu(message):
    """Show options for displaying reminders."""
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(KeyboardButton("All"))
    for category in VALID_CATEGORIES:
        markup.add(KeyboardButton(category))

    bot.send_message(message.chat.id, "Choose a category to view:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["All"] + VALID_CATEGORIES)
def show_deadlines(message):
    """Display reminders based on selected category."""
    user_id = message.chat.id
    category = None if message.text == "All" else message.text

    deadlines = get_deadlines(user_id, category)

    if deadlines:
        response = "\n".join([f"{date} {time} - {desc}" for date, time, desc in deadlines])
    else:
        response = "No deadlines found in this category." if category else "No deadlines found."

    bot.send_message(message.chat.id, response)

bot.polling()
