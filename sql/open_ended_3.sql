with yoy_start as (
    --assumption is that this is a random sample of user data
    --do rolling year from the max date since we believe we have just a sample that ended in the past
    select max(created_date) as current_date_of_data
    from users_df
)
, user_details as (
    --identify key information about the user
    --including flags indicating when they became part of the user base
    --assumption is that all users provided are still part of our user population 
    select created_date
        , current_date_of_data
        --, dateadd(year,-1,current_date_of_data) as oneyearago --redshift syntax
        --, dateadd(year,-2,current_date_of_data) as twoyearsago --redshift syntax
        , current_date_of_data::TIMESTAMP - interval 1 year as oneyearago
        , current_date_of_data::TIMESTAMP - interval 2 year as twoyearsago
        , case when created_date::timestamp between oneyearago and current_date_of_data then 1 else 0 end as new_this_year
        , case when created_date::timestamp between twoyearsago and oneyearago then 1 else 0 end as new_last_year
        , case when created_date::timestamp < twoyearsago then 1 else 0 end as existing_users_prior_to_2_years_ago
        from users_df
    join yoy_start
        on 1=1
)
--identify summary stats for the YOY growth
--see `yoy_growth_pct` for the final answer
select sum(new_this_year) as total_new_users_this_year
    , sum(new_last_year) as total_new_users_last_year
    , sum(existing_users_prior_to_2_years_ago) as total_prior_users
    , count(*) as total_users_this_year
    , total_new_users_last_year+total_prior_users as total_users_this_last_year
    , (total_users_this_year-total_users_this_last_year)/total_users_this_last_year as yoy_growth
    , yoy_growth*100 as yoy_growth_pct
from user_details
