# %%
# import packages
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


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
print(products_df.dtypes)
print(transactions_df.dtypes)
print(users_df.dtypes)

# %%
# look for missing values
print(products_df.info())
print(transactions_df.info())
print(users_df.info())

# %%
# fix transactions_df numeric formatting
print(transactions_df["FINAL_QUANTITY"].value_counts())
print(transactions_df["FINAL_SALE"].value_counts())
# FINAL_QUANTITY "zero" should be "0", then convert to number
# FINAL_SALE should remove " ", then convert to number

## fix final_quantity
transactions_df["FINAL_QUANTITY"] = transactions_df["FINAL_QUANTITY"].str.replace(
    "zero", "0"
)
transactions_df["FINAL_QUANTITY"].replace("", np.nan, inplace=True)
transactions_df["FINAL_QUANTITY"] = transactions_df["FINAL_QUANTITY"].astype(float)

## fix final_sale
transactions_df["FINAL_SALE"] = transactions_df["FINAL_SALE"].str.replace(" ", "")
transactions_df["FINAL_SALE"].replace("", np.nan, inplace=True)
transactions_df["FINAL_SALE"] = transactions_df["FINAL_SALE"].astype(float)
# %%
# look at value distribution for each df

# Indicate we want to add a column for missing data
SHOW_MISSING = True

# for each df, run through the columns
for d in [products_df, transactions_df, users_df]:
    for c in list(d.columns):
        if SHOW_MISSING:
            d["filled"] = d[c].fillna("MISSING")
        else:
            d["filled"] = d[c]
        # create a histogram, sorted by quantity, to visualize our data
        fig = go.Figure()
        fig.add_trace(
            go.Histogram(histfunc="count", y=d.index, x=d["filled"], name="count")
        )
        fig.update_xaxes(categoryorder="total descending")
        fig.update_layout(title=str(c))
        fig.show()

# Quick callouts:
# final quantity and final scale are right skewed
# brand and manufacturer are frequently missing data
# purchase and scan date are uniformly distributed over our time range
# user data was created since 2018, so I will assume this is a random sample and representative of the population
# state is frequently missing, but when it is filled out, it is roughly in state population order, so it seems our users are representative of the US population

# %%
##FINAL_QUANTITY
# Deeper exploration on the 0 items since this does not make sense.
# I would imagine that at least 1 item must exist per reciept.

# Hypothesis: Quantity is a feature that was added at a later point in time
# from my personal usage, this looks like a feature that was added but never backfilled
# July 2024 is when I started getting quantities

# See if we have a lot of 0 quantity and then it phases out to have a quantity
transactions_df[["SCAN_DATE", "PURCHASE_DATE", "FINAL_QUANTITY"]].sort_values(
    ["SCAN_DATE"]
)
transactions_df[["SCAN_DATE", "PURCHASE_DATE", "FINAL_QUANTITY"]].sort_values(
    ["PURCHASE_DATE"]
)
# the hypothesis does not appear to hold true.
# however, data is only from June-Sept 2024,
# so I am going to have to assume this was due to an app version and the 0 quantity will fade out over time

# %%
##FINAL_SALE
# Deeper exploration since this seems to be a key feature that is missing from a lot of the data

# Hypothesis: There is one missing final sale per reciept. This may be a placeholder for metadata.

transactions_df[pd.isna(transactions_df["FINAL_SALE"]) == True]

# save the info where final sale data is missing
missing_final_sale_df = transactions_df[pd.isna(transactions_df["FINAL_SALE"]) == True]

# quick plot for frequency over scan date
fig = go.Figure(data=[go.Histogram(x=missing_final_sale_df["SCAN_DATE"])])
fig.show()
# occurs over the full date range

# quick plot for frequency by final quantity
fig = go.Figure(data=[go.Histogram(x=missing_final_sale_df["FINAL_QUANTITY"])])
fig.show()
# most are 1s. but this mirrors the full dataset.

# now look to see if there is 1/reciept
missing_final_sale_df["RECEIPT_ID"].value_counts()
# there are occassionally more than 1 missing final sale amount per reciept.
# Therefore, this does not appear to be a total line item amount

# double check the quantity of missing final sale
transactions_df_ = transactions_df.copy()
transactions_df_["missing_final_sale"] = (
    pd.isna(transactions_df["FINAL_SALE"]) == True
).astype(int)
transactions_df_["missing_final_sale"].agg(["count", "sum"])
# 25% 12500/5000 are missing final sale amounts
# This is pretty frequent so data quality is a concern here.

# the hypothesis does not appear to hold true.
# we will have to deal with the missing data.
# I will assume that this is randomly missing and we can impute the data
