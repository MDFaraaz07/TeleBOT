import logging
from telethon import TelegramClient, events
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os


bot_token = os.getenv('bot_token')
api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')
phone_number = os.getenv('phone_number')
session_enam = os.getenv('session_enam')
# Your existing credentials
bot_token = '8018544160:AAGQm1RCcGcIn9D-31ouDugf8eDiGRRePdE'
api_id = '25294817'  # Get from https://my.telegram.org/
api_hash = '3d511c09129f344ec1c931e72b2d5bc2'  # Get from https://my.telegram.org/
phone_number = '+91 7389491337'  # Your phone number for login


# Set up logging
logging.basicConfig(level=logging.INFO)

# Create the Telegram client for Telethon
client = TelegramClient(session_name, api_id, api_hash)

# Store task-specific source and target groups in a dictionary
task_data = {}

# Create a bot application for handling commands with bot token
application = Application.builder().token(bot_token).build()

# Function to handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_message = (
        "Hello, linux,\n\n"
        "I am @Far_forward_bot 😘\n"
        "I can instantly forward (or copy) messages from various Telegram chats..."
    )
    await update.message.reply_text(start_message)

# Function to show all user's groups/channels with their names and IDs
async def show_groups_ids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog_list = await client.get_dialogs()  # Get all groups/channels
    groups = [d for d in dialog_list if d.is_group or d.is_channel]

    # Create the list of group/channel names and IDs
    group_list = [f"Name: {g.name} | Chat ID: {g.id}" for g in groups]

    # Send the message in chunks if it's too long
    chunk_size = 4096
    message = ""
    for group in group_list:
        if len(message) + len(group) + 1 > chunk_size:
            await update.message.reply_text(message)
            message = ""
        message += group + "\n"

    if message:
        await update.message.reply_text(message)

# Function to set source groups for a specific task
async def set_sources(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task_label = context.args[0]
    source_group_ids = context.args[1:]  # Group IDs after the label

    # Store the source group IDs in the task_data dictionary
    if task_label not in task_data:
        task_data[task_label] = {"sources": [], "targets": []}

    task_data[task_label]["sources"] = [int(group_id) for group_id in source_group_ids]
    logging.info(f"Source groups set for task {task_label}: {source_group_ids}")
    await update.message.reply_text(f"Source groups set for task {task_label}: {', '.join(source_group_ids)}")

# Function to set target groups for a specific task
async def set_targets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task_label = context.args[0]
    target_group_ids = context.args[1:]  # Group IDs after the label

    # Store the target group IDs in the task_data dictionary
    if task_label not in task_data:
        task_data[task_label] = {"sources": [], "targets": []}

    task_data[task_label]["targets"] = [int(group_id) for group_id in target_group_ids]
    logging.info(f"Target groups set for task {task_label}: {target_group_ids}")
    await update.message.reply_text(f"Target groups set for task {task_label}: {', '.join(target_group_ids)}")

# Message handler that listens for new messages in the source groups and forwards to the target groups
@client.on(events.NewMessage())
async def message_handler(event):
    global task_data
    logging.info(f"New message from chat ID: {event.chat_id} - Message: {event.message.message}")

    # Check each task's source groups and forward to the respective target groups
    for task_label, data in task_data.items():
        if event.chat_id in data["sources"]:
            logging.info(f"Message from source group {event.chat_id} for task {task_label}")
            try:
                # Forward the message to all target groups for this task
                for target_group_id in data["targets"]:
                    await client.send_message(target_group_id, event.message.message)
                    if event.message.media:
                        await client.send_file(target_group_id, event.message.media)
                logging.info(f"Copied message from {event.chat_id} to {data['targets']}")
            except Exception as e:
                logging.error(f"Error copying message from {event.chat_id} for task {task_label}: {e}")
        else:
            logging.info(f"Message from unrelated chat: {event.chat_id}")

# Help command
async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "/show_groups_ids - Show all groups/channels IDs with names\n"
        "/set_sources <task_label> <source_id1 source_id2 ...> - Set the source groups/channels\n"
        "/set_targets <task_label> <target_id1 target_id2 ...> - Set the target groups/channels\n"
        "Once set, the bot will copy messages from the source to the target group for each task."
    )
    await update.message.reply_text(help_text)

# Start the client and run the bot
async def main():
    await application.initialize()
    application.add_handler(CommandHandler("show_groups_ids", show_groups_ids))
    application.add_handler(CommandHandler("set_sources", set_sources))
    application.add_handler(CommandHandler("set_targets", set_targets))
    application.add_handler(CommandHandler("help", handle_help))
    application.add_handler(CommandHandler("start", start))
    
    await application.start()
    await application.updater.start_polling()  # Start polling to check for updates
    await client.start()
    await client.run_until_disconnected()

import asyncio
asyncio.run(main())
# this is changed (session_name = 'anon')