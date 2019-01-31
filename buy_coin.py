"""SETTINGS"""

# Quantity to buy at
bitcoin_buy_quantity = 0.001

volitality_threshold = 1.2

# Change this to True if you want to sell manually from the program.
# If this is set, we'll give you a hint where to sell at based on your sell_order_multiplier
# so you can sell quicker
manual_sell = True

# Sell order will be placed at <price> * <sell_order_multiplier>
# meaning that if it is set to 2, it will sell at 100% gains, if at 1.5, it will sell at 50%.
sell_order_multiplier = 2


# Should have trade permissions
# Create bittrex auth at https://bittrex.com/Manage#sectionApi
# Make sure you place the authentication fields within the quotation marks!
class BittrexAuth:
    api_key = ""
    api_secret = ""


"""SETTINGS DONE, GOOD LUCK!"""

try:
    assert (len(BittrexAuth.api_key) > 0)
    assert (len(BittrexAuth.api_secret) > 0)
except:
    print("Please fill in the Bittrex Authentication fields.")
try:
    import sys
    import os
    from time import time
    import hashlib
    import hmac

    if sys.version_info >= (3, 0):
        sys.stdout.write("Sorry, requires Python 2.7.14, not Python 3.x\n")
        input("Press any key to continue...")
        sys.exit(1)

    if manual_sell == 'false' or manual_sell == 'False':
        manual_sell = False

    parent_dir = os.path.abspath(os.path.dirname(__file__))
    vendor_dir = os.path.join(parent_dir, 'vendored')
    sys.path.append(vendor_dir)

    import requests

    if __name__ == "__main__":
        print("Beginning to run...")
        coin = raw_input("Input coin abbreviation to run (ex: eth): ").upper()
        nonce = str(int(time() * 1000))

        market = "BTC-{coin}".format(coin=coin)
        response = requests.get("https://bittrex.com/api/v1.1/public/getticker", params={"market": market})
        coin_data = response.json()

        bid_price = coin_data['result']['Ask']
        adjusted_price = bid_price * volitality_threshold
        buy_qty = str(bitcoin_buy_quantity / adjusted_price)
        adjusted_price = str(adjusted_price)

        uri = "https://bittrex.com/api/v1.1/market/buylimit?" + "apikey=" + BittrexAuth.api_key + "&nonce=" + nonce + "&market=" + market \
              + "&quantity=" + buy_qty + "&rate=" + adjusted_price

        apisign = hmac.new(BittrexAuth.api_secret.encode(), uri.encode(), hashlib.sha512).hexdigest()
        response = requests.get(uri, headers={"apisign": apisign})
        response_data = response.json()
        print(response_data)
        if response_data['success'] is True:
            print("SUCCESSFULLY BOUGHT {0} AT APPROXIMATELY {1}".format(market, bid_price))

        price = bid_price
        nonce = str(int(time() * 1000))

        market = "BTC-{coin}".format(coin=coin)
        uri = "https://bittrex.com/api/v1.1/account/getbalance?" + "apikey=" + BittrexAuth.api_key + "&nonce=" + nonce + "&currency=" + coin
        apisign = hmac.new(BittrexAuth.api_secret.encode(), uri.encode(), hashlib.sha512).hexdigest()
        response = requests.get(uri, headers={"apisign": apisign})
        j = response.json()
        available_funds = str(j['result']['Available'])

        if manual_sell:
            price = raw_input(
                "Input price to sell at (HINT: {0} is multiplied by {1} from price): ".format(
                    price * sell_order_multiplier,
                    sell_order_multiplier)
            )

        uri = "https://bittrex.com/api/v1.1/market/selllimit?" + "apikey=" + BittrexAuth.api_key + "&nonce=" + nonce + "&market=" + market \
              + "&quantity=" + str(available_funds) + "&rate=" + str(price)
        apisign = hmac.new(BittrexAuth.api_secret.encode(), uri.encode(), hashlib.sha512).hexdigest()
        response = requests.get(uri, headers={"apisign": apisign})
        response_data = response.json()
        print(response_data)
        if response_data['success'] is True:
            print("SET A SELL ORDER FOR {0} AT APPROXIMATELY {1}".format(market, price))
except:
    import traceback

    traceback.print_exc()
finally:
    raw_input("Press any key to continue...")
