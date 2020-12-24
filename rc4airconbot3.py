from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler


# /start
def start(update, context):
    print("UPDATE:", update)
    print("CONTEXT:", context)

    chat_id = update.message.chat.id
    username = update.message.from_user.username

    update.message.reply_text("Hi @" + username + "! How may I help you today?", reply_markup=main_options_keyboard())

def main_options_keyboard():
    keyboard = [
        [InlineKeyboardButton("New User", callback_data='newuser')],
        [InlineKeyboardButton("Update Room Information", callback_data='update_id')],
        [InlineKeyboardButton("Update Lower Credit Limit", callback_data='update_credit')],
        [InlineKeyboardButton("Check Aircon Credit Balance", callback_data='check_balance')]
    ]
    return InlineKeyboardMarkup(keyboard)

# New User
UPDATE_ID, UPDATE_NOTIF, UPDATE_END = range(3)
def prompt_unit(update, context):
    query = update.callback_query
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text = 'May I know your room unit number? (e.g. #01-01 or #01-01A)'
    )
    return UPDATE_ID

def prompt_id(update, context):
    chat_id = update.message.chat.id
    user_input = update.message.text.replace(" ", "")
    
    if (user_input[0] != '#') or (user_input[3] != '-'):
        context.bot.send_message(
        chat_id=chat_id,
        text='Please key in using this format #xx-xx or #xx-xxx.'
        )
        return UPDATE_ID
    
    if len(user_input) == 7 and (not user_input[6].isalpha()):
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

    text = "Your room " + user_input + " has been registered into our system. \nPlease enter your EVS Username. (e.g. 12345678)."

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

    text = "You have been logged into " + user_input + ". \nPlease enter your preferred lower credit limit. (e.g. 5)"

    context.bot.send_message(
        text=text,
        chat_id=chat_id
    )
    return UPDATE_END

def prompt_end(update, context):
    chat_id = update.message.chat.id
    user_input = update.message.text.replace(" ", "")

    if not user_input.isdigit():
        context.bot.send_message(
            chat_id=chat_id,
            text='Please enter a valid amount.'
        )
        return UPDATE_END

    text = "Your lower credit limit has been set to $" + user_input + ". \nInformation has been updated. Press /start for other functions."

    context.bot.send_message(
        chat_id=chat_id,
        text=text
    )
    return ConversationHandler.END

# Update Room Information
def prompt_notif_end(update, context):
    chat_id = update.message.chat.id
    user_input = update.message.text.replace(" ", "")
    
    if not (user_input.isdigit() and len(user_input) == 8):
        context.bot.send_message(
        chat_id=chat_id,
        text='Please enter a valid username.'
        )
        return UPDATE_NOTIF

    text = "You have been logged into " + user_input + ". \nInformation has been updated. Press /start for other functions."

    context.bot.send_message(
        text=text,
        chat_id=chat_id
    )
    return ConversationHandler.END

# Update Lower Credit Limit
def prompt_notif_update(update, context):
    query = update.callback_query
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text = 'What would you like to change your lower credit limit to? (e.g. 5)'
    )
    return UPDATE_END

# Check Aircon Credit Balance
def check_balance(update, context):
    query = update.callback_query

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text='Your current balance is NULL. \nPlease visit https://nus-utown.evs.com.sg/ to top-up your credits. \nPress /start for other functions.'
    )

    return ConversationHandler.END

# main()
def main():
    BOT_TOKEN = "1498781046:AAEtpdoE6uorK4iCpjTj-YNvBMIA3pIimAc"
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # put your handlers here
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(
        ConversationHandler(
            entry_points=[CallbackQueryHandler(prompt_unit, pattern='newuser')],
            states={
                UPDATE_ID: [MessageHandler(Filters.text, prompt_id)],
                UPDATE_NOTIF: [MessageHandler(Filters.text, prompt_notif)],
                UPDATE_END: [MessageHandler(Filters.text, prompt_end)]
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

    dp.add_handler(CallbackQueryHandler(check_balance, pattern='check_balance'))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()