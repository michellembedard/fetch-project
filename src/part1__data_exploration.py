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
# %%
# verify correct data type imports
products_df.dtypes
transactions_df.dtypes
users_df.dtypes

# %%
# look for missing values
products_df.info()
transactions_df.info()
users_df.info()

# %%
# fix transactions_df numeric formatting
transactions_df["FINAL_QUANTITY"].value_counts()
transactions_df["FINAL_SALE"].value_counts()
# FINAL_QUANTITY "zero" should be "0", then convert to number
# FINAL_SALE should remove " ", then convert to number

## fix final_quantity
transactions_df["FINAL_QUANTITY"] = transactions_df["FINAL_QUANTITY"].str.replace(
    "zero", "0"
)
transactions_df["FINAL_QUANTITY"].replace("", np.nan, inplace=True)
transactions_df["FINAL_QUANTITY"].astype(float)

## fix final_sale
transactions_df["FINAL_SALE"] = transactions_df["FINAL_SALE"].str.replace(" ", "")
transactions_df["FINAL_SALE"].replace("", np.nan, inplace=True)
transactions_df["FINAL_SALE"].astype(float)
# %%
