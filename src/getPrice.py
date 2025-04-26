from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from pybit.unified_trading import HTTP

import json
import os
import datetime
from datetime import timezone

headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': os.environ['CMCKEY'],
}

def make_request(session, url, parameters):
    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        return data
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

def get_price_cmc():
    global CREDITS
    url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    parameters = {
      'id' : '5426'
    }
    data = make_request(url, parameters)
    CREDITS -= data['status']['credit_count']
    print(f'CMC credits left: {CREDITS}.')
    return data['data']['5426']['quote']['USD']['price']

def get_price_bybit(symbol='SOLUSDT'):
    dt = datetime.datetime.now(timezone.utc)
    dt = datetime.datetime(
        year=dt.year,
        month=dt.month,
        day=dt.day,
        hour=dt.hour,
        minute=dt.minute
    )
    b = dt.replace(tzinfo=timezone.utc).timestamp()
    b = int(b)
    b *= 1000
    r = session.get_kline(
        category="spot",
        symbol=symbol,
        interval=1,
        start=b,
        end=b,
    )
    print(r)
    last_price = r['result']['list'][0][4]
    print(f'{dt} price: {last_price}')
    return float(last_price)


api_key = os.environ['BBKEY']
api_secret = os.environ['BBSEC']

session = HTTP(
    testnet=False,
    api_key=api_key,
    api_secret=api_secret,
)

# session = Session()
# session.headers.update(headers)

# url = 'https://pro-api.coinmarketcap.com/v1/key/info'
# data = make_request(url, {})
# CREDITS = data['data']['usage']['current_month']['credits_left']
