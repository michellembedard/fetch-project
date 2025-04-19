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
