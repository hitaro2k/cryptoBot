import sqlite3
from bot.get_assets import get_assets_crypto_info , get_trendings_coin , get_assets_list_crypto_info
from PIL import Image, ImageDraw, ImageFont
import re
from telebot import types
from bot.connection import bot


def main_functionality(message):
    markup = types.ReplyKeyboardMarkup()
    findBtn = types.KeyboardButton('Finding a coin')
    walletBtn = types.KeyboardButton('Go to wallet menu')
    trendingCoin = types.KeyboardButton('See trending coins')
    markup.add(findBtn ,walletBtn ,  trendingCoin)
    bot.send_message(message.chat.id, "Your in main menu", reply_markup=markup)


coin_names = []
coin_price = []


def generated_images(balance , name , price):
    template_path = "img/s.jpg"
    template = Image.open(template_path)

    draw = ImageDraw.Draw(template)

    font = ImageFont.truetype("arial.ttf", 25)

    balance_pos = (175, 195)
    text = balance
    draw.text(balance_pos, text, fill=(255, 255, 255), font=font)
    start_position = (25,150)
    text_step = 50  
    coin_names.append(name)
    coin_price.append(price)
    texts = [f"{name} : {price}" for name, price in zip(coin_names, coin_price)]
    for i, text in enumerate(texts):
        position = (start_position[0], start_position[1] + (i + 1) * text_step + 50)
        draw.text(position, text, fill=(255, 255, 255), font=font)

    template.save("img/output_image.jpg")


def create_connection():
    return sqlite3.connect("db/crypto_info.db")


def fetch_transactions(user_id):
    conn = sqlite3.connect('db/crypto_info.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_coin, user_percoin_price, user_coin_count  "
                   "FROM transactions WHERE user_id=?", (user_id,))
    transactions = cursor.fetchall()
    conn.close()
    return transactions


def calculate_total_value(transactions):
    coin_totals = {}
    for transaction in transactions:
        user_coin, user_percoin_price, user_coin_count = transaction
        if user_coin not in coin_totals:
            coin_totals[user_coin] = 0
        coin_totals[user_coin] += user_percoin_price * user_coin_count
    return coin_totals


def calculate_total_balance(transactions):
    resDict = {}
    totalBalance = 0

    for coin_name, price, count in transactions:
        coin_name = coin_name.upper()
        totalBalance += price * count

        if coin_name in resDict:
            resDict[coin_name] = (resDict[coin_name][0], resDict[coin_name][1] + count)
        else:
            resDict[coin_name] = (price, count)

    for coin_name, (price, count) in resDict.items():
        static_price = get_assets_list_crypto_info(coin_name)
        if static_price:
            resDict[coin_name] = (round(static_price[0]['current_price'] , 1) , count)  

    totalBalance = sum(price * count for price, count in resDict.values())
    return totalBalance
    

def create_users_db():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id VARCHAR)''')
    conn.commit()
    cursor.close()
    conn.close()


def create_transaction_db():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions
                       (user_id VARCHAR,
                        user_coin VARCHAR,
                        user_percoin_price FLOAT,
                        user_coin_count FLOAT)''')
    conn.commit()
    cursor.close()
    conn.close()


def is_transaction_table_empty():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return len(rows) == 0


create_transaction_db()
create_users_db()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🦝 Hello this free bot for adding your crypto wallet and monitoring cryptocurrencies")
    markup = types.ReplyKeyboardMarkup()
    asUserBtn = types.KeyboardButton('As User')
    markup.add(asUserBtn)
    asGuestBtn = types.KeyboardButton('As Guest')
    markup.add(asGuestBtn)
    bot.send_message(message.chat.id, "🦝 Please logining or use as guest", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'As User')
def handle_logining(message):
    markup = types.ReplyKeyboardMarkup()
    loginingBtn = types.KeyboardButton('Logining')
    loginMenuBtn = types.KeyboardButton('Login menu')
    markup.add(loginingBtn , loginMenuBtn)

    bot.send_message(message.chat.id ,"Your in system ,pls logining", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'As Guest')
def handle_guest(message):
    markup = types.ReplyKeyboardMarkup()
    findBtn = types.KeyboardButton('Finding a coin')
    markup.add(findBtn)
    addWallet = types.KeyboardButton('Register')
    markup.add(addWallet)
    trendingCoin = types.KeyboardButton('See trending coins')
    markup.add(trendingCoin)
    bot.send_message(message.chat.id, "Your in guest system", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Login menu')
def main_menu(message):
    markup = types.ReplyKeyboardMarkup()
    asUserBtn = types.KeyboardButton('As User')
    markup.add(asUserBtn)
    asGuestBtn = types.KeyboardButton('As Guest')
    markup.add(asGuestBtn)
    bot.send_message(message.chat.id, "Your in main menu", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Main menu')
def main_menu(message):
    main_functionality(message)


@bot.message_handler(func=lambda message: message.text == 'Logining')
def handle_logining(message):
    conn = create_connection()
    cursor = conn.cursor()
    user_id = message.chat.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    existing_user = cursor.fetchone()
    if existing_user is None:
        markup = types.ReplyKeyboardMarkup()
        regMarkup = types.KeyboardButton("Register")
        markup.add(regMarkup)
        bot.send_message(message.chat.id, "Your not registered user ,pls register", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Success Logining')
        main_functionality(message)

    cursor.close()
    conn.close()


@bot.message_handler(func=lambda message: message.text == 'Register')
def handle_register(message):
    conn = create_connection()
    cursor = conn.cursor()
    user_id = message.chat.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    existing_user = cursor.fetchone()
    if existing_user is None:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        bot.send_message(message.chat.id, 'Register successfully!')
        main_functionality(message)

    else:
        bot.send_message(message.chat.id, 'Already registered!')
        main_functionality(message)

    cursor.close()
    conn.close()


@bot.message_handler(func=lambda message: message.text == 'See trending coins')
def handle_trending_coin(message):
    trending_coins = get_trendings_coin()
    if trending_coins:
        for coin in trending_coins:
            coin_info = f"{coin['name']}( {coin['symbol']}) , Change 24h: {round(coin['change24h'] , 1)}"
            bot.send_message(message.chat.id, coin_info)
    else:
        bot.send_message(message.chat.id, "Ошибка при получении трендовых монет")


@bot.message_handler(func=lambda message: message.text == "Finding a coin")
def handle_coin_search(message):
    bot.send_message(message.chat.id, "Please enter the tag of the coin you want to find")
    bot.register_next_step_handler(message, process_coin_step)


def process_coin_step(message):
    coin_tag = message.text
    crypto_info = get_assets_crypto_info([coin_tag.upper()])
    if crypto_info:
        for crypto in crypto_info:
            response_message = f"Name:{crypto['name']}\nPrice:{round(crypto['current_price'], 1)}\nPrice Change:{round(crypto['price_change_24h'], 1)}"
            bot.send_message(message.chat.id, response_message)
            break  
    else:
        bot.send_message(message.chat.id, "🦝 Something went wrong while fetching crypto info. Please try again later.")
    main_functionality(message)



# --------------------- WALLET ---------------------
@bot.message_handler(func=lambda message: message.text == "Go to wallet menu")
def handle_wallet_menu_selection(message):
    global searching_coin
    searching_coin = False 
    markup = types.ReplyKeyboardMarkup()
    walletBtn = types.KeyboardButton('My wallet')
    addCoinBtn = types.KeyboardButton('Add coin to wallet')
    sellCoinBtn = types.KeyboardButton('Sell coin in wallet')
    mainMenuBtn = types.KeyboardButton('Main menu')
    markup.add(addCoinBtn,sellCoinBtn , walletBtn, mainMenuBtn )
    bot.send_message(message.chat.id, "Your in wallet menu", reply_markup=markup)


@bot.message_handler(func=lambda message:message.text == "My wallet")
def handle_watch_wallet(message):
    user_id = message.chat.id
    transactions = fetch_transactions(user_id)
    coin_totals = calculate_total_value(transactions)
    balance = calculate_total_balance(transactions)
    if is_transaction_table_empty():
         message_text = f"Total Balance: 0 USDT\n"
         bot.send_message(message.chat.id ,message_text)
    else:
        for coin, total_value in coin_totals.items():
            strBal = str(balance)
            strCoin = str(coin)
            strTotal = str(total_value)
            generated_images(strBal , strCoin , strTotal)    
        photo = open("img/output_image.jpg", 'rb')
        bot.send_photo(message.chat.id , photo)


@bot.message_handler(func=lambda message: message.text == 'Add coin to wallet')
def handle_coin_selection(message):
    # markup = types.ReplyKeyboardMarkup()
    # abortBtn = types.KeyboardButton('Abort')
    # markup.add(abortBtn)

    bot.send_message(message.chat.id, "Select the tag of the coin you want to sell")
    bot.register_next_step_handler(message, add_coin)


def add_coin(message):
    try:  
        coin_name = message.text.upper()
        if not re.search(r'\d', coin_name):
            bot.send_message(message.chat.id, "Price:")
            bot.register_next_step_handler(message, lambda msg: add_price(msg, coin_name))
        else:
            raise ValueError("coin_name contains digits")
    except Exception as e:
        bot.send_message(message.chat.id, "Your set not tag, reset tag")
        bot.register_next_step_handler(message, add_coin)


def add_price(message, coin_name):
    try:
        price = float(message.text)
        bot.send_message(message.chat.id, "Quantity:")
        bot.register_next_step_handler(message, lambda msg: add_quantity(msg, coin_name, price))
        
    except:
        bot.send_message(message.chat.id, "Your set not number, select the tag of the coin you want to add")
        bot.register_next_step_handler(message,  add_coin)


def add_quantity(message, coin_name, price):
    try:
        quantity = float(message.text)
        conn = create_connection()
        cursor = conn.cursor()
        user_id = message.chat.id
        cursor.execute("INSERT INTO transactions (user_id , user_coin, user_percoin_price, user_coin_count) VALUES (?, ?, ? , ?)", (user_id, coin_name, price , quantity))
        conn.commit()
        bot.send_message(message.chat.id, f"Coin '{coin_name}' at {price} has been successfully added to your wallet.")
    except:
        bot.send_message(message.chat.id, "Your set not number, select quantity")
        bot.register_next_step_handler(message, lambda msg: add_quantity(msg, coin_name, price))
  

@bot.message_handler(func=lambda message: message.text == 'Sell coin in wallet')
def handle_coin_selection(message):
    bot.send_message(message.chat.id, "Select the tag of the coin you want to sell")
    bot.register_next_step_handler(message, sell_coin)


def sell_coin(message):
    try:  
        coin_name = message.text.upper()
        if not re.search(r'\d', coin_name):
            bot.send_message(message.chat.id, "Price:")
            bot.register_next_step_handler(message, lambda msg: sell_price(msg, coin_name))
        else:
            raise ValueError("coin_name contains digits")
    except Exception as e:
        bot.send_message(message.chat.id, "Your set not tag, reset tag")
        bot.register_next_step_handler(message, sell_coin)


def sell_price(message, coin_name):
    try:
        price = -float(message.text)
        bot.send_message(message.chat.id, "Quantity:")
        bot.register_next_step_handler(message, lambda msg: sell_quantity(msg, coin_name, price))
        
    except:
        bot.send_message(message.chat.id, "Your set not number, select the tag of the coin you want to sell")
        bot.register_next_step_handler(message, sell_coin)
    

def sell_quantity(message, coin_name, price):
    try:
        quantity = float(message.text)
        conn = create_connection()
        cursor = conn.cursor()
        user_id = message.chat.id
        cursor.execute("INSERT INTO transactions (user_id , user_coin, user_percoin_price, user_coin_count) VALUES (?, ?, ? , ?)", (user_id, coin_name, price , quantity))
        conn.commit()
        bot.send_message(message.chat.id, f"Coin '{coin_name}' at {price} was successfully sold from your wallet.")
    except:
        bot.send_message(message.chat.id, "Your set not number, select quantity")
        bot.register_next_step_handler(message, lambda msg: sell_quantity(msg, coin_name, price))
 

@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    bot.send_message(message.chat.id, "Sorry, I don't understand your message. Please use /help for help.")



