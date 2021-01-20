import importlib

from telegram import ParseMode
from telegram.ext import CommandHandler, Filters
from forwarder import API_KEY, OWNER_ID, WEBHOOK, IP_ADDRESS, URL, CERT_PATH, PORT, LOGGER, \
    updater, dispatcher
from forwarder.modules import ALL_MODULES

# 互動按鈕
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

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
    

def reply_markup1(update, context):
    bot.send_message(chat_id, '參考資料',
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton('課程網站', url = 'https://github.com/mzshieh/pa19spring'),
            InlineKeyboardButton('Documentation', url = 'https://python-telegram-bot.readthedocs.io/en/stable/index.html')]]))

# ...
def nearest_stations(bot, update, count=5):
    with open('allstations.csv', newline='', encoding='utf-8') as infile:
        csv_reader = csv.reader(infile, delimiter=';')
        stations = [(int(row[0]), float(row[1]), float(row[2]), row[3]) for row in csv_reader]

        # distance sorting based on http://stackoverflow.com/a/28368926 by Sergey Ivanov
        coord = (float(update.message.location.latitude), float(update.message.location.longitude))
        pts = [geopy.Point(p[1], p[2], p[0]) for p in stations]
        sts = [p[3] for p in stations]
        onept = geopy.Point(coord[0], coord[1])
        alldist = [(p, geopy.distance.distance(p, onept).m) for p in pts]
        nearest = sorted(alldist, key=lambda x: (x[1]))[:count]
        nearest_points = [n[0] for n in nearest]
        nearest_distances = [n[1] for n in nearest]
        nearest_sts = [sts[int(n.altitude)] for n in nearest_points]
        msg = 'Nächstgelegene Stationen:'
        for s, d, p in zip(nearest_sts, nearest_distances, nearest_points):
            msg += '\n{} (<a href="https://www.google.de/maps?q={},{}">{:.0f}m</a>)'.format(s, p.latitude,
                                                                                            p.longitude, d)

        reply_keyboard = [[telegram.KeyboardButton(text='/Abfahrten {}'.format(n))] for n in nearest_sts]
        bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode='HTML',
                        reply_markup=telegram.ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        
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
    reply_markup1 = CommandHandler("reply_markup1", reply_markup1, filters=Filters.user(OWNER_ID), run_async=True)
    nearest_stations = CommandHandler("nearest_stations", nearest_stations, filters=Filters.user(OWNER_ID), run_async=True)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(reply_markup1 )
    dispatcher.add_handler(nearest_stations)
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
