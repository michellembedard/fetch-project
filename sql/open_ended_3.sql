--identify yoy growth for the last 5 years
with yoy_start as (
    --assumption is that this is a random sample of user data
    --do rolling year from the max date since I believe we have only a sample of data which does not go through present-day
    select max(created_date) as current_date_of_data
    from users_df
)
, user_details as (
    --identify key information about the user
    --including flags indicating when they became part of the user base
    --assumption is that all users provided are still part of our user population 
    select created_date
        , current_date_of_data
        --, dateadd(year,-1,current_date_of_data) as oneyearago --AWS Redshift syntax example
        , current_date_of_data::TIMESTAMP - interval 1 year as oneyearago
        , current_date_of_data::TIMESTAMP - interval 2 year as twoyearsago
        , current_date_of_data::TIMESTAMP - interval 3 year as threeyearsago
        , current_date_of_data::TIMESTAMP - interval 4 year as fouryearsago
        , current_date_of_data::TIMESTAMP - interval 5 year as fiveyearsago
        , case when created_date::timestamp between oneyearago and current_date_of_data then 1 else 0 end as new_0_1_year_ago
        , case when created_date::timestamp between twoyearsago and oneyearago then 1 else 0 end as new_1_2_year_ago
        , case when created_date::timestamp between threeyearsago and twoyearsago then 1 else 0 end as new_2_3_year_ago
        , case when created_date::timestamp between fouryearsago and threeyearsago then 1 else 0 end as new_3_4_year_ago
        , case when created_date::timestamp between fiveyearsago and fouryearsago then 1 else 0 end as new_4_5_year_ago
        , case when created_date::timestamp < fiveyearsago then 1 else 0 end as existing_users_prior_to_5_years_ago
        from users_df
    join yoy_start
        on 1=1
)
, summary_stats as (
    --identify summary stats for the YOY growth
    --see `yoy_growth_pct` for the final answer
    select sum(new_0_1_year_ago) as total_new_users_0_1_year_ago --unnecessary for calculation, just interesting
        , sum(new_1_2_year_ago) as total_new_1_2_year_ago
        , sum(new_2_3_year_ago) as total_new_2_3_year_ago
        , sum(new_3_4_year_ago) as total_new_3_4_year_ago
        , sum(new_4_5_year_ago) as total_new_4_5_year_ago
        , sum(existing_users_prior_to_5_years_ago) as total_prior_users
        , count(*) as total_users_this_year --all users based on our data
        , total_prior_users
            +total_new_4_5_year_ago
            +total_new_3_4_year_ago
            +total_new_2_3_year_ago
            +total_new_1_2_year_ago 
            as total_users_last_year
        , total_prior_users
            +total_new_4_5_year_ago
            +total_new_3_4_year_ago
            +total_new_2_3_year_ago
            as total_users_two_years_ago
        , total_prior_users
            +total_new_4_5_year_ago
            +total_new_3_4_year_ago
            as total_users_three_years_ago
        , total_prior_users
            +total_new_4_5_year_ago
            as total_users_four_years_ago
        , total_prior_users
            as total_users_five_years_ago
        , (total_users_this_year-total_users_last_year)/total_users_last_year as yoy_growth_last_year_to_this_year
        , (total_users_last_year-total_users_two_years_ago)/total_users_two_years_ago as yoy_growth_two_years_ago_to_last_year
        , (total_users_two_years_ago-total_users_three_years_ago)/total_users_three_years_ago as yoy_growth_three_years_ago_to_two_years_ago
        , (total_users_three_years_ago-total_users_four_years_ago)/total_users_four_years_ago as yoy_growth_four_years_ago_to_three_years_ago
        , (total_users_four_years_ago-total_users_five_years_ago)/total_users_five_years_ago as yoy_growth_five_years_ago_to_four_years_ago
    from user_details
)
--gather final result of yoy growth over the last 5 years
--and present findings as a percent
--max data currently is 9/11/2024
select yoy_growth_last_year_to_this_year*100 as yoy_growth_pct_Sept_2023_2024
    , yoy_growth_two_years_ago_to_last_year*100  as yoy_growth_pct_Sept_2022_2023
    , yoy_growth_three_years_ago_to_two_years_ago*100 as yoy_growth_pct_Sept_2021_2022
    , yoy_growth_four_years_ago_to_three_years_ago*100 as yoy_growth_pct_Sept_2020_2021
    , yoy_growth_five_years_ago_to_four_years_ago*100 as yoy_growth_pct_Sept_2019_2020
from summary_stats
