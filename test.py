from urllib.parse import quote

def get_hashname(item, skin, wear, stat):
    item = quote(item)
    skin = quote(skin)
    wear_dict = {1: " (Factory New)", 2: " (Minimal Wear)", 3: " (Field-Tested)", 4: " (Well-Worn)", 5: " (Battle-Scarred)"}
    wear = quote(wear_dict[wear])
    if stat == 1:
        item = "StatTrak%E2%84%A2 " + item
    hashname = f"{item} | {skin}{wear}"
    return hashname

# Example parameters
gun = "AK-47"
skin = "Redline"
wear = 3  # Field-Tested
stat = 1  # StatTrak™

# Get the hashname
hashname = get_hashname(gun, skin, wear, stat)
print(f"Constructed hashname: {hashname}")

# Construct the full URL
url = f"https://steamcommunity.com/market/listings/730/{hashname}"
print(f"Constructed URL: {url}")
