import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import (
    CommandHandler,
    MessageHandler, 
    filters,
    Application,
    ContextTypes, 
    CallbackContext,
    ConversationHandler,
    )

# custom imports
from gemini import gmini_ai

VALUE, DATE, DONE, PIX, EXIT = range(5)

load_dotenv()
TOKEN = os.environ.get("TOKEN")
BOT_USERNAME = os.environ.get("BOT_USERNAME")
GEMINI= os.getenv("GEMINI")

AI = gmini_ai(api_key=GEMINI)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE ):
    await update.message.reply_text("I'm a bot, please talk to me!")    
    
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE ):
    print(update.effective_chat.id)
    await update.message.reply_text("I'm a bot, please talk to me!")    

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE ):
    await update.message.reply_text("I'm a bot, please talk to me!")    

reply_kebood = [['Electricity', 'Water'], ['Internet', 'Gas']]
markup = ReplyKeyboardMarkup(reply_kebood, one_time_keyboard=True)


async def set_remember(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    await update.message.reply_text(
        'which of the bills do you want to register?', reply_markup=markup,  disable_notification=True
    )
    return VALUE

async def bill_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text: str = update.message.text
    context.user_data['tettle']: str = text
    
    await update.message.reply_text(
        f'You have selected {text}.\n What is the value of the bill? \n ex:100.00', disable_notification=True
    )    
    return DATE

async def bill_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        value: int = int(update.message.text)
        context.user_data['value']: int = value
        await update.message.reply_text(
            f'Expiry date of the bill?\n {context.user_data} \n ex: dd/mm 01/11', reply_markup=ReplyKeyboardRemove(), disable_notification=True
        )    
        return PIX
    except ValueError:
        user_data = context.user_data
        if 'tettle' in user_data:
            del user_data['tettle']
        if 'value' in user_data:
            del user_data['value']
        if 'date' in user_data:
            del user_data['date']
        await update.message.reply_text(
            
            'Please enter a valid number', reply_markup=ReplyKeyboardRemove(), disable_notification=True
        )
        user_data.clear()
        return ConversationHandler.END

async def bill_pix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date = update.message.text
    context.user_data['date']: str = date
    await update.message.reply_text(
        'What is your pix key?', reply_markup=ReplyKeyboardRemove(), disable_notification=True
    )
    return DONE

async def bill_done(update: Update, context):
    
    try:
        tettle = context.user_data['tettle']
        value = context.user_data['value']
        divider = float(value / 3   )

        date = context.user_data['date']
        pix = update.message.text

        # await update.message.pin(chat_id, message_id)
        await update.message.reply_text(
            f"⚠️⚠️ ATTENTION {tettle.upper()} BILL ⚠️⚠️\n \n"
            f"Bill:  Value: R$ {value}/3 = R$ {divider}\n\n"
            f"Vencimento dia {date}/2024.\n\n"

            f"Pix chave: {pix}\n"
            "---------------------------------------------------- \n" 

            "✅\n✅\n✅\n"
            "Bill saved successfully!",  
        )#.pin(chat_id=update.message.chat_id, message_id=update.message.message_id)
        return ConversationHandler.END

    except Exception as e:
        await update.message.reply_text(
            'This function is available only in groups',
            reply_markup=ReplyKeyboardRemove(),
            disable_notification=True,
        )
        user_data.clear()
        return ConversationHandler.END
    
async def exit_conversation (update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END

# handel responses
def handel_response(message: str) -> str:
    processed: str = message.lower()

    # if 'hello' in processed:
    #     return 'Hey! How\'s it going?'

    # if 'hi' in processed:
    #     return 'Hey! How\'s it going?'

    # if 'yoo' in processed:
    #     return 'Yoo'

    # if 'how are you' in processed:
    #     return 'I am fine, what about you?'

    # if 'date' in processed:
    #     now = datetime.now().strftime("%d/%m/%y, %H:%M:%S")
    #     toDay = datetime.now().strftime('%A')
    #     return f"Today is {toDay}, {now}"

    # return 'I do not understand'
    return AI.send_message(message)

async def handel_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f"Message received: {text} ({message_type})")
    if (
        message_type == 'group'
        and BOT_USERNAME in text
        or message_type != 'group'
        and message_type == 'supergroup'
        and BOT_USERNAME in text
    ):
        new_text: str = text.replace(BOT_USERNAME, '').strip()
        respond: str = handel_response(new_text)
    elif message_type == 'group':
        pass
    elif message_type == 'supergroup':
        return
    else:
        respond: str = handel_response(text)

    await update.message.reply_text(respond)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update: {update} caused error: {context.error}")

def main():
    print("Starting bot...")
    
    app = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('newBill', set_remember)],
        states={
            VALUE: [MessageHandler(filters.Regex("^(?!.*\?).*"), bill_value)],
            DATE: [MessageHandler(filters.Regex("^(?!.*\?).*"), bill_date)],
            DONE: [MessageHandler(filters.Regex("^(?!.*\?).*"), bill_done)],
            PIX: [MessageHandler(filters.Regex("^(?!.*\?).*"), bill_pix)],
            EXIT: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel$")) , exit_conversation)],
        },
        fallbacks=[MessageHandler(filters.TEXT, handel_message)],
    )
    
    #Commands
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    # app.add_handler(CommandHandler('remember', set_remember))
    
    #Messages
    app.add_handler(MessageHandler(filters.TEXT, handel_message))
    
    #Errors
    app.add_error_handler(error)
    
    #Chack for update
    app.run_polling()

if __name__ == '__main__':
    main()
