import random
import re
import uuid

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

from job import Job

CREATE, START, PAUSE, EDIT, DELETE, DOWNLOAD = map(chr, range(6))
SELECTING_ACTION, STOPPING = map(chr, range(7, 9))
SET_NAME, SET_TIME,  SET_QUESTION = map(chr, range(9, 12))
SET_DAYS, SET_WEEK_PERIOD, SET_MONTH_PERIOD = map(chr, range(12, 15))
CHOOSE_NAME = chr(16)

TIME_STR_PATTERN = re.compile("(\s*[0-2]?\d\:[0-5]\d){1,10}")
TIME_PATTERN = re.compile("[0-2]?\d\:[0-5]\d")

# Top level conversation callbacks
def start(update: Update, context: CallbackContext) -> str:
    """Select an action"""
    buttons = [
        [
            InlineKeyboardButton("Create job", 
                                  callback_data=str(CREATE)),
            InlineKeyboardButton("Delete job",
                                  callback_data=str(DELETE)),
        ],
        [
            InlineKeyboardButton("Start job",
                                  callback_data=str(START)),
            InlineKeyboardButton("Pause job",
                                  callback_data=str(PAUSE)),
        ],
        [
            InlineKeyboardButton("Edit job",
                                  callback_data=str(EDIT)),
            InlineKeyboardButton("Download data",
                                  callback_data=str(DOWNLOAD)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    update.message.reply_text(text="Select an action", reply_markup=keyboard)

    return SELECTING_ACTION

def set_question(update: Update, context: CallbackContext) -> str:
    time_str = update.message.text
    print(time_str)
    update.message.reply_text(f"Setting question to {time_str}")
    update.message.reply_text("done")
    return STOPPING

def pause_shedule(update: Update, context: CallbackContext) -> str:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Pausing shedule. Choose shedule")
    return CHOOSE_NAME

def choose_name(update: Update, context: CallbackContext) -> str:
    name_str = update.message.text
    print(name_str)
    update.message.reply_text(f"Choosing name {name_str}")
    update.message.reply_text("Done")
    return STOPPING

def download(update: Update, context: CallbackContext) -> str:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Download results. Choose shedule")
    return CHOOSE_NAME



class CollectorBot:
    def __init__(self, token: str) -> None:
        self.updater = Updater(token = token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.jobs: Dict[int, Job] = dict()

    def create_job(self, update: Update, context: CallbackContext) -> str:
        job_id = uuid.uuid4().int
        context.user_data["job_id"] = job_id
        self.jobs[job_id] = Job(job_id)
        query = update.callback_query
        query.answer()
        query.edit_message_text(text="Type name to job")
        return SET_NAME

    def set_job_name(self, update: Update, context: CallbackContext) -> str:
        job_id = context.user_data["job_id"]
        chat_id = update.message.chat_id
        job_name = update.message.text
        cur_job = self.jobs[job_id]
        cur_job.set_chat_id(chat_id)
        cur_job.set_name(job_name)
        update.message.reply_text(f"Setting name to {job_name}")
        update.message.reply_text("Set time to job")
        return SET_TIME

    def set_job_time(self, update: Update, context: CallbackContext) -> str:
        job_id = context.user_data["job_id"]
        times_str = update.message.text
        if TIME_STR_PATTERN.fullmatch(times_str) is None:
            update.message.reply_text("Wrong format of time. Retype time")
            return SET_TIME    
        times = TIME_PATTERN.findall(times_str)
        self.jobs[job_id].set_times(times)
        update.message.reply_text(f"Setting time to {times}")
        update.message.reply_text("Select days to job")
        return SET_QUESTION

    def start(self) -> None:

        create_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.create_job, 
                                               pattern = f'^{CREATE}$')],
            states={
                SET_NAME: [MessageHandler(Filters.text, self.set_job_name)],
                SET_TIME: [MessageHandler(Filters.text, self.set_job_time)],
                SET_DAYS: [MessageHandler(Filters.text, self.set_job_time)],
                SET_WEEK_PERIOD: [MessageHandler(Filters.text, self.set_job_time)],
                SET_MONTH_PERIOD: [MessageHandler(Filters.text, self.set_job_time)],
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