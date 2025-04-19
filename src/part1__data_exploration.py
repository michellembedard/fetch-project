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

# %%
# At this point, combine the data based on the ERD since basic exploration of the data on its own is complete
# There should be a 1-to-many relationship between users and transactions
# There should be a 1-to-many relationship between products and transactions

# %%
# verify that there is only 1 row per user (aka users are distinct) in the users_df
assert len(users_df) == users_df["ID"].nunique()

# no duplicative user ids

# %%
# verify barcodes are distinct in the products_df

# assert len(products_df)==products_df['BARCODE'].nunique()
# assertion error. Additional exploration required

# A. Exploration
# see discripancy quantity
len(products_df)  # 845552
products_df["BARCODE"].nunique()  # 841342

products_df["BARCODE"].nunique() / len(products_df)  # 0.9950210040305032
# almost no duplciates.

# determine if they are true duplciates or if there is different information in the products_df
products_df[products_df.duplicated()]  # 215 true duplicates
845552 - 841342  # 4210 duplicates
# we cannot just drop duplicates and move on. We have to create de-dup logic.

# There are multiple products without a barcode.
# This is a data quality issue we will need to address and understand.
# the blank barcodes are interesting, but I assume they are manually-entered and have yet to be incorporated to the auotmatic system which is why they do not have a barcode.
products_df[pd.isna(products_df["BARCODE"]) == True]  # 4025

# Non-blank but also duplicate barcodes
products_df[
    (products_df.duplicated("BARCODE")) & (pd.isna(products_df["BARCODE"]) == False)
]
# 185 rows to resolve.
# save these in a list for further use
dup_barcodes = (
    products_df["BARCODE"]
    .value_counts()[products_df["BARCODE"].value_counts() > 1]
    .keys()
    .to_list()
)


# B. Resolve dups
# to resolve dups, as there is no updated as of column, we cannot use a modified timestamp to pull in the most recent info
# therefore, we will pull int the information based on how much data is filled out

# 0. save non-dups
# 1. drop dups
# 2. calc how many fields are filled out
# 3. rn based on # of fields
# otherwise, choose highest index
# since we are assuming that the most recent records are at the bottom if we did not gain more product information

# B.0
# non-dups
products_df_ = products_df[~(products_df["BARCODE"].isin(dup_barcodes))]

# B.1
dup_products = products_df[products_df["BARCODE"].isin(dup_barcodes)]
dup_products.drop_duplicates(inplace=True)  # 212 rows

# B.2 calculate how much data is filled

# For the categories, see if they are null or filled
for i in range(1, 5):
    dup_products["cat" + str(i) + "_notnull"] = (
        ~pd.isna(dup_products["CATEGORY_" + str(i)])
    ).astype(int)

# For the manufacturer/brand, see if they are null or filled
dup_products["manufacturer_notnull"] = (~pd.isna(dup_products["MANUFACTURER"])).astype(
    int
)
dup_products["brand_notnull"] = (~pd.isna(dup_products["BRAND"])).astype(int)

# count the number of non-nulls
dup_products["total_notnull"] = (
    dup_products["cat1_notnull"]
    + dup_products["cat2_notnull"]
    + dup_products["cat3_notnull"]
    + dup_products["cat4_notnull"]
    + dup_products["manufacturer_notnull"]
    + dup_products["brand_notnull"]
)

# also save the index into a column for easier user in B3
dup_products["index_num"] = dup_products.index

# B3. Create a flag for if we should keep the row, based on how much info is filled out/latest index
dup_products["keep_flag"] = (
    dup_products.sort_values(
        ["BARCODE", "total_notnull", "index_num"], ascending=[True, False, False]
    )
    .groupby(["BARCODE"])
    .cumcount()
    + 1
)

# Only keep the rows where flag=1
de_dup_products = dup_products[dup_products["keep_flag"] == 1]
# 185. good. expected amount

# Save the columns we want to add into our de-duped products
cols = list(products_df_.columns)

# Add data into de-duped products
products_df_ = pd.concat([products_df_, de_dup_products[cols]])

# C.
# verify de-duping barcodes was successful
# counts should match when excluding null barcodes.
assert (
    len(products_df_[pd.isna(products_df_["BARCODE"]) == False])
    == products_df_[pd.isna(products_df_["BARCODE"]) == False]["BARCODE"].nunique()
)

# also create a df without null barcodes in the products data since that can be useful
products_df_nonulls = products_df_[pd.isna(products_df_["BARCODE"]) == False]
