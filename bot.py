from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, ConversationHandler, filters
from config import TOKEN
from handlers import start, task_date, task_time, task_name, save_task, show_tasks, delete_task_prompt, handle_task_deletion, return_to_main_menu

TAREKH, SHA_AH, NAME, SHOW, DELETE = range(5)

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
