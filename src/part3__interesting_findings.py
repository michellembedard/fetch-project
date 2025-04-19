# %%
# import packages
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


# %%
# set up date fields
users_parse_dates = ["CREATED_DATE", "BIRTH_DATE"]

# import data
users_df = pd.read_csv("../data/USER_TAKEHOME.csv", parse_dates=users_parse_dates)

users_df
# %%
##Determine if we can find interesting user trends that go along with the YOY growth story

#%%
#1. Look into Gender to see who our current audience is and if that has shifted over time
    # this could be interesting for marketing
#2. Look into Age to see who our current audience is and if that has shifted over time 
    # this will be interesting for the business to ensure we are growing in a healthy manner
