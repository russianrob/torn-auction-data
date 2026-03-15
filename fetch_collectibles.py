#!/usr/bin/env python3
"""
Fetch collectible auction house data from Torn API v2 and append to CSV.
Run daily via GitHub Actions cron.
"""

import csv
import json
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse

API_KEY = os.environ.get("TORN_API_KEY", "")
BASE_URL = "https://api.torn.com/v2/market"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CSV_FILE = os.path.join(DATA_DIR, "collectible-auctions.csv")

# Torn collectible item IDs and names (280 items)
# Source: Torn API v2 GET /v2/torn/items?cat=Collectible — verified 2026-03-14
COLLECTIBLE_IDS = {
    74: "Santa Hat '04",
    75: "Christmas Cracker '04",
    102: "Chocolate Egg '05",
    112: "Test Trophy",
    113: "Pet Rock",
    114: "Non-Anon Doll",
    115: "Poker Doll",
    116: "Yoda Figurine",
    117: "Trojan Horse",
    118: "Doll's Head",
    119: "Rubber Ducky of Doom",
    120: "Teppic Bear",
    121: "RockerHead Doll",
    122: "Mouser Doll",
    123: "Elite Action Man",
    124: "Toy Reactor",
    125: "Royal Doll",
    126: "Blue Dragon",
    127: "China Tea Set",
    128: "Mufasa Toy",
    130: "Skanky Doll",
    131: "Lego Hurin",
    132: "Mystical Sphere",
    133: "10 Ton Pacifier",
    134: "Horse Toy",
    135: "Uriel's Speakers",
    136: "Strife Clown",
    137: "Locked Teddy",
    138: "Riddle's Bat",
    139: "Soup Nazi Doll",
    140: "Pouncer Doll",
    141: "Spammer Doll",
    142: "Cookie Jar",
    143: "Vanity Mirror",
    144: "Banana Phone",
    148: "Dance Toy",
    149: "Lucky Dime",
    150: "Crystal Carousel",
    152: "Ice Sculpture",
    153: "Case of Whiskey",
    155: "Purple Frog",
    156: "Hooorang's Key",
    157: "Patriot Whip",
    158: "Statue Of Aeolus",
    161: "Black Unicorn",
    162: "WarPaint Kit",
    163: "Official Ninja Kit",
    164: "Leukaemia Teddy Bear",
    165: "Chocobo Flute",
    166: "Annoying Man",
    169: "Barbie Doll",
    171: "Jack-O-Lantern '05",
    179: "Birthday Cake '05",
    185: "Bunch of Balloons '05",
    188: "Cracked Crystal Ball",
    192: "Rainbow Stud Earring",
    193: "Hamster Toy",
    194: "Snowflake '05",
    195: "Christmas Tree '05",
    202: "Mr Torn Crown '07",
    207: "Ms Torn Crown '07",
    211: "Crazy Cow",
    212: "Legend's Urn",
    213: "Dreamcatcher",
    214: "Brutus Keychain",
    216: "Single White Rose",
    284: "Bronze Paint Brush",
    285: "Silver Paint Brush",
    286: "Gold Paint Brush",
    287: "Pand0ra's Box",
    288: "Mr Brownstone Doll",
    297: "YouYou Yo Yo",
    298: "Monkey Cuffs",
    299: "Jester's Cap",
    300: "Gibal's Dragonfly",
    301: "Green Ornament",
    302: "Purple Ornament",
    303: "Blue Ornament",
    304: "Purple Bell",
    311: "Mardi Gras Beads",
    312: "Devil Toy",
    313: "Cookie Launcher",
    314: "Cursed Moon Pendant",
    338: "Sh0rty's Surfboard",
    339: "Puzzle Piece",
    340: "Hunny Pot",
    341: "Seductive Stethoscope",
    342: "Dollar Bill",
    343: "Backstage Pass",
    344: "Chemi's Magic Potion",
    349: "Flea Collar",
    350: "Dunkin's Donut",
    351: "Amazon Doll",
    352: "BBQ Smoker",
    353: "Bag of Cheetos",
    354: "Motorbike",
    355: "Citrus Squeezer",
    356: "Superman Shades",
    357: "Kevlar Helmet",
    362: "Mr Torn Crown '08",
    363: "Ms Torn Crown '08",
    371: "Dark Doll",
    389: "Mr Torn Crown '09",
    390: "Ms Torn Crown '09",
    423: "Poker Chip",
    424: "Rabbit Foot",
    425: "Voodoo Doll",
    441: "Khinkeh P0rnStar Doll",
    442: "Blow-Up Doll",
    443: "Strawberry Milkshake",
    444: "Breadfan Doll",
    445: "Chaos Man",
    446: "Karate Man",
    447: "Burmese Flag",
    448: "Bl0ndie's Dictionary",
    449: "Hydroponic Grow Tent",
    466: "Snow Globe '09",
    467: "Dancing Santa Claus '09",
    468: "Christmas Stocking '09",
    469: "Santa's Elf '09",
    470: "Christmas Card '09",
    471: "Admin Portrait '09",
    479: "Metal Dog Tag",
    480: "Bronze Dog Tag",
    481: "Silver Dog Tag",
    482: "Gold Dog Tag",
    491: "Zombie Brain",
    492: "Human Head",
    493: "Medal of Honor",
    525: "Mr Torn Crown '10",
    526: "Ms Torn Crown '10",
    543: "Deputy Star",
    593: "Mr Torn Crown '11",
    594: "Ms Torn Crown '11",
    596: "Rusty Dog Tag",
    597: "Gold Nugget",
    630: "Mr Torn Crown '12",
    631: "Ms Torn Crown '12",
    685: "Torn Bible",
    686: "Friendly Bot Guide",
    687: "Egotistical Bear",
    688: "Brewery Key",
    689: "Signed Jersey",
    690: "Mafia Kit",
    691: "Octopus Toy",
    692: "Bear Skin Rug",
    693: "Tractor Toy",
    694: "Mr Torn Crown '13",
    695: "Ms Torn Crown '13",
    696: "Piece of Cake '13",
    705: "Staff Haxx Button",
    706: "Birthday Cake '14",
    708: "Gold Rosette",
    709: "Silver Rosette",
    710: "Bronze Rosette",
    711: "Coin : Factions",
    712: "Coin : Casino",
    713: "Coin : Education",
    714: "Coin : Hospital",
    715: "Coin : Jail",
    716: "Coin : Travel Agency",
    717: "Coin : Companies",
    718: "Coin : Stock Exchange",
    719: "Coin : Church",
    720: "Coin : Auction House",
    721: "Coin : Race Track",
    722: "Coin : Museum",
    723: "Coin : Drugs",
    724: "Coin : Dump",
    725: "Coin : Estate Agents",
    740: "Mr Torn Crown",
    741: "Ms Torn Crown",
    829: "Yellow Snowman '16",
    866: "Santa's List '17",
    867: "Soapbox",
    872: "Nothing",
    908: "Paper Bag",
    910: "Betting Slip",
    911: "Fidget Spinner",
    912: "Majestic Moose",
    913: "Lego Wonder Woman",
    914: "CR7 Doll",
    915: "Stretch Armstrong Doll",
    916: "Beef Femur",
    917: "Snake's Fang",
    918: "Icey Igloo",
    919: "Federal Jail Key",
    922: "Toast Jesus '18",
    923: "Cheesus '18",
    925: "Scammer in the Slammer '18",
    953: "Bronze Racing Trophy",
    954: "Silver Racing Trophy",
    955: "Gold Racing Trophy",
    976: "Bronze Microphone",
    977: "Silver Microphone",
    978: "Gold Microphone",
    1030: "Dong : Thomas",
    1031: "Dong : Greg",
    1032: "Dong : Effy",
    1033: "Dong : Holly",
    1034: "Dong : Jeremy",
    1041: "Special Snowflake",
    1147: "Helmet of Justice",
    1297: "Donkey Adoption Certificate",
    1323: "Royal Tiara",
    1324: "Rhino's Horn",
    1325: "Welding Jacket",
    1326: "Iron Man Helmet",
    1364: "Yorkshire Pudding",
    1365: "Chemistry Set",
    1366: "Glitter Pickle",
    1370: "Chakra Stones",
    1371: "Toy Taco Truck",
    1372: "Blacklight",
    1373: "Robot Bug Toys",
    1374: "Master of The Universe",
    1375: "Dilly the Dachshund",
    1376: "Cuticorn",
    1377: "Davy Jones' Footlocker",
    1378: "Origami Crane",
    1387: "Andyman's Keepsake",
    1388: "Baldr's Keepsake",
    1389: "CRLF's Keepsake",
    1390: "Proxima's Keepsake",
    1391: "mug's Keepsake",
    1392: "BambinaDuckie's Keepsake",
    1393: "bogie's Keepsake",
    1394: "Evil-Duck's Keepsake",
    1395: "D3vl's Keepsake",
    1396: "MarlonBrando's Keepsake",
    1397: "Champion's Keepsake",
    1398: "Sweeney_Todd's Keepsake",
    1399: "YoungBlaze's Keepsake",
    1400: "IceColdCola's Keepsake",
    1401: "Z_junior's Keepsake",
    1402: "BodyBagger's Keepsake",
    1403: "King_Ace's Keepsake",
    1404: "Deft's Keepsake",
    1405: "RGiskard's Keepsake",
    1406: "Hank's Keepsake",
    1407: "HT-Supermikk's Keepsake",
    1408: "someone's Keepsake",
    1409: "CockyNudist's Keepsake",
    1410: "Rosie's Keepsake",
    1411: "Data's Keepsake",
    1412: "Astral's Keepsake",
    1413: "Stormcast's Keepsake",
    1414: "JamilB's Keepsake",
    1415: "Kivou's Keepsake",
    1416: "DeKleineKobini's Keepsake",
    1417: "IceBlueFire's Keepsake",
    1418: "Mauk's Keepsake",
    1419: "Mephiles' Keepsake",
    1420: "Manuito's Keepsake",
    1421: "Ara's Keepsake",
    1422: "Body's Keepsake",
    1423: "aurigus' Keepsake",
    1424: "Quacks' Keepsake",
    1425: "Aethwynn's Keepsake",
    1426: "-Clansdancer's Keepsake",
    1427: "LeukyBear's Keepsake",
    1428: "is0lati0n's Keepsake",
    1451: "Caganer Figurine",
    1454: "Las Vegas Shot Glass '23",
    1455: "New Orleans Shot Glass '24",
    1464: "Mermaid Tiara",
    1467: "Withered M'aol Tentacle",
    1468: "Withered Ladso Eye",
    1469: "Withered Sylo Tooth",
    1470: "Withered Dyno Sac",
    1471: "Withered Nol Cloachra",
    1472: "Withered Asmol Knuckle",
    1473: "Chicago Shot Glass '25",
    1476: "Kelsie's Keepsake",
    1477: "Ana's Keepsake",
    1478: "Midknight's Keepsake",
    1479: "Evaline's Keepsake",
    1480: "Omanpx's Keepsake",
    1481: "Locked's Keepsake",
    1505: "Evil Christmas Gonk",
}

CSV_HEADERS = [
    "auction_id", "item_id", "item_name", "price", "bids",
    "seller_id", "buyer_id", "timestamp", "fetched_at"
]


def ensure_csv():
    """Create CSV with headers if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)


def load_existing_ids():
    """Load existing auction IDs to avoid duplicates."""
    existing = set()
    if not os.path.exists(CSV_FILE):
        return existing
    with open(CSV_FILE, "r") as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for row in reader:
            if row:
                existing.add(row[0])
    return existing


def fetch_api(endpoint):
    """Fetch from Torn API v2."""
    url = "{}/{}?key={}&sort=DESC&limit=100".format(BASE_URL, endpoint, API_KEY)
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "torn-auction-data/1.0")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print("HTTP Error {}: {} for {}".format(e.code, e.reason, endpoint))
        return None
    except Exception as e:
        print("Error fetching {}: {}".format(endpoint, e))
        return None


def fetch_item_auctions(item_id):
    """Fetch all auction data for a specific item, paginating via 'to' param."""
    all_auctions = []
    to_param = ""

    while True:
        url = "{}/{}/auctionhouse?key={}&sort=DESC&limit=100{}".format(
            BASE_URL, item_id, API_KEY, to_param
        )
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "torn-auction-data/1.0")
        try:
            resp = urllib.request.urlopen(req, timeout=30)
            data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            print("  HTTP Error {}: {}".format(e.code, e.reason))
            break
        except Exception as e:
            print("  Error: {}".format(e))
            break

        auctions = data.get("auctionhouse", [])
        if not auctions:
            break

        all_auctions.extend(auctions)

        # Check for next page
        metadata = data.get("_metadata", {})
        links = metadata.get("links", {})
        prev_link = links.get("prev", None)
        if not prev_link:
            break

        # Extract 'to' param from prev link for next page
        parsed = urllib.parse.urlparse(prev_link)
        params = urllib.parse.parse_qs(parsed.query)
        to_val = params.get("to", [None])[0]
        if not to_val:
            break

        to_param = "&to={}".format(to_val)
        time.sleep(0.6)  # Rate limit between pages

    return {"auctionhouse": all_auctions}


def parse_auctions(data, item_id, item_name):
    """Parse API response into CSV rows."""
    rows = []
    if not data:
        return rows

    auctions = data.get("auctionhouse", [])
    if not auctions:
        return rows

    fetched_at = int(time.time())

    for auction in auctions:
        if not isinstance(auction, dict):
            continue
        auction_id = str(auction.get("id", ""))
        if not auction_id:
            continue

        price = auction.get("price", 0)
        bids = auction.get("bids", 0)
        seller = auction.get("seller", {})
        buyer = auction.get("buyer", {})
        seller_id = str(seller.get("id", "")) if isinstance(seller, dict) else str(seller)
        buyer_id = str(buyer.get("id", "")) if isinstance(buyer, dict) else str(buyer)
        timestamp = auction.get("timestamp", "")

        rows.append([
            auction_id, str(item_id), item_name, str(price), str(bids),
            seller_id, buyer_id, str(timestamp), str(fetched_at)
        ])

    return rows


def main():
    if not API_KEY:
        print("Error: TORN_API_KEY environment variable not set")
        sys.exit(1)

    ensure_csv()
    existing_ids = load_existing_ids()
    total_new = 0
    total_items = len(COLLECTIBLE_IDS)

    print("Fetching auction data for {} collectible items...".format(total_items))

    new_rows = []

    for idx, (item_id, item_name) in enumerate(sorted(COLLECTIBLE_IDS.items())):
        print("[{}/{}] Fetching {} (ID: {})...".format(idx + 1, total_items, item_name, item_id))

        data = fetch_item_auctions(item_id)
        if data:
            rows = parse_auctions(data, item_id, item_name)
            for row in rows:
                if row[0] not in existing_ids:
                    new_rows.append(row)
                    existing_ids.add(row[0])
                    total_new += 1

        # Rate limit: ~2 calls per second to stay well under 100/min
        time.sleep(0.6)

    # Append new rows to CSV
    if new_rows:
        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(new_rows)

    print("\nDone! Added {} new auction records.".format(total_new))
    print("Total unique auction IDs in CSV: {}".format(len(existing_ids)))


if __name__ == "__main__":
    main()
