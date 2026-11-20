# Practice data

A small food-delivery dataset. Every SQL and pandas example in `docs/research/02-panorama-and-openings.md` was run against these files, so numbers quoted in the lesson drafts (6,000 orders, 399 cancelled, 60 restaurants in four cities, 200 couriers on three kinds of vehicle) are true of this data.

| File | Rows | Columns |
|---|---|---|
| `orders.csv` | 6,000 | order_id, customer_id, restaurant_id, courier_id, created_at, subtotal, delivery_fee, coupon_code, status, promised_minutes, actual_minutes |
| `restaurants.csv` | 60 | restaurant_id, name, city, cuisine, signup_date |
| `couriers.csv` | 200 | courier_id, vehicle, city |

Things worth knowing when writing lessons:

- `status` is either `delivered` or `cancelled`.
- `orders` has no city. City lives in `restaurants` and `couriers`, so any "per city" question about orders needs a join.
- `coupon_code` is empty on most rows, and `courier_id` is empty on cancelled orders. Keep both out of early lessons.
- `created_at` is text in the form `2026-08-01 00:00:00`.

The data was generated with a fixed random seed for the owner's earlier mock tests. The sibling repository `live-coding-gym` has a similar but different dataset in its `content/_shared` folder. Do not mix the two.
