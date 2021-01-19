from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, ReplyKeyboardMarkup, KeyboardButton, Message, Bot, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler, CallbackContext
from decimal import Decimal
from scraper import scraper
import time, datetime, pytz
from models import Session, User
import re 

# modifications
# introduce a new row with null values when user types /start
    # if user already exists, dont do anything 
# when entering any new details, modify existing row 
# if wrong credientials, dont commit changes to row 


session = Session()

# cancel 
def cancel(update):
    update.message.reply_text("Your session has been terminated. Please type /start to begin a new one.", reply_markup=ReplyKeyboardRemove())
    
# helper function 1
def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

# helper function 2
def showInfo(room_unit_no,evs_username,lower_credit_limit,update):
    text2 = "The following is your current information: \n\nRoom Unit Number: " + str(room_unit_no) + "\nEVS Username: " + str(evs_username) + "\nLower Credit Limit: $" + str(lower_credit_limit) + "\n\nYou can access our other functions here!"
    update.message.reply_text(text=text2, reply_markup=main_options_keyboard())

def main_options_keyboard():
    keyboard = [
        [InlineKeyboardButton("Update Room Information", callback_data='update_id')],
        [InlineKeyboardButton("Update Lower Credit Limit", callback_data='update_credit')],
        [InlineKeyboardButton("On/Off Notification Alert", callback_data='update_alert')],
        [InlineKeyboardButton("Check Aircon Credit Balance", callback_data='check_balance')]
    ]
    return InlineKeyboardMarkup(keyboard)

def notification_keyboard():
    keyboard = [
        [InlineKeyboardButton("On Alert", callback_data='on_notif'), InlineKeyboardButton("Off Alert", callback_data='off_notif')]
    ]
    return InlineKeyboardMarkup(keyboard)

# /start
UPDATE_ID, UPDATE_NOTIF, UPDATE_END = range(3)

def start(update, context):
    print("UPDATE:", update)
    print("CONTEXT:", context)

    global chat_id
    chat_id = update.message.chat.id
    global username
    username = update.message.from_user.username

    user = session.query(User).get(username)

    if user != None:  # if user has previously used the bot 

        global room_unit_no
        room_unit_no = user.room_unit_no  

        global evs_username
        evs_username = user.evs_username

        global lower_credit_limit
        lower_credit_limit = user.lower_credit_limit

        showInfo(room_unit_no,evs_username,lower_credit_limit,update)

        return ConversationHandler.END

    context.bot.send_message(
        chat_id=chat_id,
        text="Hi @" + username + "! Let's get you started! \nMay I know your room unit number? (e.g. #01-01 or #01-01A), or type /cancel to end your session."
    )
    return UPDATE_ID

# New User

def prompt_id(update, context):
    chat_id = update.message.chat.id
    user_input = update.message.text.replace(" ", "")
    
    def error():
        context.bot.send_message(
        chat_id=chat_id,
        text='Please key in using this format #xx-xx or #xx-xxx, or type /cancel to end your session.'
        )

    if (user_input == "/cancel"):
        cancel(update)
        return ConversationHandler.END

    pattern = r'#\d\d-\d\d\w?'

    if not re.match(pattern,user_input):
        error()
        return UPDATE_ID

    global room_unit_no
    room_unit_no = user_input
    text = "Your room " + user_input + " has been registered. \nPlease enter your EVS Username. (e.g. 12345678)"

    context.bot.send_message(
        text=text,
        chat_id=chat_id
    )
    return UPDATE_NOTIF

def prompt_notif(update, context):
    chat_id = update.message.chat.id
    user_input = update.message.text.replace(" ", "")
    
    if (user_input == "/cancel"):
        cancel(update)
        return ConversationHandler.END
    
    pattern = r'\d{8}'
    
    if not re.match(pattern,user_input):
        context.bot.send_message(
        chat_id=chat_id,
        text='Please enter a valid username or type /cancel to end your session.'
        )
        return UPDATE_NOTIF

    global evs_username
    evs_username = user_input

    # check if login details are correct with scraper 
    if scraper(evs_username,room_unit_no) == None:
        context.bot.send_message(
        chat_id=chat_id,
        text='Your log in details are wrong, please enter your room number again or type /cancel to end your session.'
        )
        return UPDATE_ID

    text = "You have been logged into " + user_input + ". \nPlease enter your preferred lower credit limit. (e.g. 2.50) or type /cancel to end your session."

    context.bot.send_message(
        text=text,
        chat_id=chat_id
    )
    return UPDATE_END

def prompt_end_buttons(update, context):
    chat_id = update.message.chat.id
    user_input = update.message.text.replace(" ", "")

    if (user_input == "/cancel"):
        cancel(update)
        return ConversationHandler.END

    if not ((user_input.isdigit()) or isfloat(user_input)):
        context.bot.send_message(
            chat_id=chat_id,
            text='Please enter a valid amount or type /cancel to end your session.'
        )
        return UPDATE_END

    global lower_credit_limit
    lower_credit_limit = user_input

    # add all of users details into database
    user = User(username = username,evs_username = evs_username, room_unit_no = room_unit_no, lower_credit_limit = lower_credit_limit)
 
    session.add(user)
    session.commit()

    text = "Your lower credit limit has been set to $" + str(Decimal(user_input)) + ". \nInformation has been updated."

    context.bot.send_message(
        chat_id=chat_id,
        text=text
    )

    showInfo(room_unit_no,evs_username,lower_credit_limit,update)
    
    return ConversationHandler.END

# Update Room Information
def prompt_unit(update, context):
    query = update.callback_query

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text = 'May I know your room unit number? (e.g. #01-01 or #01-01A) or type /cancel to end your session.'
    )
    return UPDATE_ID

def prompt_notif_end(update, context):
    chat_id = update.message.chat.id
    user_input = update.message.text.replace(" ", "")
    
    if (user_input == "/cancel"):
        cancel(update)
        return ConversationHandler.END

    pattern = r'\d{8}'
    
    if not re.match(pattern,user_input):
        context.bot.send_message(
        chat_id=chat_id,
        text='Please enter a valid username or type /cancel to end your session.'
        )
        return UPDATE_NOTIF
    
    global evs_username
    evs_username = user_input

    # check if credentials are correct 
    if scraper(evs_username,room_unit_no) == None:
        context.bot.send_message(
        chat_id=chat_id,
        text='Your log in details are wrong, please enter your room unit number again. (e.g. #01-01 or #01-01A) or type /cancel to end your session.'
        )
        return UPDATE_ID

    user = session.query(User).get(username)

    # modifying existing values in the database to new ones 
    user.evs_username = evs_username
    user.room_unit_no = room_unit_no

    session.commit()

    text = "You have been logged into " + user_input + ". \nInformation has been updated."

    context.bot.send_message(
        text=text,
        chat_id=chat_id
    )

    showInfo(room_unit_no,evs_username,lower_credit_limit,update)

    return ConversationHandler.END

# Update Lower Credit Limit
def prompt_notif_update(update, context):
    query = update.callback_query

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text = 'What would you like to change your lower credit limit to? (e.g. 2.50) or type /cancel to end your session.'
    )
    return UPDATE_END

def prompt_end(update, context):
    chat_id = update.message.chat.id
    user_input = update.message.text.replace(" ", "")

    if (user_input == "/cancel"):
        cancel(update)
        return ConversationHandler.END

    if not ((user_input.isdigit()) or isfloat(user_input)):
        context.bot.send_message(
            chat_id=chat_id,
            text='Please enter a valid amount or type /cancel to end your session.'
        )
        return UPDATE_END

    global lower_credit_limit
    lower_credit_limit = user_input

    # update database with new lower limit
    user = session.query(User).get(username)

    user.lower_credit_limit = lower_credit_limit
    session.commit()

    text = "Your lower credit limit has been set to $" + str(Decimal(user_input)) + ". \nInformation has been updated."

    context.bot.send_message(
        chat_id=chat_id,
        text=text
    )

    showInfo(room_unit_no,evs_username,lower_credit_limit,update)
    
    return ConversationHandler.END

# Check Aircon Credit Balance
def check_balance(update, context):
    query = update.callback_query

    # extract information from database, passing into scraper to return output 
    user = session.query(User).get(username)

    evs_username = user.evs_username
    room_unit_no = user.room_unit_no

    balance = scraper(evs_username,room_unit_no)

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text= 'Your credit balance is : $' + str(balance) + '\nPlease visit https://nus-utown.evs.com.sg/ to top-up your credits.'
    )

    text2 = "The following is your current information: \n\nRoom Unit Number: " + str(room_unit_no) + "\nEVS Username: " + str(evs_username) + "\nLower Credit Limit: $" + str(lower_credit_limit) + "\n\nYou can access our other functions here!"
    context.bot.send_message(
        chat_id=query.message.chat_id,
        text=text2,
        reply_markup=main_options_keyboard())

    return ConversationHandler.END

# Send Notification
def remove_job(name, context):
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return 
    for job in current_jobs:
        job.schedule_removal()

def prompt_on_off(update, context):
    query = update.callback_query
    text = "Please select the options below to on/off notifications"
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=text,
        reply_markup=notification_keyboard()
    )

def on_notif(update, context):
    query = update.callback_query
    chat_id=query.message.chat_id

    remove_job(str(chat_id), context) #remove any existing jobs
    time_zone = pytz.timezone("Asia/Singapore")
    reset_time = datetime.time(hour=20, minute=0, second=0, tzinfo=time_zone)
    #context.job_queue.run_daily(send_notification, reset_time, days = tuple(range(7)), context=update, name=str(chat_id))

    # to play around with
    context.job_queue.run_repeating(send_notification, interval = 15, first = 0, context=update, name=str(chat_id))

    text = "We will inform you when your aircon credit balance is below your lower credit limit."
    context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=query.message.message_id,
        text=text
    )

    showInfo(room_unit_no,evs_username,lower_credit_limit,query)

def send_notification(context):
    username = context.job.context.callback_query.message.chat.username

    user = session.query(User).get(username)
    evs_username = user.evs_username
    room_unit_no = user.room_unit_no
    lower_credit_limit = user.lower_credit_limit

    balance = scraper(evs_username,room_unit_no)

    if (lower_credit_limit > balance):
        context.job.context.effective_user.send_message(
            text="Your credit balance is currently: $" + "${:,.2f}".format(balance) + ". You can top up at https://nus-utown.evs.com.sg/."
        )

def off_notif(update, context):
    query = update.callback_query
    chat_id=query.message.chat_id
    
    remove_job(str(chat_id), context)

    text = "Notification alert has been stopped."
    context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=query.message.message_id,
        text=text
    )

    showInfo(room_unit_no,evs_username,lower_credit_limit,query)

# main()
BOT_TOKEN = "1498781046:AAEtpdoE6uorK4iCpjTj-YNvBMIA3pIimAc"
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # put your handlers here
    # /start function
    dp.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                UPDATE_ID: [MessageHandler(Filters.text, prompt_id)],
                UPDATE_NOTIF: [MessageHandler(Filters.text, prompt_notif)],
                UPDATE_END: [MessageHandler(Filters.text, prompt_end_buttons)]
            },
            fallbacks=[],
            per_user=False
        )
    )
    dp.add_handler(
        ConversationHandler(
            entry_points=[CallbackQueryHandler(prompt_unit, pattern='update_id')],
            states={
                UPDATE_ID: [MessageHandler(Filters.text, prompt_id)],
                UPDATE_NOTIF: [MessageHandler(Filters.text, prompt_notif_end)],
            },
            fallbacks=[],
            per_user=False
        )
    )

    dp.add_handler(
        ConversationHandler(
            entry_points=[CallbackQueryHandler(prompt_notif_update, pattern='update_credit')],
            states={
                UPDATE_END: [MessageHandler(Filters.text, prompt_end)]
            },
            fallbacks=[],
            per_user=False
        )
    )

    dp.add_handler(CallbackQueryHandler(prompt_on_off, pattern='update_alert'))
    dp.add_handler(CallbackQueryHandler(on_notif, pattern='on_notif'))
    dp.add_handler(CallbackQueryHandler(off_notif, pattern='off_notif'))
    dp.add_handler(CallbackQueryHandler(check_balance, pattern='check_balance'))

    # dp.add_handler(CommandHandler('notify', daily_job))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

