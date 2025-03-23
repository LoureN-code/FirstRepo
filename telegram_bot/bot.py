from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, filters, MessageHandler
import logging
from gpt import *
from util import *
from credentials import *
logging.basicConfig(level=logging.INFO)

async def start(update, context):
    dialog.mode = "main"
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Главное меню',
        'random': 'Узнать случайный интересный факт 🧠',
        'gpt': 'Задать вопрос чату GPT 🤖',
        'talk': 'Поговорить с известной личностью 👤',
        'quiz': 'Поучаствовать в квизе ❓',
        'language': 'Переводчик 🇷🇺🇬🇧🇨🇳🇩🇪🇫🇷',
        'assistant': 'Подготовка резюме'
    })


async def gpt(update, context):
    dialog.mode = "gpt"
    text = load_message("gpt")
    await send_image(update, context, "gpt")
    await send_text(update, context, text)

async def gpt_dialog(update, context):
    text = update.message.text
    prompt = load_prompt("gpt")
    answer = await chat_gpt.send_question(prompt, text)
    await send_text(update, context, answer)

async def talk(update, context):
    dialog.mode = "talk"
    text = load_message("talk")
    await send_image(update, context, "talk")
    await send_text_buttons(update, context, text, {
        "talk_cobain": "Курт Кобейн",
        "talk_queen": "Елизавета II",
        "talk_tolkien": "Джон Толкиен",
        "talk_nietzsche": "Фридрих Ницше",
        "talk_hawking": "Стивен Хокинг",
        "main": "Закончить"
    })

async def talk_dialog(update, context):
    text = update.message.text
    my_message = await send_text(update, context, "Набирает текст...")
    answer = await chat_gpt.add_message(text)
    await my_message.edit_text(answer)
    await send_text_buttons(update, context, text, {
        "main": "Закончить"
    })

async def talk_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()
    await send_image(update, context, query)
    await send_text(update, context, "Отличный выбор!")
    prompt = load_prompt(query)
    chat_gpt.set_prompt(prompt)

async def random(update, context):
    dialog.mode = "random"
    text = load_message("random")
    await send_image(update, context, "random")
    await send_text(update, context, "Вспоминаю факт...")


    prompt = load_prompt("random")
    answer = await chat_gpt.send_question(prompt, text)
    await send_text(update, context, answer)
    await send_text_buttons(update, context, text, {
        "random": "Хочу ещё факт",
        "main": "Закончить"
    })

async def random_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()
    if query == "main":
        await start(update, context)
        return

    if query == "random":
        await random(update, context)
        return


async def quiz(update, context):
    dialog.mode = 'quiz'
    if not context.user_data:
        context.user_data['current_mode'] = None
        context.user_data['quiz'] = None
        context.user_data['count'] = 0
    message = load_message('quiz')
    await send_image(update, context, 'quiz')
    await send_text_buttons(update, context, message, {
        'quiz_prog': 'Программирование на Python',
        'quiz_math': 'Математические теории',
        'quiz_biology': 'Биология'
    })


async def quiz_button(update, context):
    await update.callback_query.answer()
    prompt = load_prompt('quiz')
    query = update.callback_query.data
    if query == 'quiz_more':
        query = context.user_data['current_mode']
    elif query == 'quiz_exit':
        await send_text(update, context, f'Правильных ответов: {context.user_data['count']}')
        context.user_data['current_mode'] = None
        context.user_data['quiz'] = None
        context.user_data['count'] = 0
        await start(update, context)
        return
    else:
        context.user_data['current_mode'] = query
    answer = await chat_gpt.send_question(prompt, query)
    await send_text(update, context, answer)
    context.user_data['quiz'] = 'next'

async def quiz_dialog(update, context):
    if not context.user_data['current_mode'] or not context.user_data['quiz']:
        return
    context.user_data['quiz'] = None
    text = update.message.text
    answer = await chat_gpt.add_message(text)
    if answer == 'Правильно!':
        context.user_data['count'] += 1
    await send_text_buttons(update, context, answer, {
        'quiz_more': 'Следующий вопрос',
        'quiz_exit': 'Завершить'
    })

async def language(update, context):
    dialog.mode = 'language'
    text = load_message('translate')
    await send_image(update, context, 'translate')
    await send_text_buttons(update, context, text, {
        'ru': 'Русский (Russian) 🇷🇺',
        'en': 'Английский (English) 🇬🇧',
        'cn': 'Китайский (China) 🇨🇳',
        'de': 'Немецкий (German) 🇩🇪',
        'fr': 'Французский (French) 🇫🇷'
    })

async def language_button(update, context):
    await update.callback_query.answer()
    query = update.callback_query.data
    dialog.language = query
    dialog.mode = 'translate'
    await send_text(update, context, f"Вы выбрали перевод на {'Русский' if query == 'ru' else ('Английский' if query == 'en'
                                                                                               else ('Китайский' if query == 'cn' 
                                                                                                     else ('Немецкий' if query == 'de' 
                                                                                                           else 'Французский')))} язык")

    chat_gpt.set_prompt(query)

async def language_dialog(update, context):

    if dialog.mode == 'translate' and dialog.language:
        text = update.message.text
        prompt = load_prompt('translate')
        answer = await chat_gpt.send_question(prompt, text)
        await send_text(update, context, answer)
    else:
        await language(update, context)


async def assistant(update, context):
    dialog.mode = "assistant"
    text = load_message("assistant")
    await send_image(update, context, "assistant")
    await send_text(update, context, text)

    dialog.user.clear()
    dialog.count = 0
    await send_text(update, context, "Как тебя зовут?")

async def assistant_dialog(update, context):
    text = update.message.text
    dialog.count += 1

    if dialog.count == 1:
       dialog.user["age"]= text
       await send_text(update, context, "Какое у вас образование?")
    elif dialog.count == 2:
       dialog.user["experience"]= text
       await send_text(update, context, "Опыт работы?")
    elif dialog.count == 3:
        dialog.user["skills"]= text
        await send_text(update, context, "Какие у вас есть навыки?")
    elif dialog.count == 4:
        dialog.user["additional information"]= text
        await send_text(update, context, "Дополнительная информация?")
    elif dialog.count == 5:
        dialog.user["exit"] = text

        prompt = load_prompt("assistant")
        user_info = dialog_user_info_to_str(dialog.user)
        my_message = await send_text(update, context, "ChatGPT 🧠 составляет резюме...")
        answer = await chat_gpt.send_question(prompt, user_info)
        await my_message.edit_text(answer)


async def hello(update, context):
    if dialog.mode == "gpt":
        await gpt_dialog(update, context)
    elif dialog.mode == "talk":
        await talk_dialog(update, context)
    elif dialog.mode == "random":
        await random(update, context)
    elif dialog.mode == "quiz":
        await quiz_dialog(update, context)
    elif dialog.mode == "language":
        await language_dialog(update, context)
    elif dialog.mode == "translate":
        await language_dialog(update, context)
    elif dialog.mode == "assistant":
        await assistant_dialog(update, context)
    else:
        await send_text(update, context, "Вы написали " + update.message.text)

dialog = Dialog()
dialog.mode = None
dialog.list = []
dialog.count = 0
dialog.language = None
dialog.user = {}



chat_gpt = ChatGptService(TOKEN_OPENAI)
app = ApplicationBuilder().token(TOKEN_TG).build()


app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("talk", talk))
app.add_handler(CommandHandler("random", random))
app.add_handler(CommandHandler("quiz", quiz))
app.add_handler(CommandHandler("language", language))
app.add_handler(CommandHandler("assistant", assistant))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))



app.add_handler(CallbackQueryHandler(talk_button, pattern='^talk_'))
app.add_handler(CallbackQueryHandler(random_button, pattern='^random'))
app.add_handler(CallbackQueryHandler(random_button, pattern='^main'))
app.add_handler(CallbackQueryHandler(quiz_button, pattern='^quiz_'))
app.add_handler(CallbackQueryHandler(language_button, pattern='^(ru|en|cn|de|fr)$'))
app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()
