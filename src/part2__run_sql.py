# %%
import duckdb
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

# Assumptions: I only have a sample of data.
# The code is set up to run properly if more data is present

# Assumptions: We want the top 5 results.
# However, if there is a tie for 5th place, include all brands which are tied for the 5th place spot,
# as there is is not an inherent order to brands

# Assumptions: We care about unique receipts scanned, not specific times the brand was on the same receipt
# This allows for us to not account for the missing quantity data, which we cannot resolve without understanding business assumptions
# And we believe it is more important for the item to be purchased multiple times in distinct trips to the store, rather than multiples within the same check-out.

d1 = open("../sql/close_ended_1.sql", "r")
sql1 = d1.read()
d1.close()
duckdb.sql(sql1).show()


##However, if this is the full dataset, then I would advise running the following
# 90219 over 21, and not missing birthdate, from full user population
# 90219/100000 #90% of users are over 21.
# Therefore, we can assume that the brands of the full population will match the over 21 population

d1b = open("../sql/close_ended_1b.sql", "r")
sql1b = d1b.read()
d1b.close()
duckdb.sql(sql1b).show()

# %%
# Open-ended question 2:
# 2. Which is the leading brand in the Dips & Salsa category?

# Assumptions: leading brand is the brand with the highest final sales
# as there are limited transactions, we can look at all the data, rather than go through an analysis of trending historical data

# Assumptions: there are no other salsa or dip categories that are not also included in the CATEGORY_2='Dips & Salsa'
# This was verified through data exploration for the sample of data I was provided.

# Assumptions: if Final Quantity = 'zero', we assume the quantity = 1
# because we assume this data was due to a new feature rollout where data was not backfilled

# Assumptions: Final Sales is the total amount for the line item (does not need to be multiplied by a quantity)

# Assumptions: Final Sales can be imputed with the median of the salsa & dips product type


d2 = open("../sql/open_ended_2.sql", "r")
sql2 = d2.read()
d2.close()
duckdb.sql(sql2).show()

# %%
# Open-ended question 3:
# 3. At what percent has Fetch grown year over year?

# Assumptions: user growth is the measure of Fetch growth

# Assumptions: the user data provided is a representative sample, even if it is not the full dataset
# the data was pulled in the past so is not current through today, but rather current though the last user created date

# Assumptions: the standard YOY growth formula is used by Fetch:  (Users This Period-Users Last Period)/Users Last Period

d3 = open("../sql/open_ended_3.sql", "r")
sql3 = d3.read()
d3.close()
duckdb.sql(sql3).show()
