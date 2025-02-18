# TimelyRemindBot

### Description:
This is a Telegram bot designed to help you manage your tasks. The bot allows users to:
- Add tasks with a specific date, time, and description.
- View all your saved tasks.
- Delete tasks by choosing them from a list.

Each user gets a unique database to store their tasks.

### Features:
- **Add Tasks**: Users can add tasks with a date, time, and description.
- **View Tasks**: Users can view a list of their tasks, sorted by date and time.
- **Delete Tasks**: Users can delete tasks by selecting them from a list of their saved tasks.

### Requirements:
- Python 3.7+
- `python-telegram-bot` library
- `sqlite3` for local database storage

### Installation:

1. Clone the repository:
   ```bash
   git clone [TimelyRemindBot.git](https://github.com/EliyahuYadegari/TimelyRemindBot.git)
   ```

2. Navigate to the project folder:
   ```bash
   cd TimelyRemindBot
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `config.py` file and add your bot's token:
   ```python
   TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
   ```

### Usage:
1. Start the bot by running the `bot.py` script:
   ```bash
   python bot.py
   ```

2. Send `/start` to the bot on Telegram to begin interacting with it.

### Database:
Each user will have a unique SQLite database to store their tasks. The database file is named based on the user's `user_id`, e.g., `tasks_123456.db`.

### Functions:
- **create_db(user_id)**: Creates a database for each user.
- **save_task_to_db(user_id, date, time, name)**: Saves a task to the user's database.
- **get_all_tasks(user_id)**: Retrieves all tasks for the user.
- **delete_task(user_id, date, time, name)**: Deletes a specific task from the user's database.

### Contributing:
Feel free to fork the repository and create a pull request with your improvements or fixes!

### License:
This project is open-source and available under the [MIT License](https://opensource.org/license/mit).

---
