# %%
import duckdb  # this is used to run SQL in python since I am not connecting to an external database
import pandas as pd

# %%
# import csvs as dfs so that we can run the sql below
users_parse_dates = ["CREATED_DATE", "BIRTH_DATE"]
transaction_parse_dates = ["PURCHASE_DATE", "SCAN_DATE"]

# import data
products_df = pd.read_csv("../data/PRODUCTS_TAKEHOME.csv")
transactions_df = pd.read_csv(
    "../data/TRANSACTION_TAKEHOME.csv", parse_dates=transaction_parse_dates
)
users_df = pd.read_csv("../data/USER_TAKEHOME.csv", parse_dates=users_parse_dates)

# %%
# Close-ended question 1:
# 1. What are the top 5 brands by receipts scanned among users 21 and over?

# Assumption 1: I only have a sample of data.
# The code is set up to run properly if more data is present

# Assumption 2: We want the top 5 results.
# However, if there is a tie for 5th place, include all brands which are tied for the 5th place spot,
# as there is is not an inherent order to brands

# Assumption 3: We care about unique receipts scanned, not specific times the brand was on the same receipt
# This allows for us to not account for the missing quantity data, which we cannot resolve without understanding business assumptions
# And we believe it is more important for the item to be purchased multiple times in distinct trips to the store, rather than multiples within the same check-out.

# Assumption 4: Products without barcodes have been manually entered
# and are not validated with the system.
# Therefore, they should not be considered in the analysis.

# Assumption 5: Duplicate barcodes in the product data must be resolved.
# There should only be one set of product details per barcode.
# The assumption is the product details with the most data is the most accurate
# and if there is a tie, then the product details with brand is most accurate.

d1 = open("../sql/close_ended_1.sql", "r")
sql1 = d1.read()
d1.close()
duckdb.sql(sql1).show()
"""
Top 5 brands by unique receipts scanned by users 21+
┌─────────────────┬─────────────────┐
│      BRAND      │ unique_receipts │
│     varchar     │      int64      │
├─────────────────┼─────────────────┤
│ DOVE            │               3 │
│ NERDS CANDY     │               3 │
│ MEIJER          │               2 │
│ SOUR PATCH KIDS │               2 │
│ HERSHEY'S       │               2 │
│ GREAT VALUE     │               2 │
│ TRIDENT         │               2 │
│ COCA-COLA       │               2 │
└─────────────────┴─────────────────┘
"""


## However, if I have been provided with the full dataset,
# then I would advise running the following to mitigate the risk of missing user data.
    # As, 90219 are over 21, and not missing birthdate, from full user population
    # 90219/100000 #90% of users are over 21.
# Therefore, we can assume that the brands of the full population will match the over 21 population

d1b = open("../sql/close_ended_1b.sql", "r")
sql1b = d1b.read()
d1b.close()
duckdb.sql(sql1b).show()
"""
Top 5 brands by unique receipts scanned (based on above caveat)
┌─────────────┬─────────────────┐
│    BRAND    │ unique_receipts │
│   varchar   │      int64      │
├─────────────┼─────────────────┤
│ COCA-COLA   │             527 │
│ GREAT VALUE │             384 │
│ PEPSI       │             361 │
│ EQUATE      │             341 │
│ LAY'S       │             324 │
└─────────────┴─────────────────┘
"""

# %%
# Open-ended question 2:
# 2. Which is the leading brand in the Dips & Salsa category?

# Assumption 1: leading brand is the brand with the highest final sales
# as there are limited transactions, we can look at all the data, rather than go through an analysis of trending historical data

# Assumption 2: there are no other salsa or dip categories that are not also included in the CATEGORY_2='Dips & Salsa'
# This was verified through data exploration for the sample of data I was provided.

# Assumption 3: if Final Quantity = 'zero', we assume the quantity = 1
# because we assume this data was due to a new feature rollout where data was not backfilled

# Assumption 4: Final Sales is the total amount for the line item (does not need to be multiplied by a quantity)

# Assumption 5: Final Sales can be imputed with the median of the salsa & dips product type from items in transactions.
# This accounts for the median based on actual purchases,
# rather than the median from the product list without considering shopping patterns.
# Since quantity is almost always 1 and imputing assumption is not fully trustworthy without more business context,
# then I will not multiply by quantity in order to limit risks of imputing.

# Assumption 6: Products without barcodes have been manually entered
# and are not validated with the system.
# Therefore, they should not be considered in the analysis.

# Assumption 7: Duplicate barcodes in the product data must be resolved.
# There should only be one set of product details per barcode.
# The assumption is the product details with the most data is the most accurate
# and if there is a tie, then the product details with brand is most accurate.

d2 = open("../sql/open_ended_2.sql", "r")
sql2 = d2.read()
d2.close()
duckdb.sql(sql2).show()
# TOSTITOS is the leading Dips & Salsa brand

# %%
# Open-ended question 3:
# 3. At what percent has Fetch grown year over year?

# Assumption 1: user growth is the measure of Fetch growth

# Assumption 2: the user data provided is a representative sample, even if it is not the full dataset
# the data was pulled in the past so is not current through today, but rather current though the last user created date

# Assumption 3: the standard YOY growth formula is used by Fetch:  (Users This Period-Users Last Period)/Users Last Period
# this is calculating the full population growth rate, not the new user growth rate

# Assumption 4: we would like to view YOY growth for the last 5 years

d3 = open("../sql/open_ended_3.sql", "r")
sql3 = d3.read()
d3.close()
duckdb.sql(sql3).show()
# 18.2% YOY growth over the last year

# Ideally, I would want to measure YOY Growth for active users
# However, since there is only June-Sept 2024 transactions I cannot go this route
# as it would be unfairly penalizing old users where we do not have their transaction data
# I would like to use a measure of activity that indicates longer-term usage.
# For instance, I would want to mark a user a part of our population if they have a transaction at least 90 days after signup
# Again, with the limited data, that is not possible.
# However, to illustrate a way I would go about it (with the current data), I would do something like the following
# (With the current data availability, I would assume a higher YOY growth this way than the first query, as newer users likely have transactions this year compared to older users)

d3b = open("../sql/open_ended_3b.sql", "r")
sql3b = d3b.read()
d3b.close()
duckdb.sql(sql3b).show()
# as expected, **very low** user quantity considered due to limited transaction data (but also a slightly higher growth rate)
# this data CANNOT be trusted until more historic transaction data is available.
# %%
