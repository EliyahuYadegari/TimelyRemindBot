import time
from datetime import datetime
from database import conn, cursor
from bot import bot

def send_reminders():
    """Send reminders at the scheduled time."""
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        print(f"Checking for reminders at {now}...")  # בדיקה

        cursor.execute("SELECT user_id, category, description FROM deadlines WHERE date || ' ' || time = ?", (now,))
        deadlines = cursor.fetchall()

        print("Reminders found:", deadlines)  # בדיקה

        for user_id, category, description in deadlines:
            print(f"Sending reminder to {user_id}: {description}")  # בדיקה
            bot.send_message(user_id, f"Reminder! You have a deadline now in {category}: {description}")

        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    send_reminders()
    bot.send_message(219067842, "Test message from the bot")

