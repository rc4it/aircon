from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, ReplyKeyboardMarkup, KeyboardButton, Message, Bot, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from decimal import Decimal
from scraper import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
from scraper import scraper

# creating database

sqlID = ''
sqlPASSWORD = ''
URI = 'mysql://' + sqlID + ':' + sqlPASSWORD + '@localhost/aircon'
engine = create_engine(URI, echo = True)
Base = declarative_base()

# table structure
class User(Base):  
    __tablename__ = 'users'
    
    username = Column(String(100),primary_key=True)
    evs_username = Column(String(10))
    room_unit_no = Column(String(10))
    lower_credit_limit = Column(Integer())

Base.metadata.create_all(engine)

# starting session
Session = sessionmaker(bind = engine)
session = Session()

def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def main_options_keyboard():
    keyboard = [
        [InlineKeyboardButton("Update Room Information", callback_data='update_id')],
        [InlineKeyboardButton("Update Lower Credit Limit", callback_data='update_credit')],
        [InlineKeyboardButton("Check Aircon Credit Balance", callback_data='check_balance')]
    ]
    return InlineKeyboardMarkup(keyboard)

# /start
def start(update, context):
    print("UPDATE:", update)
    print("CONTEXT:", context)

    chat_id = update.message.chat.id
    global username
    username = update.message.from_user.username

    # search table for specific user according to tele handle 
    # creates a 'user' object, which has attributes which correspond to the rows of the table 
    user = session.query(User).get(username)
    
    if user != None:  # if user has already registered 

        global room_unit_no
        room_unit_no = user.room_unit_no  

        global evs_username
        evs_username = user.evs_username

        global lower_credit_limit
        lower_credit_limit = user.lower_credit_limit

        text2 = "The following is your current information: \n\nRoom Unit Number: " + str(room_unit_no) + "\nEVS Username: " + str(evs_username) + "\nLower Credit Limit: $" + str(lower_credit_limit) + "\n\nYou can access our other functions here!"
        update.message.reply_text(text=text2, reply_markup=main_options_keyboard())

        return ConversationHandler.END

    context.bot.send_message(
        chat_id=chat_id,
        text="Hi @" + username + "! Let's get you started! \nMay I know your room unit number? (e.g. #01-01 or #01-01A)"
    )
    return UPDATE_ID

# /cancel
def cancel(update,context):
	
    update.message.reply_text("Your session has been terminated. Please type /start to begin a new one.", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

# New User
UPDATE_ID, UPDATE_NOTIF, UPDATE_END = range(3)
def prompt_id(update, context):
    chat_id = update.message.chat.id
    user_input = update.message.text.replace(" ", "")

    

    if (len(user_input) != 7 and len(user_input) != 6) or (user_input[0] != '#') or (user_input[3] != '-'):
        context.bot.send_message(
        chat_id=chat_id,
        text='Please key in using this format #xx-xx or #xx-xxx.'
        )

        return UPDATE_ID
    
    if (len(user_input) == 7) and not (user_input[6].isalpha()):
         context.bot.send_message(
         chat_id=chat_id,
         text='Please key in using this format #xx-xx or #xx-xxx.'
         )       
         return UPDATE_ID
    
    i = 1
    while i < 6:
        if i == 3:
            i += 1
            continue
        if (not user_input[i].isdigit()):
            context.bot.send_message(
            chat_id=chat_id,
            text='Please key in using this format #xx-xx or #xx-xxx.'
            )
            return UPDATE_ID
        i += 1

    global room_unit_no
    room_unit_no = user_input
    text = "Your room " + user_input + " has been registered. \nPlease enter your EVS Username. (e.g. 12345678)."

    context.bot.send_message(
        text=text,
        chat_id=chat_id
    )
    return UPDATE_NOTIF

def prompt_notif(update, context):
    chat_id = update.message.chat.id
    user_input = update.message.text.replace(" ", "")
    
    

    if not (user_input.isdigit() and len(user_input) == 8):
        context.bot.send_message(
        chat_id=chat_id,
        text='Please enter a valid username.'
        )
        return UPDATE_NOTIF

    global evs_username
    evs_username = user_input

    # check if login details are correct with scraper 
    if scraper(evs_username,room_unit_no) == None:
        context.bot.send_message(
        chat_id=chat_id,
        text='Your log in details are wrong, please enter your room number again.'
        )
        return UPDATE_ID

    text = "You have been logged into " + user_input + ". \nPlease enter your preferred lower credit limit. (e.g. 2.50)"

    context.bot.send_message(
        text=text,
        chat_id=chat_id
    )
    return UPDATE_END

def prompt_end_buttons(update, context):
    chat_id = update.message.chat.id
    user_input = update.message.text.replace(" ", "")

    

    if not ((user_input.isdigit()) or isfloat(user_input)):
        context.bot.send_message(
            chat_id=chat_id,
            text='Please enter a valid amount.'
        )
        return UPDATE_END

    global lower_credit_limit
    lower_credit_limit = user_input

    # add all of users details into database
    user = User(username = username,evs_username = evs_username, room_unit_no = room_unit_no, lower_credit_limit = lower_credit_limit)

    # committing changes to the database 
    session.add(user)
    session.commit()

    text = "Your lower credit limit has been set to $" + str(Decimal(user_input)) + ". \nInformation has been updated."

    context.bot.send_message(
        chat_id=chat_id,
        text=text
    )

    # can input their current room information and lower credit limit
    text2 = "The following is your current information: \n\nRoom Unit Number: " + str(room_unit_no) + "\nEVS Username: " + str(evs_username) + "\nLower Credit Limit: $" + str(lower_credit_limit) + "\n\nYou can access our other functions here!"
    update.message.reply_text(text=text2, reply_markup=main_options_keyboard())
    
    return ConversationHandler.END

# Update Room Information
def prompt_unit(update, context):
    query = update.callback_query

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text = 'May I know your room unit number? (e.g. #01-01 or #01-01A)'
    )
    return UPDATE_ID

def prompt_notif_end(update, context):
    chat_id = update.message.chat.id
    user_input = update.message.text.replace(" ", "")
    
    

    if not (user_input.isdigit() and len(user_input) == 8):
        context.bot.send_message(
        chat_id=chat_id,
        text='Please enter a valid username.'
        )
        return UPDATE_NOTIF
    
    global evs_username
    evs_username = user_input

    # check if credentials are correct 
    if scraper(evs_username,room_unit_no) == None:
        context.bot.send_message(
        chat_id=chat_id,
        text='Your log in details are wrong, please enter your room unit number again. (e.g. #01-01 or #01-01A)'
        )
        return UPDATE_ID

    # update database with new evs username and room number 
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

    text2 = "The following is your current information: \n\nRoom Unit Number: " + str(room_unit_no) + "\nEVS Username: " + str(evs_username) + "\nLower Credit Limit: $" + str(lower_credit_limit) + "\n\nYou can access our other functions here!"
    update.message.reply_text(text=text2, reply_markup=main_options_keyboard())

    return ConversationHandler.END

# Update Lower Credit Limit
def prompt_notif_update(update, context):
    query = update.callback_query

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text = 'What would you like to change your lower credit limit to? (e.g. 2.50)'
    )
    return UPDATE_END

def prompt_end(update, context):
    chat_id = update.message.chat.id
    user_input = update.message.text.replace(" ", "")

    

    if not ((user_input.isdigit()) or isfloat(user_input)):
        context.bot.send_message(
            chat_id=chat_id,
            text='Please enter a valid amount.'
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
    text2 = "The following is your current information: \n\nRoom Unit Number: " + str(room_unit_no) + "\nEVS Username: " + str(evs_username) + "\nLower Credit Limit: $" + str(lower_credit_limit) + "\n\nYou can access our other functions here!"
    update.message.reply_text(text=text2, reply_markup=main_options_keyboard())
    
    return ConversationHandler.END

# Check Aircon Credit Balance
def check_balance(update, context):
    query = update.callback_query

    # use information from database and scraper to return output 

    user = session.query(User).get(username)
    evs_username = user.evs_username
    room_unit_no = user.room_unit_no
    balance = scraper(evs_username,room_unit_no)

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text= '------------' + balance + '------------' + '\nPlease visit https://nus-utown.evs.com.sg/ to top-up your credits.'
    )

    text2 = "The following is your current information: \n\nRoom Unit Number: " + str(room_unit_no) + "\nEVS Username: " + str(evs_username) + "\nLower Credit Limit: $" + str(lower_credit_limit) + "\n\nYou can access our other functions here!"
    context.bot.send_message(
        chat_id=query.message.chat_id,
        text=text2,
        reply_markup=main_options_keyboard())

    return ConversationHandler.END

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
            fallbacks=[CommandHandler('cancel',cancel)],
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
            fallbacks=[CommandHandler('cancel',cancel)],
            per_user=False
        )
    )

    dp.add_handler(
        ConversationHandler(
            entry_points=[CallbackQueryHandler(prompt_notif_update, pattern='update_credit')],
            states={
                UPDATE_END: [MessageHandler(Filters.text, prompt_end)]
            },
            fallbacks=[CommandHandler('cancel',cancel)],
            per_user=False
        )
    )

    dp.add_handler(CallbackQueryHandler(check_balance, pattern='check_balance'))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()