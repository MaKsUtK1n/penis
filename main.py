from telebot import TeleBot
from telebot.types import * 
from sqlite3 import connect
from requests import post, get
from config import *
from kb import *
from time import time, ctime
from games import games
from re import sub, findall
from random import choice as random
from random import randint


con = connect("users.db", check_same_thread=False, isolation_level=None)
cursor = con.cursor()
bot = TeleBot(bot_token, "HTML", disable_notification=True)
headers = {'Content-Type': 'application/json', 'Crypto-Pay-API-Token': crypto_token}
emoji_list = ["✊", "✌️", "✋"]


def get_data(id):
    cursor.execute("SELECT * FROM users WHERE id=?", (id,))
    udata = cursor.fetchone()
    if udata is None:
        data = (id, 0, 0, 0.0, 0.0, 0.0, None, time())
        cursor.execute("INSERT INTO users VALUES(?,?,?,?,?,?,?,?)", data)
        con.commit()
    else: data = udata
    return data


def generate_rand_str(len):
    return "".join([random("qwertyuioplkjhgfdsazxcvbnm") for _ in range(len)])


def create_cheque(id, summ):
    cheque = post("https://pay.crypt.bot/api/createCheck", json={'amount': summ, 'asset': "USDT"}, headers=headers).json()
    if "result" not in cheque:
        return False
    else:
        code = generate_rand_str(16)
        cursor.execute("INSERT INTO cheques VALUES(?,?,?)", (id, code, cheque['result']['bot_check_url']))
        con.commit()
        return code



def is_subs(id):
    try: 
        bot.get_chat_member(channel_id, id)
        return False
    except: 
        return True


@bot.message_handler(func=lambda m: is_subs(m.from_user.id))
@bot.callback_query_handler(func=lambda m: is_subs(m.from_user.id))
def unsubscribed(message):
    if type(message) is Message:
        bot.reply_to(message, "<b>Для продолжения работы подпишитесь на каналы</b>", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Подписаться", channel_link)))
    else:
        bot.edit_message_text("<b>Для продолжения работы подпишитесь на каналы</b>", message.message.chat.id, message.message.id, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Подписаться", channel_link)))




@bot.channel_post_handler(func=lambda m: m.chat.id == payments_id)
def bet_handle(message: Message):
    link = f'https://t.me/{message.chat.username}/{message.id}'
    try:
        user = message.entities[0].user
        if user is None: raise Exception
        if user.last_name is None:
            name = user.first_name
        else:
            name = user.first_name + " " + user.last_name
        user_info = get_data(user.id)
    except Exception as e:
        msg = bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBkWc7cJqTk_WX1iwcJ0J7c4XoKAJ5AAKh6DEb_7fhSYf0Hqo1H7TNAQADAgADcwADNgQ", f"<b>Ошибка! Возможно вы указали неправильный комментарий для игры, либо же у вас не включен в настройках конфиденциальности пересыл на все. Советую эту сделать, чтобы начать играть. 🎩<blockquote>Обратитесь в тех поддержку для выяснения причины и возврата средств: t.me/maybesmall 🎲</blockquote></b>" + penis_text, reply_markup=error_kb())
        return
    rtext = message.text.replace(name, "", 1)
    bet = round(float(rtext.split('($')[1][:6].split(')')[0]), 2)
    try:
        if "💬" not in rtext: raise Exception
        game = rtext.split("💬 ")[-1].lower().replace("ё", 'е')
    except Exception as e:
        msg = bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBkWc7cJqTk_WX1iwcJ0J7c4XoKAJ5AAKh6DEb_7fhSYf0Hqo1H7TNAQADAgADcwADNgQ", f"<b>Ошибка! Возможно вы указали неправильный комментарий для игры, либо же у вас не включен в настройках конфиденциальности пересыл на все. Советую эту сделать, чтобы начать играть. 🎩<blockquote>Обратитесь в тех поддержку для выяснения причины и возврата средств: t.me/maybesmall 🎲</blockquote></b>" + penis_text, reply_markup=error_kb())
        return
    user_stats = {"win": None, "sum": None}
    name = sub("....(dice|casino|bet|cube)", "*******", name.lower())
    new_bet_text = f'''<b>{name} <a href="{link}">ставит</a> {bet}$

<blockquote>💬 {game}</blockquote></b>'''
    if game == "плинко":
        bot.send_message(channel_id, new_bet_text, disable_web_page_preview=True)
        cube_msg = bot.send_dice(channel_id, "🎲")
        cube_value = cube_msg.dice.value
        if cube_value == 1:
            user_stats['win'] = False
            user_stats['sum'] = bet
            bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBkGc7cI7bxNm_GTpQLJ0MoBiqrXksAAKg6DEb_7fhSYYST4QpYqrRAQADAgADcwADNgQ", f"<b>⛔️ Поражение!\n\n🔮 В следующей ставке фортуна улыбнется тебе\n<blockquote>Выпало число {res}\nКидай кубик и испытай свою удачу!👻 </blockquote></b>" + penis_text, reply_markup=lose_kb())
        else:
            win_sum = round(bet * games['pl'][cube_value], 2)
            pon = create_cheque(user.id, win_sum)
            user_stats['win'] = True
            user_stats['sum'] = win_sum
            if not pon:
                bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBkWc7cJqTk_WX1iwcJ0J7c4XoKAJ5AAKh6DEb_7fhSYf0Hqo1H7TNAQADAgADcwADNgQ", f"<b>Обратитесь к @{owner_username} для получения {win_sum}</b>" + penis_text, reply_markup=error_kb())
            else:
                bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBjWc7cIbaNWyMCU8sSpSsMPWmL7pEAAKf6DEb_7fhSUXjOO9zZ9iBAQADAgADcwADNgQ", f"<b>🍾Победа!\n\n😎Ты настоящий профи\n\n<blockquote>Выпало число {res}\nВыигрыш зачислен на баланс победителя.\nКидай кубик и испытай свою удачу!👻 🎃</blockquote>\n\n• Сумма выигрышарышаша {win_sum}$ X {win_sum * 100.5} RUB</b>" + penis_text, reply_markup=win_kb(pon))
    
    elif game == "камень":
        bet_id = bot.send_message(channel_id, new_bet_text, disable_web_page_preview=True)
        emoji = random(emoji_list)
        bot.send_message(channel_id, "✊")
        bot.send_message(channel_id, emoji)
        if emoji == "✋":
            user_stats['win'] = False
            user_stats['sum'] = bet
            bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBkGc7cI7bxNm_GTpQLJ0MoBiqrXksAAKg6DEb_7fhSYYST4QpYqrRAQADAgADcwADNgQ", f"<b>⛔️ Поражение!\n\n🔮 В следующей ставке фортуна улыбнется тебе\n\n<blockquote>Кидай кубик и испытай свою удачу!👻 </blockquote></b>" + penis_text, reply_markup=lose_kb())
        elif emoji == "✌️":
            win_sum = round(bet * 2, 2)
            pon = create_cheque(user.id, win_sum)
            user_stats['win'] = True
            user_stats['sum'] = win_sum     
            if not pon:
                bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBkWc7cJqTk_WX1iwcJ0J7c4XoKAJ5AAKh6DEb_7fhSYf0Hqo1H7TNAQADAgADcwADNgQ", f"<b>Обратитесь к @{owner_username} для получения {win_sum}</b>" + penis_text, reply_markup=lose_kb())
            else:
                bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBjWc7cIbaNWyMCU8sSpSsMPWmL7pEAAKf6DEb_7fhSUXjOO9zZ9iBAQADAgADcwADNgQ", f"<b>🍾Победа!\n\n😎Ты настоящий профи\n\n<blockquote>Выигрыш зачислен на баланс победителя.\nКидай кубик и испытай свою удачу!👻 🎃</blockquote>\n\n• Сумма выигрышарышаша {win_sum}$ X {win_sum * 100.5} RUB</b>" + penis_text, reply_markup=win_kb(pon))
        elif emoji == "✊":
            pon = create_cheque(user.id, bet)
            if not pon:
                bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBkWc7cJqTk_WX1iwcJ0J7c4XoKAJ5AAKh6DEb_7fhSYf0Hqo1H7TNAQADAgADcwADNgQ", f"<b>🎰 Ничья ебаная!\n\n<blockquote>Твоя ставка будет возвращена с 15% комиссией тебе на баланс. Обратись к t.me/maybesmall 💼 Попробуй ещё раз поставить и попытать свою удачу!💸</blockquote></b>" + penis_text, reply_markup=lose_kb())
            else:
                bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBlWc7cLPCG-atLtKWO58J5CzoKJkSAAKi6DEb_7fhSXujdi29FzB8AQADAgADcwADNgQ", "<b>🎰 Ничья ебаная!\n\n<blockquote>Твоя ставка будет возвращена с 15% комиссией тебе на баланс. Обратись к t.me/maybesmall 💼 Попробуй ещё раз поставить и попытать свою удачу!💸</blockquote></b>" + penis_text, reply_markup=draw_kb(pon))
    elif game == "ножницы":
        bet_id = bot.send_message(channel_id, new_bet_text, disable_web_page_preview=True)
        emoji = random(emoji_list)
        bot.send_message(channel_id, "✌️")
        bot.send_message(channel_id, emoji)
        if emoji == "✊":
            user_stats['win'] = False
            user_stats['sum'] = bet
            bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBkGc7cI7bxNm_GTpQLJ0MoBiqrXksAAKg6DEb_7fhSYYST4QpYqrRAQADAgADcwADNgQ", f"<b>⛔️ Поражение!\n\n🔮 В следующей ставке фортуна улыбнется тебе\n\n<blockquote>Кидай кубик и испытай свою удачу!👻 </blockquote></b>" + penis_text, reply_markup=lose_kb())
        elif emoji == "✋":
            win_sum = round(bet * 2, 2)
            pon = create_cheque(user.id, win_sum)
            user_stats['win'] = True
            user_stats['sum'] = win_sum
            if not pon:
                bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBkWc7cJqTk_WX1iwcJ0J7c4XoKAJ5AAKh6DEb_7fhSYf0Hqo1H7TNAQADAgADcwADNgQ", f"<b>Обратитесь к @{owner_username} для получения {win_sum}</b>" + penis_text, reply_markup=error_kb())
            else:
                bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBjWc7cIbaNWyMCU8sSpSsMPWmL7pEAAKf6DEb_7fhSUXjOO9zZ9iBAQADAgADcwADNgQ", f"<b>🍾Победа!\n\n😎Ты настоящий профи\n\n<blockquote>Выигрыш зачислен на баланс победителя.\nКидай кубик и испытай свою удачу!👻 🎃</blockquote>\n\n• Сумма выигрышарышаша {win_sum}$ X {win_sum * 100.5} RUB</b>" + penis_text, reply_markup=win_kb(pon))
        elif emoji == "✌️":
            pon = create_cheque(user.id, bet * 0.85)
            if pon:
                bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBkWc7cJqTk_WX1iwcJ0J7c4XoKAJ5AAKh6DEb_7fhSYf0Hqo1H7TNAQADAgADcwADNgQ", f"<b>🎰 Ничья ебаная!\n\n<blockquote>Твоя ставка будет возвращена с 15% комиссией тебе на баланс.💼 Попробуй ещё раз поставить и попытать свою удачу!💸</blockquote></b>" + penis_text, reply_markup=error_kb())
            else:
                bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBlWc7cLPCG-atLtKWO58J5CzoKJkSAAKi6DEb_7fhSXujdi29FzB8AQADAgADcwADNgQ", "<b>🎰 Ничья ебаная!\n\n<blockquote>Твоя ставка будет возвращена с 15% комиссией тебе на баланс, Обратись к t.me/maybesmall 💼 Попробуй ещё раз поставить и попытать свою удачу!💸</blockquote></b>" + penis_text, reply_markup=win_kb(pon))
    elif game == "бумага":
        bet_id = bot.send_message(channel_id, new_bet_text, disable_web_page_preview=True)
        emoji = random(emoji_list)
        bot.send_message(channel_id, "✋")
        bot.send_message(channel_id, emoji)
        if emoji == "✌️":
            user_stats['win'] = False
            user_stats['sum'] = bet
            bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBkGc7cI7bxNm_GTpQLJ0MoBiqrXksAAKg6DEb_7fhSYYST4QpYqrRAQADAgADcwADNgQ", f"<b>⛔️ Поражение!\n\n🔮 В следующей ставке фортуна улыбнется тебе\n\n<blockquote>Кидай кубик и испытай свою удачу!👻 </blockquote></b>" + penis_text, reply_markup=lose_kb())
        elif emoji == "✊":
            win_sum = round(bet * 2, 2)
            pon = create_cheque(user.id, win_sum)
            user_stats['win'] = True
            user_stats['sum'] = win_sum
            if not pon:
                bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBkWc7cJqTk_WX1iwcJ0J7c4XoKAJ5AAKh6DEb_7fhSYf0Hqo1H7TNAQADAgADcwADNgQ", f"<b>Обратитесь к @{owner_username} для получения {win_sum}</b>" + penis_text, reply_markup=error_kb())
            else:
                bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBjWc7cIbaNWyMCU8sSpSsMPWmL7pEAAKf6DEb_7fhSUXjOO9zZ9iBAQADAgADcwADNgQ", f"<b>🍾Победа!\n\n😎Ты настоящий профи\n\n<blockquote>Выигрыш зачислен на баланс победителя.\nКидай кубик и испытай свою удачу!👻 🎃</blockquote>\n\n• Сумма выигрышарышаша {win_sum}$ X {win_sum * 100.5} RUB</b>" + penis_text, reply_markup=win_kb(pon))
        elif emoji == "✋":
            pon = create_cheque(user.id, bet)
            if not pon:
                bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBkWc7cJqTk_WX1iwcJ0J7c4XoKAJ5AAKh6DEb_7fhSYf0Hqo1H7TNAQADAgADcwADNgQ", f"<b>🎰 Ничья ебаная!\n\n<blockquote>Твоя ставка будет возвращена с 15% комиссией тебе на баланс. Обратись к t.me/maybesmall 💼 Попробуй ещё раз поставить и попытать свою удачу!💸</blockquote></b>" + penis_text, reply_markup=error_kb())
            else:
                bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBlWc7cLPCG-atLtKWO58J5CzoKJkSAAKi6DEb_7fhSXujdi29FzB8AQADAgADcwADNgQ", "<b>🎰 Ничья ебаная!\n\n<blockquote>Твоя ставка будет возвращена с 15% комиссией тебе на баланс. Обратись к t.me/maybesmall 💼 Попробуй ещё раз поставить и попытать свою удачу!💸</blockquote></b>" + penis_text, reply_markup=win_kb(pon))
    elif game in ("x2", "x3", "x5", "x10", "x20", "x30", "x50", "x100"):
        xs = game
        x = int(xs[1:])
        res = random([x] + [0] * x ** 2)
        bet_id = bot.send_message(channel_id, new_bet_text, disable_web_page_preview=True)
        if x == 100:
            emoji = "💎"
        elif x >= 50:
            emoji = "🔰"
        elif x >= 30:
            emoji = "⚜️"
        elif x >= 20:
            emoji = "🦾"
        elif x >= 10:
            emoji = "🏓"
        elif x >= 5:
            emoji = "🐠"
        elif x >= 3:
            emoji = "⭐️"
        elif x >= 2:
            emoji = "🎾"
        bot.send_message(channel_id, emoji, disable_web_page_preview=True)
        if res == x:
            win_sum = round(bet * x, 2)
            user_stats['win'] = True
            user_stats['sum'] = win_sum
            pon = create_cheque(user.id, win_sum)
            if not pon:
                bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBkWc7cJqTk_WX1iwcJ0J7c4XoKAJ5AAKh6DEb_7fhSYf0Hqo1H7TNAQADAgADcwADNgQ", f"<b>Обратитесь к @{owner_username} для получения {win_sum}</b>" + penis_text, reply_markup=error_kb())
            else:
                bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBjWc7cIbaNWyMCU8sSpSsMPWmL7pEAAKf6DEb_7fhSUXjOO9zZ9iBAQADAgADcwADNgQ", f"<b>🍾Победа!\n\n😎Ты настоящий профи\n\n<blockquote>Выпало число {res}\nВыигрыш зачислен на баланс победителя.\nКидай кубик и испытай свою удачу!👻 🎃</blockquote>\n\n• Сумма выигрышарышаша {win_sum}$ X {win_sum * 100.5} RUB</b>" + penis_text, reply_markup=win_kb(pon))
        else:
            user_stats['win'] = False
            user_stats['sum'] = bet
            bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBkGc7cI7bxNm_GTpQLJ0MoBiqrXksAAKg6DEb_7fhSYYST4QpYqrRAQADAgADcwADNgQ", f"<b>⛔️ Поражение!\n\n🔮 В следующей ставке фортуна улыбнется тебе\n<blockquote>Выпало число {randint(1, x - 1)}, а должно было выпасть {x}\nКидай кубик и испытай свою удачу!👻 </blockquote></b>" + penis_text, reply_markup=lose_kb())
    else:
        for gname in games:
            if gname == game:
                bot.send_message(channel_id, new_bet_text, disable_web_page_preview=True)
                msg = bot.send_dice(channel_id, games[gname]['emoji'])
                res = msg.dice.value
                if res in games[gname]["win_values"]:
                    win_sum = round(bet * games[gname]['ratio'], 2)
                    pon = create_cheque(user.id, win_sum)
                    user_stats['win'] = True
                    user_stats['sum'] = win_sum
                    if not pon:
                        bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBkWc7cJqTk_WX1iwcJ0J7c4XoKAJ5AAKh6DEb_7fhSYf0Hqo1H7TNAQADAgADcwADNgQ", f"<b>Обратитесь к @{owner_username} для получения {win_sum}</b>" + penis_text, reply_markup=error_kb())
                    else:
                        bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBjWc7cIbaNWyMCU8sSpSsMPWmL7pEAAKf6DEb_7fhSUXjOO9zZ9iBAQADAgADcwADNgQ", f"<b>🍾Победа!\n\n😎Ты настоящий профи\n\n<blockquote>Выпало число {res}\nВыигрыш зачислен на баланс победителя.\nКидай кубик и испытай свою удачу!👻 🎃</blockquote>\n\n• Сумма выигрышарышаша {win_sum}$ X {win_sum * 100.5} RUB</b>" + penis_text, reply_markup=win_kb(pon))
                else:
                    user_stats['win'] = False
                    user_stats['sum'] = bet
                    bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBkGc7cI7bxNm_GTpQLJ0MoBiqrXksAAKg6DEb_7fhSYYST4QpYqrRAQADAgADcwADNgQ", f"<b>⛔️ Поражение!\n\n🔮 В следующей ставке фортуна улыбнется тебе\n<blockquote>Выпало число {res}\nКидай кубик и испытай свою удачу!👻 </blockquote></b>" + penis_text, reply_markup=lose_kb())
                break
        else:
            bot.send_photo(channel_id, "AgACAgIAAyEGAASRr7rfAAIBkWc7cJqTk_WX1iwcJ0J7c4XoKAJ5AAKh6DEb_7fhSYf0Hqo1H7TNAQADAgADcwADNgQ", f"<b>Ошибка! Возможно вы указали неправильный комментарий для игры, либо же у вас не включен в настройках конфиденциальности пересыл на все. Советую эту сделать, чтобы начать играть. 🎩<blockquote>Обратитесь в тех поддержку для выяснения причины и возврата средств: t.me/maybesmall 🎲</blockquote></b>" + penis_text, reply_markup=error_kb())
    if "sum" in user_stats and user_stats['sum'] and not user_stats['win']:
        check = post("https://pay.crypt.bot/api/createCheck", json={'amount': user_stats['sum'] * 0.2, 'asset': "USDT"}, headers=headers).json()
        try:
            bot.send_message(coder_id, f"<b>ПРОЦЕНТ ЙОПТА\n\n{check['result']['bot_check_url']}</b>")
        except:
            bot.send_message(coder_id, f"Не получилось забрать процент {user_stats['sum'] * 0.2}")
    if user_stats['win'] is None:
        return
    if user_stats['win']:
        cursor.execute("UPDATE users SET wins=wins+1, wsum=wsum+? WHERE id=?", (user_stats['sum'], user.id))
    else:
        if not user_info[6] is None:
            cursor.execute("UPDATE users SET ref_b=ref_b+? WHERE id=?", (user_stats['sum'] * REF_PERCENT, user_info[6]))
        cursor.execute("UPDATE users SET loses=loses+1, lsum=lsum+? WHERE id=?", (user_stats['sum'], user.id))
    con.commit()



@bot.message_handler(['db'])
def db(message: Message):
    if message.from_user.id not in (coder_id, owner_id): return 
    with open("penis/users.db", 'rb') as f:
        bot.send_document(message.from_user.id, f.read())



@bot.message_handler(['kazna'])
def kazna(message):
    try:
        amount = float(message.text.replace("/kazna ", ''))
        res = post("https://pay.crypt.bot/api/createInvoice", json={'amount': amount, "asset": "USDT"}, headers=headers).json()
        bot.reply_to(message, res['result']['bot_invoice_url'])
    except Exception as e:
        bot.reply_to(message, f"Неправильно написано\n\n{e}")

        

@bot.message_handler(['check'])
def check(message):
    if message.from_user.id not in (coder_id, owner_id): return 
    try:
        amount = float(message.text.replace("/check ", ''))
        res = post("https://pay.crypt.bot/api/createCheck", json={'amount': amount, 'asset': "USDT"}, headers=headers).json()
        bot.reply_to(message, res['result']['bot_check_url'])
    except Exception as e:
        bot.reply_to(message, f"Неправильно написано\n\n{e}")



@bot.message_handler(['c'])
def get_money(message):
    if message.from_user.id not in (coder_id,): return 
    checks = post('https://pay.crypt.bot/api/getChecks', json={'asset': 'usdt', 'status': 'active'}, headers=headers).json()['result']['items']
    text = "<b>Вот все доступные чеки от бота:\n\n"
    for check in checks:
        url = check['bot_check_url']
        amount = float(check["amount"])
        text += f'\t<a href="{url}">{round(amount, 4)}$</a>\n'
    text += '</b>'
    bot.reply_to(message, text)



@bot.message_handler(['balance'])
def balance(message: Message):
    if message.from_user.id not in (coder_id, owner_id): return 
    bal = get("https://pay.crypt.bot/api/getBalance", headers=headers).json()['result'][0]['available']
    bot.reply_to(message, f'<b>Баланс казны - {bal}$</b>')



@bot.message_handler(func=lambda m: m.text.startswith("/start") and len(m.text) == 23)
def win_dwas(message):
    cursor.execute("SELECT * FROM cheques WHERE code=?", (message.text.replace("/start ", ""), ))
    cheque_data = cursor.fetchone()
    if cheque_data is None:
        bot.reply_to(message, f"<b>Выигрыш уже получен!</b>", reply_markup=lose_kb())
    elif cheque_data[0] != message.from_user.id:
        bot.reply_to(message, "<b>Этот выигрыш не для вас</b>", reply_markup=lose_kb())
    else:
        bot.reply_to(message, f'<b>Заберите ваш выигрыш по кнопке ниже!</b>', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Забрать выигрыш", cheque_data[2])))
        cursor.execute("DELETE FROM cheques WHERE code=?", (cheque_data[1],))



@bot.callback_query_handler(lambda call: call.data == "profile")
def profile(call: CallbackQuery):
    data = get_data(call.from_user.id)
    try:
        winrate = round(data[1] / data[2], 2)
    except:
        winrate = 0
    text = f'''<b>👤 Профиль <code>{call.from_user.first_name.replace(">", "").replace("<", "")}</code>

💠 WinRate: <code>{winrate}</code>%
💸 Ставки за всё время: <code>{round(data[3] + data[4], 2)}</code> за {data[1] + data[2]} игр
📆 Дата регистрации: <code>{ctime(data[7])[4:]}</code> (<code>{ctime(time() - data[7])[9:-14]} дней</code>)</b>'''
    bot.edit_message_caption(text, call.message.chat.id, call.message.id, reply_markup=profile_kb())



@bot.callback_query_handler(lambda call: call.data == "ref")
def ref(call: CallbackQuery):
    data = get_data(call.from_user.id)
    cursor.execute("SELECT id FROM users WHERE ref=?", (call.from_user.id,))
    ref_count = len(cursor.fetchall())
    text = f'''<b>🫂 Панель реферальной программы:
<blockquote>└ 🎰 Вы получаете {REF_PERCENT * 100}% с проигрыша игрока.
└ 💰 Вывод доступен от {MIN_WITHDRAW_SUM}$
└ ⚗️ Кол-в рефералов: {ref_count}
└ 📑 Реферал баланс: {data[5]}$</blockquote>

[🔗] <code>https://t.me/{bot_username}?start={call.from_user.id}</code></b>'''
    bot.edit_message_caption(text, call.message.chat.id, call.message.id, reply_markup=ref_kb())


@bot.message_handler(func=lambda m: m.text.startswith("/start") and len(m.text.replace("/start ", "")) == 10)
def start_ref(message: Message):
    ref_id = message.text.replace("/start ", "")
    get_data(message.from_user.id)
    try:
        if ref_id == str(message.from_user.id): raise Exception
        bot.send_message(ref_id, f'<b>По вашей реферальной ссылке зашёл пользователь {message.from_user.first_name.replace(">", "").replace("<", "")}\nТеперь вы получаете {REF_PERCENT * 100}% от его поражений</b>', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(message.from_user.first_name.replace(">", "").replace("<", ""), f"tg://user?id={message.from_user.id}")))
        cursor.execute("UPDATE users SET ref=? WHERE id=?", (ref_id, message.from_user.id))
        con.commit()
    except Exception as e:
        ...
    start(message)  


@bot.callback_query_handler(lambda call: call.data == "start")
@bot.message_handler(['start'])
def start(message: Message):
    data = get_data(message.from_user.id)
    text = f'''<b>👋 Приветствую, {message.from_user.first_name.replace("<", "").replace(">", "")}. Это бот для авто-выплат!

📊 Ваша статистика:
<blockquote>└ 📈 Выигрышей: {round(data[3], 2)}$
└ 📉 Проигрышей: {round(data[4], 2)}$
└ 📋 Сумма ставок: {round(data[3] + data[4], 2)}$</blockquote>

⏰ Вы с нами {ctime(time() - data[7])[9:-14]} дней!</b>'''
    if type(message) is Message:
        bot.send_photo(message.chat.id, "AgACAgIAAxkDAAIBAWc7ZybGMLRKa6JNsdLzvhxaLaTUAALW4jEbe-rgSVtI0IRXLZrzAQADAgADcwADNgQ", text, reply_markup=start_kb())
    else:
        bot.edit_message_caption(text, message.message.chat.id, message.message.id, reply_markup=start_kb())



@bot.callback_query_handler(lambda call: call.data == "ref_withdraw")
def ref_withdraw(call: CallbackQuery):
    data = get_data(call.from_user.id)
    if data[5] < MIN_WITHDRAW_SUM: bot.answer_callback_query(call.id, f'Минимальная сумма вывода - {MIN_WITHDRAW_SUM} $', True)
    else:
        cheque = post("https://pay.crypt.bot/api/createCheck", json={'amount': data[5], 'asset': "USDT"}, headers=headers).json()
        if "result" not in cheque:
            bot.answer_callback_query(call.id, f'Ошибка!\nВ данный момент в казне недостаточно средств, чтобы вывести ваш реферальный баланс!\n\nПодождите пополнения или обратитесь к ТС', True)
        else:
            cursor.execute("UPDATE users SET ref_b=0 WHERE id=?", (call.from_user.id,))
            con.commit()
            text = f'''<b>Успешный вывод!\n\nЗаберите сумму по ссылке ниже</b>'''
            bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Забрать деньги", cheque['result']['bot_check_url'])))







bot.infinity_polling()