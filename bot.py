from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
import os
from datetime import datetime, timedelta
import asyncio

# In-memory user token storage
user_tokens = {}

# Scheduler for auto token expiry
scheduler = BackgroundScheduler()
scheduler.start()

TOKEN = os.getenv('TOKEN')
CHANNEL_ID = '@BlizzardLinks'

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_tokens or user_tokens[user_id]['expiry'] < datetime.now():
        await show_ads(update, context)
    else:
        await send_video(update, context)

# Show Fake Ads
async def show_ads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Watch Ad 1 (30 sec)", callback_data='ad1')]]
    await update.message.reply_text('Please watch the ads to unlock access:', reply_markup=InlineKeyboardMarkup(keyboard))

# Handle Ad Clicks
async def ad_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'ad1':
        await query.edit_message_text('Watching Ad 1... (Wait 30 sec)')
        await asyncio.sleep(30)
        keyboard = [[InlineKeyboardButton("Watch Ad 2 (30 sec)", callback_data='ad2')]]
        await query.message.reply_text('Ad 1 completed!', reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'ad2':
        await query.edit_message_text('Watching Ad 2... (Wait 30 sec)')
        await asyncio.sleep(30)
        keyboard = [[InlineKeyboardButton("Watch Ad 3 (30 sec)", callback_data='ad3')]]
        await query.message.reply_text('Ad 2 completed!', reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'ad3':
        await query.edit_message_text('Watching Ad 3... (Wait 30 sec)')
        await asyncio.sleep(30)

        user_id = query.from_user.id
        user_tokens[user_id] = {'expiry': datetime.now() + timedelta(hours=24)}
        scheduler.add_job(lambda: user_tokens.pop(user_id, None), 'date', run_date=datetime.now() + timedelta(hours=24))

        await query.message.reply_text('Ad process completed! Token active for 24 hours.')
        await send_video(query, context)

# Send Video
async def send_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video_message = await context.bot.send_video(chat_id=update.effective_user.id, video='YOUR_VIDEO_FILE_ID', supports_streaming=True)
    await asyncio.sleep(1200)  # 20 minutes
    await context.bot.delete_message(chat_id=video_message.chat_id, message_id=video_message.message_id)

# Main Setup
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(CallbackQueryHandler(ad_handler))

app.run_polling()
