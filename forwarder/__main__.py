import importlib

from telegram import ParseMode
from telegram.ext import CommandHandler, Filters
from forwarder import API_KEY, OWNER_ID, WEBHOOK, IP_ADDRESS, URL, CERT_PATH, PORT, LOGGER, \
    updater, dispatcher
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
    
    
def start(update, context):
    update.message.reply_text(
        'hello, {}'.format(update.message.from_user.first_name))

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
    hello_handler = CommandHandler("hhello", hello, filters=Filters.user(OWNER_ID), run_async=True)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(hello_handler)

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
        LOGGER.info("Using long polling.")
        updater.start_polling(timeout=15, read_latency=4)

    updater.idle()


if __name__ == '__main__':
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    main()
