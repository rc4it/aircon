from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
import random

def start(update, context):
    print("UPDATE:", update)
    print("CONTEXT:", context)

    chat_id = update.message.chat.id
    username = update.message.from_user.first_name

    update.message.reply_text("Hi " + username + "! How may I help you today?", reply_markup=main_options_keyboard())

def new_user(update, context):
    query = update.callback_query
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text = 'May I know your 8-digit EVS Username? (e.g. 12345678)'
    )
    return 1

def room_id(update, context):
    chat_id = update.message.chat.id
    user_input = update.message.text
    
    if not user_input.isdigit() and len(user_input) == 8:
        context.bot.send_message(
        chat_id=chat_id,
        text='Please enter a valid username.'
        )
        return 1

    text = "You have been logged into " + user_input + ". Please enter your preferred lower credit limit. (e.g. 5)"

    context.bot.send_message(
        text=text,
        chat_id=chat_id
    )
    return 2

def update_id(update, context):
    query = update.callback_query
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text = 'May I know your 8-digit EVS Username? (e.g. 12345678)'
    )
    return 1

def update_id_end(update, context):
    chat_id = update.message.chat.id
    user_input = update.message.text

    if not user_input.isdigit() and len(user_input) == 8:
        context.bot.send_message(
        chat_id=chat_id,
        text='Please enter a valid username.'
        )
        return 1

    text = "You have been logged into " + user_input + ". Thank you."

    context.bot.send_message(
        chat_id=chat_id,
        text=text
    )
    return ConversationHandler.END

def notif_pref(update, context):
    chat_id = update.message.chat.id
    user_input = update.message.text

    if not user_input.isdigit():
        context.bot.send_message(
            chat_id=chat_id,
            text='Please enter a valid amount.'
        )
        return 2

    text = "Your lower credit limit has been set to $" + user_input + ". That is all for now, thank you!"

    context.bot.send_message(
        text=text,
        chat_id=chat_id
    )
    return ConversationHandler.END

def update_notif(update, context):
    query = update.callback_query
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text = 'May I know your what you would like to change your lower credit limit to?'
    )
    return 1

def update_notif_end(update, context):
    chat_id = update.message.chat.id
    user_input = update.message.text

    if not user_input.isdigit():
        context.bot.send_message(
            chat_id=chat_id,
            text='Please enter a valid amount.'
        )
        return 1

    text = "Your lower credit limit has been set to $" + user_input + ". Thank you."

    context.bot.send_message(
        chat_id=chat_id,
        text=text
    )
    return ConversationHandler.END

def check_balance(update, context):
    query = update.callback_query
    opt_buttons = [[KeyboardButton(text='Yes')],[KeyboardButton(text='No')]]

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text='Your current balance is NULL.'
    )

    context.bot.send_message(
        chat_id=query.message.chat_id,
        text='Would you like to top-up?',
        reply_markup=ReplyKeyboardMarkup(keyboard=opt_buttons, one_time_keyboard = True)
    )
    return 1

def check_balance_end(update, context):
    chat_id = update.message.chat.id
    user_input = update.message.text

    if user_input == 'Yes':
        context.bot.send_message(
            chat_id=chat_id,
            text='Please visit https://nus-utown.evs.com.sg/ to top-up your credits. Thank you.'
        )
        return ConversationHandler.END
    
    elif user_input == 'No':
        context.bot.send_message(
            chat_id=chat_id,
            text='That is all for now. Thank you.'
        )
        return ConversationHandler.END

    context.bot.send_message(
        chat_id=chat_id,
        text='Please enter Yes/No.'
    )
    return 1

def main_options_keyboard():
    keyboard = [
        [InlineKeyboardButton("New User", callback_data='newuser')],
        [InlineKeyboardButton("Update Login Details", callback_data='update_id')],
        [InlineKeyboardButton("Update Notification Settings", callback_data='notifications')],
        [InlineKeyboardButton("Check Aircon Credit Balance", callback_data='check_balance')]
    ]
    return InlineKeyboardMarkup(keyboard)

def main():
    # Get telegram bot token from botfather, and do not lose or reveal it
    # TODO: Change below to your bot token
    BOT_TOKEN = "1498781046:AAEtpdoE6uorK4iCpjTj-YNvBMIA3pIimAc"

    # bot updater, refer to https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.updater.html
    updater = Updater(BOT_TOKEN, use_context=True)

    # bot dispatcher to register command handlers
    dp = updater.dispatcher

    # put your handlers here
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(
        ConversationHandler(
            entry_points=[CallbackQueryHandler(new_user, pattern='newuser')],
            states={
                1: [MessageHandler(Filters.text, room_id)],
                2: [MessageHandler(Filters.text, notif_pref)]
            },
            fallbacks=[],
            per_user=False
        )
    )

    dp.add_handler(
        ConversationHandler(
            entry_points=[CallbackQueryHandler(update_id, pattern='update_id')],
            states={
                1: [MessageHandler(Filters.text, update_id_end)]
            },
            fallbacks=[],
            per_user=False
        )
    )

    dp.add_handler(
        ConversationHandler(
            entry_points=[CallbackQueryHandler(update_notif, pattern='notifications')],
            states={
                1: [MessageHandler(Filters.text, update_notif_end)]
            },
            fallbacks=[],
            per_user=False
        )
    )

    dp.add_handler(
         ConversationHandler(
            entry_points=[CallbackQueryHandler(check_balance, pattern='check_balance')],
            states={
                1: [MessageHandler(Filters.text, check_balance_end)]
            },
            fallbacks=[],
            per_user=False
        )
    )

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()