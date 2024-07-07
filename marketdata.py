import requests
import itertools
import time
from urllib.parse import quote

# Function to fetch proxies from the provided API
def fetch_proxies_from_api():
    url = "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc"
    try:
        response = requests.get(url)
        response.raise_for_status()
        proxy_data = response.json()["data"]
        http_proxies = [
            f"{proxy['ip']}:{proxy['port']}"
            for proxy in proxy_data
            if "http" in proxy["protocols"]
        ]
        return http_proxies
    except requests.RequestException as e:
        print(f"Failed to fetch proxies from API: {e}")
        return []

# Fetch the proxies from the API
dynamic_proxies = fetch_proxies_from_api()

# Provided proxies list (static proxies)
static_proxies = [
    "35.185.196.38:3128"
    # Add more static proxies here if needed
]

# Combine static and dynamic proxies
all_proxies = static_proxies + dynamic_proxies

# Create an iterator for round-robin proxy selection
proxy_iterator = itertools.cycle(all_proxies)

# Function to get the next proxy in the list
def get_next_proxy():
    return next(proxy_iterator)

def get_hashname(item, skin, wear, stat):
    if stat == 1:
        item = "StatTrak™ " + item
    wear_dict = {1: " (Factory New)", 2: " (Minimal Wear)", 3: " (Field-Tested)", 4: " (Well-Worn)", 5: " (Battle-Scarred)"}
    wear = wear_dict[wear]
    hashname = f"{item} | {skin}{wear}"
    return hashname

def get_nameid(hashname, max_retries=10):
    for _ in range(max_retries):
        proxy = get_next_proxy()
        proxy_dict = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}",
        }
        url = f"https://steamcommunity.com/market/listings/730/{quote(hashname)}"
        print(f"Trying URL: {url} with proxy: {proxy}")
        try:
            response = requests.get(url, proxies=proxy_dict, timeout=10)
            response.raise_for_status()  # Raise an exception for HTTP errors
            html = response.text
            print(f"Response HTML: {html[:1000]}")  # Log first 1000 characters of the response for debugging
            if 'Market_LoadOrderSpread(' in html:
                nameid = html.split('Market_LoadOrderSpread( ')[1].split(' ')[0]
                if nameid.isdigit():
                    return int(nameid)
                else:
                    print(f"Failed to extract valid nameid for URL: {url}")
            else:
                print(f"Failed to find 'Market_LoadOrderSpread(' in the response for URL: {url}")
            time.sleep(2)  # Add delay between retries
        except requests.RequestException as e:
            print(f"Proxy {proxy} failed with error: {e}")
            time.sleep(2)  # Add delay between retries
    raise Exception("All proxies failed to fetch nameid")

def item_data(hashname, max_retries=10):
    nameid = str(get_nameid(hashname, max_retries))
    out = {}
    for _ in range(max_retries):
        proxy = get_next_proxy()
        proxy_dict = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}",
        }
        url = f"https://steamcommunity.com/market/itemordershistogram?country=US&currency=1&language=english&two_factor=0&item_nameid={nameid}"
        print(f"Trying URL: {url} with proxy: {proxy}")
        try:
            response = requests.get(url, proxies=proxy_dict, timeout=10)
            response.raise_for_status()
            order_data = response.json()  # Parse as JSON
            print(f"Order Data Response: {order_data}")  # Debugging

            buy_req = order_data.get("highest_buy_order", None)
            sell_req = order_data.get("lowest_sell_order", None)

            if buy_req is not None and sell_req is not None:
                out["buy_req"] = int(buy_req) / 100
                out["sell_req"] = int(sell_req) / 100
            else:
                print(f"Failed to parse buy or sell order data for URL: {url}")
                continue

            try:
                volume_url = f"https://steamcommunity.com/market/priceoverview/?appid=730&currency=1&market_hash_name={quote(hashname)}"
                print(f"Trying URL: {volume_url} with proxy: {proxy}")
                volume_response = requests.get(volume_url, proxies=proxy_dict, timeout=10)
                volume_response.raise_for_status()
                volume_data = volume_response.json()  # Parse as JSON
                print(f"Volume Data Response: {volume_data}")  # Debugging

                volume = volume_data.get("volume", None)
                if volume is not None and volume.isdigit():
                    out["volume"] = int(volume)
                else:
                    out["volume"] = 0
            except Exception as e:
                print(f"Failed to get volume data with proxy {proxy}: {e}")
                out["volume"] = 0

            out["nameid"] = nameid
            return out
        except requests.RequestException as e:
            print(f"Proxy {proxy} failed with error: {e}")
            time.sleep(2)  # Add delay between retries
    raise Exception("All proxies failed to fetch item data")

# Test the URL construction and data fetching
if __name__ == "__main__":
    gun = "AK-47"
    skin = "Redline"
    wear = 3  # Field-Tested
    stat = 1  # StatTrak™

    hashname = get_hashname(gun, skin, wear, stat)
    url = f"https://steamcommunity.com/market/listings/730/{quote(hashname)}"
    print(f"Constructed URL: {url}")

    try:
        data = item_data(hashname)
        print(f"Item Data: {data}")
    except Exception as e:
        print(f"Error: {e}")
