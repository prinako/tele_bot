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

import markdown

def handel_response(message: str) -> str:
    """
    This function sends a message to an AI and returns the response.

    Args:
        message (str): The message to send to the AI.

    Returns:
        str: The response from the AI.
    """
    # Sends the message to the AI and gets the response
    resp: str = AI.send_message(message)  # type: ignore

    # Returns the response from the AI
    return resp

async def handel_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle incoming messages and send responses from the AI.

    Args:
        update (telegram.Update): The received update.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): The context object.

    Returns:
        None
    """

    # Get the type of the chat and the text of the message
    message_type: str = update.message.chat.type
    text: str = update.message.text

    # If the message is sent in a group or supergroup and mentions the bot,
    # remove the mention and send the response
    if (
        message_type == 'group' and BOT_USERNAME in text
        or message_type == 'supergroup' and BOT_USERNAME in text
    ):
        new_text: str = text.replace(BOT_USERNAME, '').strip()
        respond: str = handel_response(new_text).replace('##', '').strip()

    # If the message is sent in a group or supergroup, return without sending a response
    elif message_type in {'group', 'supergroup'}:
        return

    # If the message is sent in a one-on-one chat, send the response
    else:
        # respond: str = handel_response(text) #.replace('*', '').strip()
        respond: str = 'To chat with AI, use *AI* option in the *menu* 👇 \nOr Just type */ai* to use the chat AI 🤖'

    # Send the response using Markdown formatting
    try:
        await update.message.reply_markdown_v2(respond)
    except Exception:
        try:
            await update.message.reply_markdown(respond)
        except Exception:
            try:
                await update.message.reply_text(respond, parse_mode='MARKDOWN')
            except Exception:
                try:
                    await update.message.reply_text(respond)
                except Exception as e:
                    await error(update, context, e)


# variables to control the conversation handler for ai
CAI, END_CHAT = range(2)

async def start_conversation_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Start a conversation with the chat-based AI.
    
    Args:
        update (telegram.Update): The received update.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): The context object.
        
    Returns:
        int: The state to transition to.
    """
    # Instantiate a new chat-based AI with the Gemini API key
    new_chat_ai = gmini_ai(api_key=GEMINI)
    
    # Store the chat-based AI in user data
    context.user_data['new_chat_ai'] = new_chat_ai
    
    # Send a message to the user asking what they need help with
    await update.message.reply_text("What can I help you with?")
    
    # Return the state to transition to
    return CAI

async def chat_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle messages for chat-based AI.
    
    Args:
        update (telegram.Update): The received update.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): The context object.
        
    Returns:
        int: The state to transition to.
    """
    # Retrieve the chat-based AI
    new_chat_ai = context.user_data['new_chat_ai']

    # Check if the user wants to end the conversation
    if update.message.text == '/endchat':
        # End the conversation and reply with the AI's response
        resp = new_chat_ai.send_message(update.message.text)
        await update.message.reply_text(resp)
        # Remove the chat-based AI from user data
        user_dat = context.user_data
        if 'new_chat_ai' in user_dat:
            del user_dat['new_chat_ai']
        return ConversationHandler.END
    
    # Generate a response from the chat-based AI
    resp = (new_chat_ai.send_message(update.message.text)).replace('##', '').strip()
    try:
        # Send the response using Markdown v2
        await update.message.reply_markdown_v2(resp)
    except Exception as e:
        try:
            # Send the response using Markdown
            await update.message.reply_markdown(resp)
        except Exception as e:
            try:
                # Send the response using Markdown with parse mode
                await update.message.reply_text(resp, parse_mode='MARKDOWN')
            except Exception as e:
                try:
                    # Send the response as plain text
                    await update.message.reply_text(resp)
                except Exception as e:
                    # Handle any errors and reply with an error message
                    await error(update, context, error=e)
    
    # Return the state to transition to
    return CAI

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE, error: Exception) -> None:
    """
    Handle errors that occur during message processing.

    Args:
        update (telegram.Update): The received update.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): The context object.
        error (Exception): The error that occurred.

    This function prints the update and error, and sends a message to the user
    indicating that something went wrong.
    """
    # Print the update and error
    print(f"Update: {update} caused error: {error}")
    
    # Send a message to the user indicating that something went wrong
    await update.message.reply_text("Oops! Something went wrong. \nPlease try again.")

async def error_internal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle errors that occur during message processing.

    Args:
        update (telegram.Update): The received update.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): The context object.
        error (Exception): The error that occurred.

    This function prints the update and error, and sends a message to the user
    indicating that something went wrong.
    """
    # Print the update and error
    print(f"Update: {update} caused error: {context.error}")
    
    # Send a message to the user indicating that something went wrong
    await update.message.reply_text("Oops! Something went wrong. \nPlease try again.")


def main():
    """
    Main function to start the bot.

    This function builds the bot application and sets up the conversation handlers and command handlers.
    It then runs the polling method to start the bot.
    """
    print("Starting bot...")
    
    # Build the bot application
    app = Application.builder().token(TOKEN).build()
    
    # Set up the conversation handler for new bill
    conv_handler = ConversationHandler(
        # Entry points for the conversation
        entry_points=[CommandHandler('newBill', set_remember)],
        # States for the conversation
        states={
            VALUE: [MessageHandler(filters.Regex("^(?!.*\?).*"), bill_value)],
            DATE: [MessageHandler(filters.Regex("^(?!.*\?).*"), bill_date)],
            DONE: [MessageHandler(filters.Regex("^(?!.*\?).*"), bill_done)],
            PIX: [MessageHandler(filters.Regex("^(?!.*\?).*"), bill_pix)],
            EXIT: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^cancel$")) , exit_conversation)],
        },
        # Fallback handler for unhandled messages
        fallbacks=[MessageHandler(filters.TEXT, handel_message)]
    )
    
    # Set up the conversation handler for chat-based AI
    ai_chat_handler = ConversationHandler(
        # Entry points for the conversation
        entry_points=[CommandHandler('ai', start_conversation_ai)], 
        # States for the conversation
        states={
            CAI: [MessageHandler(filters.TEXT, chat_ai)],
        },
        # Fallback handler for unhandled messages
        fallbacks=[MessageHandler(filters.TEXT, error)]
    )
    
    # Add command handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    
    # Add conversation handlers
    app.add_handler(conv_handler)
    app.add_handler(ai_chat_handler)
    
    # Add message handler
    app.add_handler(MessageHandler(filters.TEXT, handel_message))
    app.add_error_handler(error_internal)
    
    # Start the bot
    app.run_polling(poll_interval=5)

if __name__ == '__main__':
    AI = gmini_ai(api_key=GEMINI)
    main()
