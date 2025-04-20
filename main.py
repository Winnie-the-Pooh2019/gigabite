import argparse
import enum
import os
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_gigachat.chat_models import GigaChat
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters


class ModelType(enum.Enum):
    lite = 'GigaChat-Lite'
    pro = 'GigaChat-Pro'
    max = 'GigaChat-Max'


def map_to_giga_models(model: str) -> ModelType:
    match model:
        case 'pro':
            return ModelType.pro
        case 'max':
            return ModelType.max
        case _:
            return ModelType.lite


def read_system_message(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"File {file_path} Not Found.")
        return ''
    except Exception as e:
        print(f"Error occurred while file reading: {e}")
        return ''


parser = argparse.ArgumentParser()
parser.add_argument('-m', '--model', help='Model type: lite, pro or max', default="lite")
parser.add_argument('-v', '--verbose', action='store_true', help='Print message history to console or not')

args = parser.parse_args()

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GIGA_TOKEN = os.getenv('GIGA_TOKEN')
SYSTEM_PROMPT_FILE = os.getenv('SYSTEM_PROMPT_FILE')

verbose = args.verbose
print(f'\nverbose mode: {"on" if verbose else "off"}')
model_type = map_to_giga_models(args.model)
print(f'\nloading model: {model_type.value}')

system_message = read_system_message(SYSTEM_PROMPT_FILE)
print(f'\ngot system message: {system_message}')

giga = GigaChat(
    credentials=GIGA_TOKEN,
    verify_ssl_certs=False,
    model=str(model_type.value),
)
print('\nmodel loaded successfully')

user_contexts = {}


async def clear_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_contexts[user_id] = []
    await update.message.reply_text("Начнём с чистого листа.")


async def start(update: Update, context):
    messages = [
        SystemMessage(system_message),
        HumanMessage('Добрый день'),
    ]

    try:
        response = giga.invoke(messages)

        bot_response = response.content

        await update.message.reply_text(bot_response[:4000])

    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("System error occurred... Try again later.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_input = update.message.text

    if user_id not in user_contexts:
        user_contexts[user_id] = []

    user_contexts[user_id].append(user_input)

    messages = [
        SystemMessage(system_message),
        *user_contexts[user_id]
    ]

    try:
        response = giga.invoke(messages)
        bot_response = response.content
        user_contexts[user_id].append(response)

    except Exception as e:
        print(f"Error: {e}")
        bot_response = 'System error occurred... Try again later.'

    if verbose:
        print(f'\nuser: {user_id}\n\tuser message: {user_input}\n\tresponse: {bot_response}\n')

    await update.message.reply_text(bot_response)


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler("clear", clear_context))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()


if __name__ == "__main__":
    main()
