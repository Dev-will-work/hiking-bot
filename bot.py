import logging
import random
import re
from itertools import tee

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Updater, MessageHandler, Filters, ConversationHandler,
)

from config import TELEGRAM_BOT_TOKEN

FIRST, SECOND, THIRD = range(3)

results = {'sleep': """Ловец снов в пролёте 😴
Ребят, у меня до похода весь режим сломался и спальники с собой, прилягу на минуток 10
 и пойду таскать дрова на свежую голову 🤪
*Немногим позже после обеда*
Так, уже темнеет, прикорну-ка ненадолго и потом сразу все решим!
Добрый вечер, а, ночь, а что как темно 😐🌚""",
           'fire': """Костровой на взводе 🔥
От создателей «Чей кроссовок тут загорелся?» и «Нужно больше хвороста, милорд», и конечно
 «Неправильно вы костер сложили, дайте покажу как надо.. *****, держите котёл скорее!!» 🤯""",
           'photo': """Фотограф в работе 📸😎
Наверняка вы по приезде вокруг себя мешающих заниматься делом лемуров найдёте,
 а впрочем, это далеко не все источники счастья для вас в походе 🤩
Зато вы прекрасные воспоминания для всех за это время соберёте 🔮""",
           'car': """Водитель на Форде
А может и не на Форде, а может и не водитель.. 🤔
Но точно то, что воды теперь всем хватит в походе, и вещей вы один как 10 человек привезете,
 ну и заодно людей поближе к месту похода довезёте 🧳🌊""",
           'food': """Опытный повар вроде 👨‍🍳
Это понятно, что в походе пасту Болоньезе никто не даст, максимум томатную пасту сами туда возьмете..
Но что до сих пор не понятно, как вы полезную и вкусную еду из минимума ингредиентов создаёте 😋💯
Главное, чтобы всем осталось, ну и вы сами не остались с едой в пролёте 😊""",
           'forest': """Дитя леса на свободе 🌲
Ребята, как же тут классно всё-таки, через несколько минут вернусь.. ⏳
*Через несколько часов, когда все ушли за дровами и бревнами*
Костровой, а где все? А, понятно 🙂
пойду за ними схожу..
*Примерно в конце похода*
А, так вы уже тут, ЧТО, как уже всё?? 😵💢""",
           'friends': """Искатель друзей в собравшемся народе 🤗
Пока вы идете до отрядного места с отрядом вы подходите поздороваться к паре людей, а от них к еще паре людей,
 и всё, неизвестно как но теперь вы в Костроме 👺
А с другой стороны большая часть пути на природе и обратно с друзьями вы тоже дорогу найдёте 😏🚷""",
           'clothes': """Одетый/Одетая по погоде ⛅
Оно конечно понятно, что в походы мы весной и осенью ходим, 
но с таким количеством одежды вероятно вы достаточно медленно идёте и быстро устаёте 🥱 
А если очень повезет, то вам с костюмом даже выпадет возможность искупаться в болоте 💦🦺""",
           'guitar': """Гитарист на природе 🎶
Я на спевку, ближайшие час или полчаса без меня проживёте 😏
Так, все вместе сцепляемся в круг, 5 шагов назад, и ещё шаг...
*1,5 км спустя*
Никто меня не слышит? Отлично, тогда начинаем 🔥🎼""",
           'axe': """Лесоруб на охоте 🤠🪓
Так, здесь значит будем сидеть, понято, сейчас приду 🚶‍♂️
Штош, 16 бревен нам должно хватить 😼
И еще 32 дерева посрубали чтоб другим хватило 😉
Только полностью сухие брали, само собой, такие же как мы будем на завтрашнее утро 💧☠"""}

test_message_bank = iter(["Итак, начнём короткий тест:\nТы любишь ходить и гулять?",
                          "Открытость к людям и общению с ними, нравится такое?",
                          "Сила и выносливость, это про тебя?",
                          "А с ответственностью как дела?"])
test_message_bank, shadow_message_bank = tee(test_message_bank)

your_destiny = ""

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)
bot = Bot(token=TELEGRAM_BOT_TOKEN)


def calculate_result() -> str:
    mapping = {'----': 'sleep',
               '---+': 'photo',
               '--+-': 'clothes',
               '--++': 'guitar',
               '-+--': 'friends',
               '-+-+': 'food',
               '-++-': 'car',
               '-+++': 'car',
               '+---': 'forest',
               '+--+': 'photo',
               '+-+-': 'clothes',
               '+-++': 'guitar',
               '++--': 'friends',
               '++-+': 'fire',
               '+++-': 'car',
               '++++': 'axe'
               }
    return mapping[your_destiny]


def start_command_handler(update: Update, _: CallbackContext) -> int:
    """ Send a message when the command /start is issued."""
    user = update.message.from_user
    logger.info("Пользователь %s начал разговор", user.first_name)
    keyboard = [
        [
            InlineKeyboardButton("А кто я?", callback_data="answer question"),
            InlineKeyboardButton("Я точно знаю кто я 😎", callback_data="answer exact")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f'''Привет, {user.first_name}! 🏕
Наверняка ты скучаешь по незабываемым событиям осеннего похода.. 👀
Но не грусти, мы подготовили для тебя смешной тест о том, кто ты обычно в походе 🤠
А может, ты уже и так знаешь? 🧐
    ''', reply_markup=reply_markup)

    return FIRST


def continuation_handler(update: Update, _: CallbackContext):
    result = update.callback_query.data.split()[1]
    update.callback_query.answer()
    if result == "question":
        keyboard = [
            [
                InlineKeyboardButton("Не, тороплюсь(", callback_data="answer random"),
                InlineKeyboardButton("Да, найдется)", callback_data="answer test"),
            ]
        ]
        message_content = "А есть пара минуток на мааленький тест? 🥺"
    elif result == "exact":
        keyboard = [
            [
                InlineKeyboardButton("Спать люблю", callback_data="answer sleep"),
                InlineKeyboardButton("Хочу костёр!", callback_data="answer fire"),
            ],
            [
                InlineKeyboardButton("Дайте фотки сделаю!", callback_data="answer photo"),
                InlineKeyboardButton("Ало, что привезти?", callback_data="answer car"),
            ],
            [
                InlineKeyboardButton("Так, где мой котёл?", callback_data="answer food"),
                InlineKeyboardButton("Ща в лес сбегаю", callback_data="answer forest"),
            ],
            [
                InlineKeyboardButton("Пойду поздороваюсь", callback_data="answer friends"),
                InlineKeyboardButton("Блин, что-то жарко", callback_data="answer clothes"),
            ],
            [
                InlineKeyboardButton("Так, щас спою", callback_data="answer guitar"),
                InlineKeyboardButton("Я за бревнами", callback_data="answer axe"),
            ]
        ]
        message_content = "Ладненько, тогда выбери фразу себе по душе 😇"
    else:
        raise ValueError(f"Unknown answer {result}!")

    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(update.callback_query.message.chat_id,
                     text=message_content, reply_markup=reply_markup)

    return SECOND


def result_handler(update: Update, _: CallbackContext):
    result = update.callback_query.data.split()[1]
    update.callback_query.answer()

    if result == "yes":
        keyboard = [
            [
                InlineKeyboardButton("А кто я?", callback_data="answer question"),
                InlineKeyboardButton("Да, я знаю кто я 😎", callback_data="answer exact")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(update.callback_query.message.chat_id,
                         text='''Круто, давай погадаем кто ты в походе еще разок 🔥
Итак, ты знаешь свою роль в походе? 🧐''',
                         reply_markup=reply_markup)

        return FIRST
    elif result == "no":
        query = update.callback_query
        query.answer()
        bot.send_message(update.callback_query.message.chat_id,
                         text="""Ну ладно 🙄 
До встречи тогда! Увидимся в следующий раз! 
Расскажи обо мне своим друзьям, если несложно)
Псс, и если соскучишься, набери /start или что-нибудь с "кто я", и отправь мне :)""")
        return ConversationHandler.END


def feedback_handler(update: Update, _: CallbackContext):
    global your_destiny
    global shadow_message_bank, test_message_bank
    result = update.callback_query.data.split()[1]
    update.callback_query.answer()

    keyboard = [
        [
            InlineKeyboardButton("Да, давай", callback_data="answer yes"),
            InlineKeyboardButton("Не, хватит пожалуй", callback_data="answer no"),
        ]
    ]

    if result in ("test", "yes", "no"):
        keyboard = [
            [
                InlineKeyboardButton("Скорее, да", callback_data="answer yes"),
                InlineKeyboardButton("Думаю, нет", callback_data="answer no"),
            ]
        ]
        if result == "yes":
            your_destiny += '+'
        elif result == "no":
            your_destiny += '-'

        try:
            next_text = next(test_message_bank)
        except StopIteration:
            keyboard = [
                [
                    InlineKeyboardButton("Да, и правда", callback_data=f"answer {calculate_result()}"),
                    InlineKeyboardButton("Нее, долго было!! 👹", callback_data=f"answer {calculate_result()}"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.send_message(update.callback_query.message.chat_id,
                             text="Вот и всё!) Недолго, верно?)", reply_markup=reply_markup)

            return SECOND

        print(f"Now {your_destiny}")

        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(update.callback_query.message.chat_id,
                         text=next_text, reply_markup=reply_markup)

        return SECOND

    elif result == "random" or result in results.keys():
        if result == "random":
            result = random.sample(results.keys(), 1)[0]
        bot.send_photo(update.callback_query.message.chat_id, photo=open(f"./results/{result}.jpg", 'rb'),
                       caption=f"Похоже, ты...\n{results[result]}\n\nХочешь еще раз попробую предсказать, или не? 🤔",
                       reply_markup=InlineKeyboardMarkup(keyboard))
        your_destiny = ""
        test_message_bank, shadow_message_bank = tee(shadow_message_bank)
    else:
        raise ValueError(f"Bad result! Maybe path traversal or something unknown!")

    return THIRD


def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(TELEGRAM_BOT_TOKEN)  # type: ignore

    dispatcher = updater.dispatcher  # type: ignore

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start_command_handler),
            MessageHandler(Filters.regex(re.compile(r'кто я', re.IGNORECASE)), start_command_handler)
        ],
        states={
            FIRST: [
                CallbackQueryHandler(continuation_handler, pattern='^answer (.*)$')
            ],
            SECOND: [
                CallbackQueryHandler(feedback_handler, pattern='^answer (.*)$')
            ],
            THIRD: [
                CallbackQueryHandler(result_handler, pattern='^answer (.*)$')
            ]
        },
        fallbacks=[CommandHandler('start', start_command_handler)],
    )
    dispatcher.add_handler(conv_handler)

    # dispatcher.add_handler(CommandHandler('start', start_command_handler))
    # dispatcher.add_handler(CommandHandler('gettasklist', tasklist_command))
    # dispatcher.add_handler(InlineQueryHandler(inline_query_handler))
    # dispatcher.add_handler(CallbackQueryHandler(button_handler))
    # dispatcher.add_handler(
    #     MessageHandler(Filters.text & ~Filters.command, text_handler)  # type: ignore
    # )

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
