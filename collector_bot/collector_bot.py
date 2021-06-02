from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    Filters,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
)

CREATE, START, PAUSE, EDIT, DELETE, DOWNLOAD = map(chr, range(6))
SELECTING_ACTION, STOPPING = map(chr, range(7, 9))
SET_NAME, SET_TIME, SET_QUESTION = map(chr, range(9, 12))
CHOOSE_NAME = chr(12)
START_OVER = chr(13)

# Top level conversation callbacks
def start(update: Update, context: CallbackContext) -> str:
    """Select an action"""
    text = (
        "Choose action"
    )

    buttons = [
        [
            InlineKeyboardButton("Create shedule", 
                                  callback_data=str(CREATE)),
            InlineKeyboardButton("Delete shedule",
                                  callback_data=str(DELETE)),
        ],
        [
            InlineKeyboardButton("Start shedule",
                                  callback_data=str(START)),
            InlineKeyboardButton("Pause shedule",
                                  callback_data=str(PAUSE)),
        ],
        [
            InlineKeyboardButton("Edit shedule",
                                  callback_data=str(EDIT)),
            InlineKeyboardButton("Download data",
                                  callback_data=str(DOWNLOAD)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    # If we're starting over we don't need to send a new message
    if context.user_data.get(START_OVER):
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        update.message.reply_text(
            "Hi, i will help you to shedule questions and store answers"
        )
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_ACTION


def create_shedule(update: Update, _: CallbackContext) -> str:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Creating shedule. Type name")
    return SET_NAME

def set_name(update: Update, _: CallbackContext) -> str:
    name_str = update.message.text
    print(name_str)
    update.message.reply_text(f"Setting name to {name_str}")
    update.message.reply_text("Set time")
    return SET_TIME

def set_time(update: Update, _: CallbackContext) -> str:
    time_str = update.message.text
    print(time_str)
    update.message.reply_text(f"Setting time to {time_str}")
    update.message.reply_text("Select question")
    return SET_QUESTION

def set_question(update: Update, _: CallbackContext) -> str:
    time_str = update.message.text
    print(time_str)
    update.message.reply_text(f"Setting question to {time_str}")
    update.message.reply_text("done")
    return STOPPING

def pause_shedule(update: Update, _: CallbackContext) -> str:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Pausing shedule. Choose shedule")
    return CHOOSE_NAME

def choose_name(update: Update, _: CallbackContext) -> str:
    name_str = update.message.text
    print(name_str)
    update.message.reply_text(f"Choosing name {name_str}")
    update.message.reply_text("Done")
    return STOPPING

def download(update: Update, _: CallbackContext) -> str:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Download results. Choose shedule")
    return CHOOSE_NAME


class CollectorBot:
    def __init__(self, token: str) -> None:
        self.updater = Updater(token = token, use_context=True)
        self.dispatcher = self.updater.dispatcher

    def start(self) -> None:

        create_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(create_shedule, 
                                               pattern = f'^{CREATE}$')],
            states={
                SET_NAME: [MessageHandler(Filters.text, set_name)],
                SET_TIME: [MessageHandler(Filters.text, set_time)],
                SET_QUESTION: [MessageHandler(Filters.text, set_question)],
            },
            fallbacks=[],
            map_to_parent = { STOPPING: STOPPING }
        )

        pause_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(pause_shedule, 
                                               pattern = f'^{PAUSE}$')],
            states={
                CHOOSE_NAME: [MessageHandler(Filters.text, choose_name)],
            },
            fallbacks=[],
            map_to_parent = { STOPPING: STOPPING }
        )

        download_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(download, 
                                               pattern = f'^{DOWNLOAD}$')],
            states={
                CHOOSE_NAME: [MessageHandler(Filters.text, choose_name)],
            },
            fallbacks=[],
            map_to_parent = { STOPPING: STOPPING }
        )

        selection_handlers = [
            create_handler,
            pause_handler,
            download_handler,
        ]

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                SELECTING_ACTION: selection_handlers,
                STOPPING: [CommandHandler('start', start)]
            },
            fallbacks=[CommandHandler('start', start)],
        )

        self.dispatcher.add_handler(conv_handler)
        self.updater.start_polling()
        self.updater.idle()