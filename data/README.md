# Practice data

A small food-delivery dataset. Every SQL and pandas example in `docs/research/02-panorama-and-openings.md` was run against these files, so numbers quoted in the lesson drafts (6,000 orders, 399 cancelled, 60 restaurants in four cities, 200 couriers on three kinds of vehicle) are true of this data.

| File | Rows | Columns |
|---|---|---|
| `orders.csv` | 6,000 | order_id, customer_id, restaurant_id, courier_id, created_at, subtotal, delivery_fee, coupon_code, status, promised_minutes, actual_minutes |
| `restaurants.csv` | 60 | restaurant_id, name, city, cuisine, signup_date |
| `couriers.csv` | 200 | courier_id, vehicle, city |
| `deliveries.csv` | 5,601 | order_id, distance_km, rain, bag_size |
| `coupons.csv` | 4 | coupon_code, discount_pct |

Things worth knowing when writing lessons:

- `status` is either `delivered` or `cancelled`.
- `orders` has no city. City lives in `restaurants` and `couriers`, so any "per city" question about orders needs a join.
- `coupon_code` is empty on most rows, and `courier_id` and `actual_minutes` are empty on cancelled orders. Keep them out of early lessons.
- `subtotal` is empty on 25 orders (23 delivered, 2 cancelled). Found on 20 Nov 2026 while checking lesson 1. Load empty cells as missing values, not as empty text, or averages and comparisons on `subtotal` come out wrong.
- `created_at` is text in the form `2026-08-01 00:00:00`.

The data was generated with a fixed random seed for the owner's earlier mock tests. The sibling repository `live-coding-gym` has a similar but different dataset in its `content/_shared` folder. Do not mix the two.

## Tables added on 24 Nov 2026

The owner allowed synthetic additions (decision C15). The three original files were not changed, and no lesson answer that was checked against them moved.

**`deliveries.csv`** has one row for each delivered order. Cancelled orders have no row, so 399 orders have no delivery.

- `distance_km`: restaurant to customer. Empty on 112 rows, as if the GPS dropped out.
- `rain`: 1 if it rained during the delivery.
- `bag_size`: how many orders the courier carried at once, from 1 to 3.

It exists so that lateness has something to be predicted by. In the original tables every column was unrelated to lateness, and any model scored an AUC of about 0.50. These three columns were generated from each order's delay (actual minus promised minutes), with noise, so the relation is real in the data even though the data is made up:

- `distance_km` is 2.5, 4.5 or 6.5 for a promise of 30, 40 or 50 minutes, plus 0.07 for each minute of delay, plus noise with a standard deviation of 0.9, never below 0.4.
- `rain` has probability `1 / (1 + exp(1.5 - 0.07 * delay))`.
- `bag_size` is 1 plus two draws that each succeed with probability `1 / (1 + exp(1.4 - 0.05 * delay))`.
- NumPy's default generator, seed 20261124. Rows were then shuffled.

What that gives: 37.5 percent late without rain and 63.8 percent with it. A logistic regression on the three columns scores an AUC of 0.70, and 0.80 with `promised_minutes` added.

**`coupons.csv`** lists the four coupon codes. `VOLTA15` appears on no order. It exists so that "rows with no match" has a row to find.

The checker and the player load every CSV in this folder, so both tables are visible to SQL.

## Real data, kept out of git

`data/real/olist/` holds the **Brazilian E-Commerce Public Dataset by Olist**: about 100,000 real orders from 2016 to 2018, in nine CSV files (126 MB). The two cold sittings use it (decision C17). The lessons do not.

- Source: Kaggle, dataset `olistbr/brazilian-ecommerce`, file `brazilian-ecommerce.zip` (42.6 MB), fetched on 24 Nov 2026.
- Licence: CC BY-NC-SA 4.0. Credit Olist, do not sell it, and share any changed copy under the same licence. This repository is public, so the folder is in `.gitignore` and the files are not committed.
- To fetch it again on another machine, with a Kaggle token in `~/.kaggle/kaggle.json`: `uvx --with six kaggle datasets download -d olistbr/brazilian-ecommerce`, then unzip into `data/real/olist/`.
- The checker and the player load only the CSV files directly in `data/`, so nothing in `data/real/` reaches a lesson unless a later design says so.

| File | Rows | What it is |
|---|---|---|
| `olist_orders_dataset.csv` | 99,441 | One row per order: status, and the purchase, delivery and estimated delivery times |
| `olist_order_items_dataset.csv` | 112,650 | One row per item in an order: product, seller, price, freight |
| `olist_order_payments_dataset.csv` | 103,886 | Payment type, instalments and value |
| `olist_order_reviews_dataset.csv` | 99,224 | Review score from 1 to 5, and comments in Portuguese |
| `olist_customers_dataset.csv` | 99,441 | City and state. A returning customer has several `customer_id` values and one `customer_unique_id`. |
| `olist_sellers_dataset.csv` | 3,095 | City and state |
| `olist_products_dataset.csv` | 32,951 | Category, size and weight |
| `product_category_name_translation.csv` | 71 | Category names in English |
| `olist_geolocation_dataset.csv` | 1,000,163 | Latitude and longitude by postcode prefix |

Worth knowing: `delivered` is 96,478 of the orders, 8.1 percent of delivered orders arrived after the estimated date, 775 orders have no items, and dates are text.
