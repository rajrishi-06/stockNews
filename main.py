import requests
import datetime
from twilio.rest import Client

TWILLIO_ACC_SID="YOUR TWILIO ACCOUNT SID"
TWILLIO_AUTH_TOKEN="YOUR TWILIO AUTH TOKEN"
TWILLO_VERIFIED_NUMBER="your own phone number verified with Twilio"
TWILLIO_VIRTUAL_NUMBER="your virtual twilio number"

STOCK = "TSLA"
COMPANY_NAME=("Tesla Inc")

STOCK_API_KEY= "YOUR OWN API KEY FROM ALPHAVANTAGE"
NEWS_API_KEY="YOUR OWN API KEY FROM NEWSAPI"
STOCK_API="https://www.alphavantage.co/query?"


NEWS_END = "https://newsapi.org/v2/everything"
stock_parameters = {
    "function" : "TIME_SERIES_DAILY" ,
    "symbol" : STOCK ,#"RELIANCE.BSE" ,
    "outputsize" : "compact" ,
    "apikey" : STOCK_API_KEY
}

def get_last_four_days():
    today_date = datetime.date.today()
    last_days = [(today_date - datetime.timedelta(days=i)) for i in range(1, 6)]

    return last_days
last_four_days = get_last_four_days()
yesterday = last_four_days[0]
news_parameters = {
    "q" : COMPANY_NAME ,
    "from" : yesterday ,
    # "searchIn" : "title ,description" ,
    "language" : "en" ,
    "sortBy" : "popularity",
    "apikey" : NEWS_API_KEY
}

stock_response = requests.get("https://www.alphavantage.co/query?" ,params=stock_parameters)
stock_response.raise_for_status()

now = datetime.datetime.now()
today = str(now.date()).split('-')
last_four_days = get_last_four_days()
prices = []
for date in last_four_days:
    try:
        price = float(stock_response.json()["Time Series (Daily)"][f"{str(date)}"]["4. close"])
    except KeyError:
        print("close")
        continue
    else:
        prices.append(price)
    finally:
        print(date)

yesterday_price = prices[0]
day_before_yesterday_price = prices[1]

price_diff = round( abs(yesterday_price - day_before_yesterday_price) / yesterday_price * 100, 2)
if not yesterday_price < day_before_yesterday_price:
    symbol = "🔺"
else:
    symbol = "🔻"
if price_diff > 1:
    news_response = requests.get(url=NEWS_END ,params=news_parameters)
    news_response.raise_for_status()
    news_data = news_response.json()
    news_printed = 0
    counter = 0
    while news_printed < 3:
        try:
            if news_data["articles"][counter]["title"] == "[Removed]":
                raise KeyError
        except KeyError:
            continue
        else:
            client = Client(TWILLIO_ACC_SID, TWILLIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f"{STOCK}: {symbol}{price_diff}\n"
                     f"HeadLine:{news_data["articles"][counter]["title"]}\n"
                     f"Brief:{news_data["articles"][counter]["description"]}",
                from_=TWILLIO_VIRTUAL_NUMBER,
                to=TWILLO_VERIFIED_NUMBER,
            )
            print(f"{STOCK}: {symbol}{price_diff}\n"
            f"HeadLine:{news_data["articles"][counter]["title"]}\n"
            f"Brief:{news_data["articles"][counter]["description"]}")
            news_printed += 1
        finally:
            counter += 1
