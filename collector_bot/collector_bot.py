from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
)


def start(update: Update, _: CallbackContext) -> str:
    keyboard = [
        [InlineKeyboardButton("Create shedule", 
                              callback_data="create_new")],
        [InlineKeyboardButton("Start new shedule",
                              callback_data="start_shedule")],
        [InlineKeyboardButton("Pause shedule",
                              callback_data="pause_shedule")],
        [InlineKeyboardButton("Edit shedule",
                              callback_data="edit_shedule")],
        [InlineKeyboardButton("Delete shedule",
                              callback_data="delete_shedule")],
        [InlineKeyboardButton("Download data",
                              callback_data="download data")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Choose action", reply_markup=reply_markup)
    return 'BEGIN'

def create_shedule(update: Update, _: CallbackContext) -> str:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Create new")
    return 'BEGIN'

def start_shedule(update: Update, _: CallbackContext) -> str:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Start shedule")
    return 'BEGIN'

def pause_shedule(update: Update, _: CallbackContext) -> str:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Pause shedule")
    return 'BEGIN'

def edit_shedule(update: Update, _: CallbackContext) -> str:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Edit shedule")
    return 'BEGIN'

def delete_shedule(update: Update, _: CallbackContext) -> str:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Delete shedule")
    return 'BEGIN'

def download_data(update: Update, _: CallbackContext) -> str:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Download data")
    return 'BEGIN'

class CollectorBot:
    def __init__(self, token: str) -> None:
        self.updater = Updater(token = token, use_context=True)
        self.dispatcher = self.updater.dispatcher

    def start(self) -> None:
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                'BEGIN': [
                    CallbackQueryHandler(create_shedule, pattern='create_*'),
                    CallbackQueryHandler(start_shedule, pattern='start_*'),
                    CallbackQueryHandler(pause_shedule, pattern='pause_*'),
                    CallbackQueryHandler(edit_shedule, pattern='edit_*'),
                    CallbackQueryHandler(delete_shedule, pattern='delete_*'),
                    CallbackQueryHandler(download_data, pattern='download_*'),
                ],
            },
            fallbacks=[CommandHandler('start', start)],
        )

        self.dispatcher.add_handler(conv_handler)
        self.updater.start_polling()
        self.updater.idle()