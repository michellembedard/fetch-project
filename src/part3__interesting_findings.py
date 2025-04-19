# %%
# import packages
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import plotly.express as px
from dateutil.relativedelta import relativedelta
from scipy import stats

# %%
# set up date fields
users_parse_dates = ["CREATED_DATE", "BIRTH_DATE"]

# import data
users_df = pd.read_csv("../data/USER_TAKEHOME.csv", parse_dates=users_parse_dates)

users_df
# %%
##Determine if we can find interesting user trends that go along with the YOY growth story

# %%
# 1. Look into Gender to see who our current audience is and if that has shifted over time
# this could be interesting for marketing
# 2. Look into Age to see who our current audience is and if that has shifted over time
# this will be interesting for the business to ensure we are growing in a healthy manner

# %%
# create plotting function to plot each value of a column on a time series together


def timeseries_plotting(
    dataframe: pd.DataFrame = users_df, groupcol: str = "GENDER", grain: str = "Daily"
):
    """Function to plot the quantity of each category across time.

    Args:
        users_df_ (pd.DataFrame, optional): DataFrame which has column to plot. Defaults to users_df.
        groupcol (str, optional): Column to plot. Defaults to 'GENDER'.
        grain (str, optional): Frequency of time series plots. Defaults to 'Daily'. Can also accept "Weekly" or "Monthly"

    Returns:
        plotly.go figure: returns the plotly figure which can be displayed with .show()
    """

    # Determine the categories we will need for plotting
    groups = list(users_df[[groupcol]].value_counts().keys())
    fig = go.Figure()
    # For each category, plot the data in a time series
    for g in groups:
        g_ = g[0]
        df = dataframe.copy()
        # copy the dataframe and get the daily level count (rather than at a timestamp granularity)
        df["CREATED_DATE_"] = pd.to_datetime(df["CREATED_DATE"].dt.date)
        df_ = (
            df[df[groupcol] == g_][["CREATED_DATE_", groupcol]]
            .groupby("CREATED_DATE_")
            .agg("count")
        )
        # if necessary, resample to necessarily granularity level
        if grain == "Weekly":
            df_resampled = df_.resample("W").sum()
        elif grain == "Monthly":
            df_resampled = df_.resample("ME").sum()
        else:
            df_resampled = df_.resample("D").sum()
        # plot the resampled data
        fig.add_trace(
            go.Scatter(
                name=g_,
                mode="lines",
                x=df_resampled.index,
                y=df_resampled[groupcol],
            )
        )
    fig.update_xaxes(showgrid=True, ticklabelmode="period")
    fig.update_layout(title=str(grain) + " new users by " + str(groupcol))
    # return the graph object which can later be shown
    return fig


# %%
# use the function to plot the gender of users over time, on the different granularities
f = timeseries_plotting()
f.show()

f = timeseries_plotting(grain="Weekly")
f.show()

f = timeseries_plotting(grain="Monthly")
f.show()

##1. Notes:
# Genders stay at roughly the same proportion over time.
# There are a couple of days where there was a spike in male users.
# It could be interesting to see if marketing helped cause these spikes or if there is some other activity we can capitalize on.
# This is interesting, but will now pursue age for additional findings.

# %%
# To prep for age discovery, add field for age at account creation
# maybe plot box plots of age and quantity of age over time
users_df["age_at_creation_days"] = (
    users_df["CREATED_DATE"] - users_df["BIRTH_DATE"]
).map(lambda x: np.nan if pd.isnull(x) else x.days)
users_df["Age_at_Creation"] = users_df["age_at_creation_days"].apply(
    lambda x: x / 365.2425
)

# find pct of users without age
users_df["Age_at_Creation"].count() / len(users_df["Age_at_Creation"])
# 96.3% have an age so we can assume this is representative of the full population

# %%
# also add in columns for when the user account was created at the Month and Year so we have easier discovery below
users_df["CREATED_DATE_Month"] = (
    users_df["CREATED_DATE"].dt.to_period("M").dt.to_timestamp()
)
users_df["CREATED_DATE_Year"] = (
    users_df["CREATED_DATE"].dt.to_period("Y").dt.to_timestamp()
)

# %%
# plot the distribution of age at time account was created
# loop through the different grains
for d in ["CREATED_DATE", "CREATED_DATE_Month", "CREATED_DATE_Year"]:
    fig = px.box(users_df, x=d, y="Age_at_Creation")
    fig.show()

##2. Notes:
# Population age looks fairly consistent over time
# There was a decrese around 2020, but it has looked flat for the last couple of years
# Next steps - determine if there is a stat sig difference in the age distributions for this year compared to last year
# Similar to the SQL section, I am assuming that the data is a sample
# so I will use the latest created_date as the most recent information and work backwards from there
# %%
# Create relative date variables
max_created_date = users_df["CREATED_DATE"].max()
one_year_ago = users_df["CREATED_DATE"].max() + relativedelta(years=-1)
two_years_ago = users_df["CREATED_DATE"].max() + relativedelta(years=-2)

# add flag for created within the last year vs the year prior
users_df["created_within_the_last_year"] = (
    (users_df["CREATED_DATE"] > one_year_ago)
    & (users_df["CREATED_DATE"] <= max_created_date)
).astype(int)
users_df["created_within_the_year_prior"] = (
    (users_df["CREATED_DATE"] > two_years_ago)
    & (users_df["CREATED_DATE"] <= one_year_ago)
).astype(int)

# %%
# First, plot the distribution to see if it is normally distributed,
# as this will affect which tests we can use without resampling

# set up within the last year and within 2 years ago populations
df1 = users_df[users_df["created_within_the_last_year"] == 1]
df2 = users_df[users_df["created_within_the_year_prior"] == 1]

# plot these populations together to see the distributions as well as how they compare
fig = go.Figure()
fig.add_trace(go.Histogram(x=df1["Age_at_Creation"], name="Past Year - Signup Age"))
fig.add_trace(go.Histogram(x=df2["Age_at_Creation"], name="Two Years Ago - Signup Age"))
fig.update_layout(barmode="overlay")
fig.update_traces(opacity=0.75)
fig.update_layout(title="Age at Account Creation by relative year")
fig.show()

# These are not normally distributed, even though they do have a bit of a bell curve.
# %%
# Use ks-test since it does not assume normal distribution and our data is not normally distributed
# to identify if the distribution of the ages is stat sig different
# H0=Two distributions are identical

# remove nulls from age, as we saw above most people had age
# so we can remove these samples with decent confidence that it will not affect our overall findings
df1_ = df1[pd.isna(df1["Age_at_Creation"]) == False]["Age_at_Creation"]
df2_ = df2[pd.isna(df2["Age_at_Creation"]) == False]["Age_at_Creation"]

# Calculate the stats
ks_statistic, p_value = stats.ks_2samp(df1_, df2_)
print("K-S statistic:", ks_statistic)
print("P-value:", p_value)

# stat sig. So we reject that the distributions are the same
# meaning our population of users is different this year compared to last year

# Now compare the stats to see what the difference in ages is
print("This past year")
print(df1_.mean())
print(df1_.quantile([0.25, 0.5, 0.75]))

print("Two years ago")
print(df2_.mean())
print(df2_.quantile([0.25, 0.5, 0.75]))

# visually see the differences in this past year vs the year prior
# 25th percentile: past year 26.9, prior yr 24.1
# 50th percentile: past year 40, prior yr 37
# 25th percentile: past year 52.6, prior yr 49.7
