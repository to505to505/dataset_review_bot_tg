#imports
#from asyncore import dispatcher 
import request1 as R
import logging
TOKEN = '5497861232:AAHuktc9mz6HMqCRI3UPMB8XnuKt3qtzq_8'

async def start(update, context): 
    '''  '''
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Hi, I am Dataset Review Bot made by Dmitrii Sakharov! Send me a csv (comma-separated) file of your dataset and I'll analyze it for you! Very handy! You should make sure that the qualitative attributes in your data (for example: gender, color, country, etc.) are text values, not numeric values! If you have any questions, send /help"
    )
    
async def instructions(update, context):
    await context.bot.send_message(   
        chat_id = update.effective_chat.id,
        text = "To use me, you should send a .csv (comma-separated) file with your data. VERY IMPORTANT - make sure that qualitative trait values are entered as text, not as a number (Gender 1, 0 should be male, female, for example). Let's make our work together easier!"
    )
    
async def help(update, context):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Here's a list of commands I know:\n/start - Welcome command with data requirements\n/instructions - instructions to work with me\n"
              )
    
         
async def unknown(update, context):
    text = 'Sorry, I do not know this command :(.\nWrite /help so I can help you!'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text
    )

from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler
from telegram import *
from telegram.ext import *

#logs activate
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   level=logging.INFO
                )

if __name__ == "__main__":
    
    application = ApplicationBuilder().token(TOKEN).read_timeout(30).write_timeout(30).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('instructions', instructions))
    application.add_handler(MessageHandler(filters.Document.ALL, R.get_document))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    application.add_handler(CallbackQueryHandler(R.get_buttons_callbacks))
    
    application.run_polling()

