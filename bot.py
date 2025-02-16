import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, ConversationHandler, filters
from datetime import datetime
from config import TOKEN

def create_db(user_id):
    db_name = f'tasks_{user_id}.db'
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''  
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            name TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_task_to_db(user_id, date, time, name):
    db_name = f'tasks_{user_id}.db' 
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''  
        INSERT INTO tasks (date, time, name)
        VALUES (?, ?, ?)
    ''', (date, time, name))
    conn.commit()
    conn.close()

def get_all_tasks(user_id):
    db_name = f'tasks_{user_id}.db'
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('SELECT date, time, name FROM tasks ORDER BY date, time')
    tasks = c.fetchall()
    conn.close()
    return tasks

def is_valid_date(date_string):
    try:
        datetime.strptime(date_string, '%d/%m/%Y')
        return True
    except ValueError:
        return False

def is_valid_time(time_string):
    try:
        datetime.strptime(time_string, '%H:%M')
        return True
    except ValueError:
        return False

def delete_task(user_id, date, time, name):
    db_name = f'tasks_{user_id}.db'
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''DELETE FROM tasks WHERE date = ? AND time = ? AND name = ?''', (date, time, name))
    conn.commit()
    conn.close()

TAREKH, SHA_AH, NAME, SHOW, DELETE = range(5)

async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    print(user_id)
    create_db(user_id)

    keyboard = [['add', 'show', 'delete']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text('ברוך הבא! מה תרצה לעשות?', reply_markup=reply_markup)

# כשבוחרים להוסיף מטלה
async def task_date(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('אנא הזן את התאריך של המטלה (לדוגמה: 12/02/2025):')
    return TAREKH

# קביעת השעה של המטלה
async def task_time(update: Update, context: CallbackContext) -> int:
    date = update.message.text
    if not is_valid_date(date):
        await update.message.reply_text('התאריך שהוזן לא תקין. יש להכניס תאריך בפורמט DD/MM/YYYY (לדוגמה: 12/02/2025).')
        return TAREKH
    
    context.user_data['date'] = date
    await update.message.reply_text('אנא הזן את השעה של המטלה (לדוגמה: 14:00):')
    return SHA_AH

async def task_name(update: Update, context: CallbackContext) -> int:
    time = update.message.text
    if not is_valid_time(time):
        await update.message.reply_text('השעה שהוזנה לא תקינה. יש להכניס שעה בפורמט HH:MM (לדוגמה: 14:00).')
        return SHA_AH

    context.user_data['time'] = time
    await update.message.reply_text('אנא הזן את שם המטלה:')
    return NAME

async def save_task(update: Update, context: CallbackContext) -> int:
    context.user_data['name'] = update.message.text
    user_id = update.message.from_user.id
    save_task_to_db(user_id, context.user_data['date'], context.user_data['time'], context.user_data['name'])
    
    task_info = f"מטלה חדשה: תאריך: {context.user_data['date']}, שעה: {context.user_data['time']}, שם: {context.user_data['name']}"
    await update.message.reply_text(f"המטלה הוספה בהצלחה:\n{task_info}")
    
    keyboard = [['add', 'show', 'delete']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text('מה תרצה לעשות עכשיו?', reply_markup=reply_markup)

    return ConversationHandler.END

async def show_tasks(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    tasks = get_all_tasks(user_id)
    
    if tasks:
        task_list = '\n'.join([f"תאריך: {task[0]}, שעה: {task[1]}, שם: {task[2]}" for task in tasks])
        await update.message.reply_text(f"המטלות שלך:\n{task_list}")
    else:
        await update.message.reply_text("אין מטלות רשומות.")
    
    keyboard = [['הוסף מטלה', 'חזור לתפריט הראשי']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text('מה תרצה לעשות עכשיו?', reply_markup=reply_markup)
    
    return SHOW

async def delete_task_prompt(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    tasks = get_all_tasks(user_id)
    
    if tasks:
        task_list = '\n'.join([f"{idx + 1}. תאריך: {task[0]}, שעה: {task[1]}, שם: {task[2]}" for idx, task in enumerate(tasks)])
        await update.message.reply_text(f"המטלות שלך למחיקה:\n{task_list}\nאנא בחר את מספרי המטלות שברצונך למחוק, מופרדים בפסיקים (למשל: 1, 2, 4):")
        return DELETE
    else:
        await update.message.reply_text("אין מטלות למחוק. חזרה לתפריט הראשי.")
        return await return_to_main_menu(update, context)

async def handle_task_deletion(update: Update, context: CallbackContext) -> int:
    try:
        task_numbers = update.message.text.split(",")
        task_numbers = [int(num.strip()) - 1 for num in task_numbers]

        user_id = update.message.from_user.id
        tasks = get_all_tasks(user_id)
        
        invalid_tasks = [num + 1 for num in task_numbers if num < 0 or num >= len(tasks)]
        if invalid_tasks:
            await update.message.reply_text(f"המספרים הבאים לא תקינים: {', '.join(map(str, invalid_tasks))}, אנא הכנס מספר תקין מהרשימה.")
            return DELETE

        for task_number in task_numbers:
            task = tasks[task_number]
            delete_task(user_id, task[0], task[1], task[2])
            
        await update.message.reply_text(f"המטלות הבאות נמחקו: \n" +
                                       '\n'.join([f"תאריך: {tasks[num][0]}, שעה: {tasks[num][1]}, שם: {tasks[num][2]}" for num in task_numbers]))
        
    except ValueError:
        await update.message.reply_text("יש להכניס מספרים תקינים של מטלות מופרדים בפסיקים.")
    
    return await return_to_main_menu(update, context)

async def return_to_main_menu(update: Update, context: CallbackContext) -> None:
    keyboard = [['add', 'show', 'delete']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text('מה תרצה לעשות?', reply_markup=reply_markup)
    return ConversationHandler.END

def main():
    application = Application.builder().token(TOKEN).build()

    conversation_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^add$'), task_date), 
                      MessageHandler(filters.Regex('^show$'), show_tasks),
                      MessageHandler(filters.Regex('^delete$'), delete_task_prompt)],
        states={ 
            TAREKH: [MessageHandler(filters.TEXT & ~filters.COMMAND, task_time)],
            SHA_AH: [MessageHandler(filters.TEXT & ~filters.COMMAND, task_name)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_task)],
            SHOW: [MessageHandler(filters.Regex('^חזור לתפריט הראשי$'), return_to_main_menu),
                   MessageHandler(filters.Regex('^הוסף מטלה$'), task_date)],
            DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_task_deletion)]
        },
        fallbacks=[]
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conversation_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
