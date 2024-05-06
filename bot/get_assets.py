import requests


def get_assets_crypto_info(symbols):
    api_key = 'b5d47d68bd0fe395386c5c725e6fe0d88ef59bd7e8249be5e57f519b4130f068'
    symbols_str = ','.join(symbols)
    url = f'https://min-api.cryptocompare.com/data/pricemultifull?fsyms={symbols_str}&tsyms=USD&api_key={api_key}'

    try:
        response = requests.get(url)
        data = response.json()

        crypto_assets_list = []

        for symbol in symbols:
            if 'RAW' in data and symbol in data['RAW']:
                crypto_assets = data['RAW'][symbol]['USD']
                name = crypto_assets['FROMSYMBOL']
                current_price = crypto_assets['PRICE']
                price_change_24h = crypto_assets['CHANGEPCT24HOUR']
                image_url = f'https://www.cryptocompare.com{crypto_assets["IMAGEURL"]}'

                crypto_assets_list.append({
                    'name': name,
                    'symbol': symbol,
                    'current_price': current_price,
                    'price_change_24h': price_change_24h,
                })

            else:
                print(f"Invalid response structure or symbol not found: {symbol}")

        print(crypto_assets_list)
        return crypto_assets_list

    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        return None


def get_assets_list_crypto_info(symbols):
    if isinstance(symbols, str):
        symbols = [symbols]

    api_key = 'b5d47d68bd0fe395386c5c725e6fe0d88ef59bd7e8249be5e57f519b4130f068'
    symbols_str = ','.join(symbols)
    url = f'https://min-api.cryptocompare.com/data/pricemultifull?fsyms={symbols_str}&tsyms=USD&api_key={api_key}'

    try:
        response = requests.get(url)
        data = response.json()

        crypto_assets_list = []

        for symbol in symbols:
            if 'RAW' in data and symbol in data['RAW']:
                crypto_assets = data['RAW'][symbol]['USD']
                name = crypto_assets['FROMSYMBOL']
                current_price = crypto_assets['PRICE']
                price_change_24h = crypto_assets['CHANGEPCT24HOUR']
                image_url = f'https://www.cryptocompare.com{crypto_assets["IMAGEURL"]}'

                crypto_assets_list.append({
                    'name': name,
                    'symbol': symbol,
                    'current_price': current_price,
                    'price_change_24h': price_change_24h,
                })

            else:
                print(f"Invalid response structure or symbol not found: {symbol}")

        return crypto_assets_list

    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        return None


def get_trendings_coin():
    API_KEY = '3d99cb06-b5fb-4481-85c4-0990e76d8762'
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': '1',
        'limit': '5',
        'convert': 'USD',
        'sort': 'percent_change_24h',
    }

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY,
    }

    response = requests.get(url, headers=headers, params=parameters)

    if response.status_code == 200:
        data = response.json()['data']
        last_coins = []
        for coin in data:
            last_coins.append({
                "name": coin['name'],
                "symbol": coin['symbol'],
                "change24h": coin['quote']['USD']['percent_change_24h']
            })
        return last_coins
    else:
        print("Ошибка при выполнении запроса:", response.status_code)