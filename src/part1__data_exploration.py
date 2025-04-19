# %%
# import packages
import pandas as pd
import numpy as np

# %%
# set up date fields
users_parse_dates = ["CREATED_DATE", "BIRTH_DATE"]
transaction_parse_dates = ["PURCHASE_DATE", "SCAN_DATE"]

# import data
products_df = pd.read_csv("../data/PRODUCTS_TAKEHOME.csv")
transactions_df = pd.read_csv(
    "../data/TRANSACTION_TAKEHOME.csv", parse_dates=transaction_parse_dates
)
users_df = pd.read_csv("../data/USER_TAKEHOME.csv", parse_dates=users_parse_dates)
