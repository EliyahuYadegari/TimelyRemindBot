from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
from telegram.ext import CallbackContext
from database import create_db, save_task_to_db, get_all_tasks, delete_task
from validators import is_valid_date, is_valid_time

TAREKH, SHA_AH, NAME, SHOW, DELETE = range(5)

async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    # print(user_id)
    create_db(user_id)

    keyboard = [['add', 'show', 'delete']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text('ברוך הבא! מה תרצה לעשות?', reply_markup=reply_markup)

async def task_date(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('אנא הזן את התאריך של המטלה (לדוגמה: 12/02/2025):')
    return TAREKH

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
