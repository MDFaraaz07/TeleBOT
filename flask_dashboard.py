from flask import Flask, render_template, request, redirect, url_for
import logging
from telethon import TelegramClient, events
import asyncio

app = Flask(__name__)

# Your Telegram Bot and Telethon credentials
bot_token = '8018544160:AAGQm1RCcGcIn9D-31ouDugf8eDiGRRePdE'
api_id = '25294817'  # Get from https://my.telegram.org/
api_hash = '3d511c09129f344ec1c931e72b2d5bc2'  # Get from https://my.telegram.org/
phone_number = '+91 7389491335'  # Your phone number for login
session_name = 'anon'

# Create the Telegram client
client = TelegramClient(session_name, api_id, api_hash)

# Example task data (this should be dynamically managed)
tasks = [
    {'label': 'Task 1', 'source_group_ids': [-1001752417741], 'target_group_ids': [-1001857701288]},
    {'label': 'Task 2', 'source_group_ids': [-1001828758385], 'target_group_ids': [-1001857701288]}
]

# Home route to display the dashboard
@app.route('/')
def dashboard():
    return render_template('dashboard.html', tasks=tasks, enumerate=enumerate)


# Route to add a new task
@app.route('/add_task', methods=['POST'])
def add_task():
    label = request.form['label']
    source_ids = request.form['source_group_ids'].split(',')
    target_ids = request.form['target_group_ids'].split(',')

    new_task = {
        'label': label,
        'source_group_ids': [int(sid.strip()) for sid in source_ids],
        'target_group_ids': [int(tid.strip()) for tid in target_ids]
    }

    tasks.append(new_task)
    return redirect(url_for('dashboard'))

# Route to delete a task
@app.route('/delete_task/<int:task_index>')
def delete_task(task_index):
    if 0 <= task_index < len(tasks):
        tasks.pop(task_index)
    return redirect(url_for('dashboard'))

# Start the Telethon client
async def start_telethon():
    await client.start()
    await client.run_until_disconnected()

# Run both the bot and the Flask server
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(start_telethon())
    app.run(debug=True)
