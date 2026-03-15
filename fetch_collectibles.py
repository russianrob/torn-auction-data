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

# Torn collectible item IDs and names
# Source: Torn items API, category=Collectible
COLLECTIBLE_IDS = {
    74: "Santa Hat '04",
    75: "Christmas Cracker '04",
    113: "Pet Rock",
    114: "Non-Anon Doll",
    115: "Poker Doll",
    116: "Yoda Figurine",
    117: "Trojan Horse",
    118: "Magician's Hat",
    119: "Mystical Orb",
    120: "Voodoo Doll",
    121: "Teddy Bear",
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
    133: "Silver Eye",
    134: "Skateboard",
    135: "Uriel's Speakers",
    136: "Strife Clown",
    137: "Locked Teddy",
    138: "Riddle's Bat",
    139: "Unicycle",
    140: "Troll Doll",
    141: "Snow Globe",
    142: "Paper Crane",
    143: "Vanity Mirror",
    144: "Banana Phone",
    148: "Dance Toy",
    149: "Lucky Dime",
    150: "Crystal Carousel",
    151: "Nessie",
    152: "Ice Sculpture",
    153: "Case of Whiskey",
    155: "Purple Frog",
    156: "Hooorang's Key",
    157: "Patriot Whip",
    158: "Statue Of Aeolus",
    161: "Black Unicorn",
    162: "Teddy Bear '05",
    163: "Chocolate Egg '05",
    164: "Kitten Plushie",
    165: "Chocobo Flute",
    166: "Annoying Man",
    167: "Devil Doll",
    168: "Golden Candle",
    171: "Jack-O-Lantern '05",
    185: "Bunch of Balloons '05",
    188: "Cracked Crystal Ball",
    192: "Rainbow Stud Earring",
    193: "Hamster Toy",
    194: "Snowflake '05",
    195: "Christmas Tree '05",
    198: "Egg Basket '06",
    199: "Little Black Book",
    200: "Torn City Award",
    201: "Mr Torn Crown '06",
    202: "Mr Torn Crown '07",
    204: "Ms Torn Crown '06",
    207: "Ms Torn Crown '07",
    209: "Teddy Bear '07",
    210: "Jack-O-Lantern '07",
    211: "Christmas Stocking '07",
    212: "Party Popper '07",
    213: "Skateboard Deck",
    214: "Golden Skateboard",
    215: "Action Figure '08",
    216: "Salt Shaker",
    255: "Jack-O-Lantern '08",
    256: "Dahlia",
    258: "Snowflake '08",
    259: "Christmas Cracker '08",
    260: "Action Figure '09",
    267: "Rubber Duck '09",
    268: "Jack-O-Lantern '09",
    269: "Christmas Stocking '09",
    270: "Snowflake '09",
    271: "Hot Chocolate",
    272: "Gingerbread Man",
    273: "Action Figure '10",
    274: "Chocolate Bunny '10",
    276: "Party Hat",
    277: "Jack-O-Lantern '10",
    278: "Candy Corn",
    279: "Snowflake '10",
    280: "Christmas Cracker '10",
    283: "Action Figure '11",
    284: "Chocolate Egg '11",
    285: "Chocolate Bunny '11",
    286: "Novelty Rubber Duck",
    287: "Jack-O-Lantern '11",
    288: "Pumpkin '11",
    291: "Snowflake '11",
    292: "Christmas Cracker '11",
    297: "Easter Egg '12",
    298: "Chocolate Bunny '12",
    300: "Sand Castle",
    302: "Jack-O-Lantern '12",
    304: "Christmas Cracker '12",
    305: "Snowflake '12",
    366: "Easter Egg '13",
    367: "Chocolate Bunny '13",
    373: "Jack-O-Lantern '13",
    375: "Snowflake '13",
    376: "Christmas Cracker '13",
    377: "Action Figure '13",
    382: "Easter Egg '14",
    383: "Chocolate Bunny '14",
    384: "Grumpy Cat",
    385: "Sand Castle '14",
    386: "Pumpkin '14",
    387: "Jack-O-Lantern '14",
    388: "Christmas Cracker '14",
    389: "Snowflake '14",
    392: "Pumpkin Head",
    394: "Santa Hat '14",
    396: "Action Figure '14",
    403: "Easter Egg '15",
    404: "Chocolate Bunny '15",
    405: "Bear Plushie",
    406: "Jack-O-Lantern '15",
    407: "Pumpkin '15",
    408: "Christmas Cracker '15",
    409: "Snowflake '15",
    410: "Kitten '15",
    411: "Action Figure '15",
    441: "Chocolate Bunny '16",
    442: "Easter Egg '16",
    443: "Balloon Duck '16",
    444: "Jack-O-Lantern '16",
    445: "Pumpkin '16",
    446: "Snowflake '16",
    447: "Christmas Cracker '16",
    448: "Action Figure '16",
    452: "Chocolate Bunny '17",
    453: "Easter Egg '17",
    454: "Balloon Duck '17",
    455: "Jack-O-Lantern '17",
    456: "Pumpkin '17",
    459: "Snowflake '17",
    460: "Christmas Cracker '17",
    461: "Action Figure '17",
    462: "Chocolate Bunny '18",
    463: "Easter Egg '18",
    464: "Balloon Duck '18",
    465: "Jack-O-Lantern '18",
    466: "Pumpkin '18",
    467: "Snowflake '18",
    468: "Christmas Cracker '18",
    469: "Action Figure '18",
    470: "Chocolate Bunny '19",
    471: "Easter Egg '19",
    472: "Balloon Duck '19",
    473: "Jack-O-Lantern '19",
    474: "Pumpkin '19",
    475: "Snowflake '19",
    476: "Christmas Cracker '19",
    477: "Action Figure '19",
    478: "Chocolate Bunny '20",
    479: "Easter Egg '20",
    480: "Balloon Duck '20",
    491: "Jack-O-Lantern '20",
    492: "Pumpkin '20",
    493: "Snowflake '20",
    494: "Christmas Cracker '20",
    495: "Action Figure '20",
    629: "Chocolate Bunny '21",
    630: "Easter Egg '21",
    631: "Balloon Duck '21",
    632: "Twitch Subscriber Perk",
    633: "Jack-O-Lantern '21",
    634: "Pumpkin '21",
    635: "Snowflake '21",
    636: "Christmas Cracker '21",
    637: "Action Figure '21",
    833: "Chocolate Bunny '22",
    834: "Easter Egg '22",
    835: "Balloon Duck '22",
    839: "Jack-O-Lantern '22",
    840: "Pumpkin '22",
    841: "Snowflake '22",
    842: "Christmas Cracker '22",
    843: "Action Figure '22",
    844: "Easter Egg '23",
    845: "Chocolate Bunny '23",
    847: "Balloon Duck '23",
    848: "Jack-O-Lantern '23",
    849: "Pumpkin '23",
    851: "Snowflake '23",
    852: "Christmas Cracker '23",
    853: "Action Figure '23",
    1060: "Easter Egg '24",
    1061: "Chocolate Bunny '24",
    1062: "Balloon Duck '24",
    1160: "Jack-O-Lantern '24",
    1161: "Pumpkin '24",
    1162: "Snowflake '24",
    1163: "Christmas Cracker '24",
    1165: "Action Figure '24",
    1232: "Easter Egg '25",
    1233: "Chocolate Bunny '25",
    1234: "Balloon Duck '25",
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
