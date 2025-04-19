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


# %%
