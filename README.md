# Torn Auction Data

Daily collectible auction house data fetched from the Torn City API v2.

## Data

- `data/collectible-auctions.csv` — Historical auction records for all Torn collectible items

### CSV Columns

| Column | Description |
|--------|-------------|
| auction_id | Unique auction listing ID |
| item_id | Torn item ID |
| item_name | Item name |
| price | Final auction price |
| quantity | Quantity sold |
| seller_id | Seller's player ID |
| buyer_id | Buyer's player ID |
| start_time | Auction start timestamp |
| end_time | Auction end timestamp |
| fetched_at | When this record was fetched |

## CDN Usage

Raw CSV URL for use in scripts:
```
https://raw.githubusercontent.com/russianrob/torn-auction-data/main/data/collectible-auctions.csv
```

## Schedule

Data is fetched daily at 06:00 UTC via GitHub Actions. Can also be triggered manually.

## Author

RussianRob [137558]
