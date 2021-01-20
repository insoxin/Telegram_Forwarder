import importlib

from telegram import ParseMode,InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, Filters,Updater, CallbackQueryHandler
from forwarder import API_KEY, OWNER_ID, WEBHOOK, IP_ADDRESS, URL, CERT_PATH, PORT, LOGGER, \
    updater, dispatcher
from random import randint
from forwarder.modules import ALL_MODULES
PM_START_TEXT = """
Hey {}, 我是{}🤖!
你已经订阅了我们!新的帖子很快就会发布，请保持联系!
回复《/stop》 或 《/unsubscribe》可以退订。
要获取命令列表，请使用《/help》.
<a href='https://twitter.com/jordanbpeterson'>Jordan B. Peterson</a>
"""

PM_HELP_TEXT = """
以下是可用命令的列表：
  - /start：启动机器人。
  - /help ：向您发送此帮助消息。

只需在私人聊天/群组/频道中发送 /id，我将回复它的ID。
"""

for module in ALL_MODULES:
    importlib.import_module("forwarder.modules." + module)
    
def starts(bot, update):
    a, b = randint(1, 100), randint(1, 100)
    update.message.reply_text('{} + {} = ?'.format(a, b),
        reply_markup = InlineKeyboardMarkup([[
                InlineKeyboardButton(str(s), callback_data = '{} {} {}'.format(a, b, s)) for s in range(a + b - randint(1, 3), a + b + randint(1, 3))
            ]]))

def answer(bot, update):
    a, b, s = [int(x) for x in update.callback_query.data.split()]
    if a + b == s:
        update.callback_query.edit_message_text('你答對了！')
    else:
        update.callback_query.edit_message_text('你答錯囉！')

updater = Updater('YOUR TOKEN HERE')

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CallbackQueryHandler(answer))

updater.start_polling()
updater.idle()

def start(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    message = update.effective_message  # type: Optional[Message]
    user = update.effective_user  # type: Optional[User]

    if chat.type == "private":
        message.reply_text(PM_START_TEXT.format(user.first_name, dispatcher.bot.first_name), parse_mode=ParseMode.HTML)
    else:
        message.reply_text("我在！")


def help(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    message = update.effective_message  # type: Optional[Message]

    if not chat.type == "private":
        message.reply_text("不要公开找我，私聊我们的小秘密")
    else:
        message.reply_text(PM_HELP_TEXT)


def main():
    start_handler = CommandHandler("start", start, filters=Filters.user(OWNER_ID), run_async=True)
    help_handler = CommandHandler("help", help, filters=Filters.user(OWNER_ID), run_async=True)
    show_settings_handler = CommandHandler("show_settings", show_settings, filters=Filters.user(OWNER_ID), run_async=True)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    if WEBHOOK:
        LOGGER.info("Using webhooks.")
        updater.start_webhook(listen=IP_ADDRESS,
                              port=PORT,
                              url_path=API_KEY)

        if CERT_PATH:
            updater.bot.set_webhook(url=URL + API_KEY,
                                    certificate=open(CERT_PATH, 'rb'))
        else:
            updater.bot.set_webhook(url=URL + API_KEY)

    else:
        LOGGER.info("使用长时间轮询。超时=15, 读取潜伏期=4")
        updater.start_polling(timeout=15, read_latency=4)

    updater.idle()


if __name__ == '__main__':
    LOGGER.info("成功加载所需模块： " + str(ALL_MODULES))
    main()
