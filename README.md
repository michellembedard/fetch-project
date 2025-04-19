# fetch-project

## Part 1: explore the data
- Review the unstructured csv files and answer the following questions with code that supports your conclusions:
1. Are there any data quality issues present?
2. Are there any fields that are challenging to understand?

<details>
<summary>ANSWER:</Summary>

1. Are there any data quality issues present?
    - Within transactions, there is missing final sale and final quantity data
        - These both appear to be business-critical data points, so it is concerning that these are missing. I would like to connect with other data team or software engineering members to gather historical context and learn if there are any assumptions we can make around the missing data.
    - There are not always barcodes for transactions
        - This is not concerning since I imagine that there are niche stores, etc that would be selling products without a traditional barcode.
            - However, if there is an automatic process to create a barcode in the data if one does not exist, then this is cause for concern and something I would want to reach out to developers to understand further.
    - There are products without barcodes
        - This is not concerning since I assume that they contain manually entered product information that has not been incorporated into an automatic system which generates the barcode.
    - There is missing data across the board.
        - My assumption is that only a sample of transactions, users, and products was provided and that there is more data available.
        
2. Are there any fields that are challenging to understand?
    - It is challenging to understand the transactions `FINAL_SALE` field.
        - It is unclear whether this is a sale amount for the full line item, a sale amount which must be multiplied by the quantity, or some total sale amount.
            - I am assuming this is the sale amount for the full line item in my analysis.
    - It is challenging to understand the transactions `FINAL_QUANTITY` field.
        - It is unclear what "zero" means.
            - I am assuming that this is a field which was added later and never backfilled. Any receipts prior to the app update which added the quantity was imputed with a text field of "zero". 
            - Since 1 is the most common quantity amount, I will assume that any "zero" values can reasonably be assumed to have a true quantity of 1.

- More information can be found in `src/part1__data_exploration.py` and `src/part1__readme.md`
</details>

## Part 2: provide SQL queries
- Answer three of the following questions with at least one question coming from the closed-ended and one from the open-ended question set. Each question should be answered using one query.
### 2A Closed-ended questions:
1. What are the top 5 brands by receipts scanned among users 21 and over?
2. What are the top 5 brands by sales among users that have had their 3. account for at least six months?
3. What is the percentage of sales in the Health & Wellness category by generation?
### 2B Open-ended questions: for these, make assumptions and clearly state them when answering the question.
1. Who are Fetch’s power users?
2. Which is the leading brand in the Dips & Salsa category?
3. At what percent has Fetch grown year over year?

<details>
<summary>ANSWER:</Summary>

- Questions Chosen:
    - C1. What are the top 5 brands by receipts scanned among users 21 and over?
    - O2. Which is the leading brand in the Dips & Salsa category?
    - O3. At what percent has Fetch grown year over year?
- Please see assumptions in `src/part2__run_sql.py` file
    - There are also variations on C1 and O3 based on differing assumptions I might make, specifically if there was more data.
- Queries are reproduced in the expandable sections below


<details>
<summary>C1. What are the top 5 brands by receipts scanned among users 21 and over?</Summary>

```
with users_21_up as (
    --first identify the users 21 and over.
    select *
        , today() as todaysdate
        , todaysdate::TIMESTAMP - interval 21 year as yearsago21
        --, dateadd(year,-21,getdate()) as yearsago21 --redshift syntax
        , case when BIRTH_DATE::TIMESTAMP is null then 1 else 0 end as missing_birthdate
        , case when BIRTH_DATE::TIMESTAMP<=yearsago21 then 1 else 0 end as atleast21_flag
    from users_df
    where missing_birthdate=0
        and atleast21_flag=1
)
, de_duped_products as (
    --next, de-duplciate barcodes (based on part 1 exploration, this is something which must be fixed)
    --the the rows with the most data
    --and if that is tied, use the row with brand info
    select *
        , case when CATEGORY_1 is not null then 1 else 0 end
            + case when CATEGORY_2 is not null then 1 else 0 end
            + case when CATEGORY_3 is not null then 1 else 0 end
            + case when CATEGORY_4 is not null then 1 else 0 end
            + case when MANUFACTURER is not null then 1 else 0 end
            + case when BRAND is not null then 1 else 0 end
            as cols_with_info
        , case when BRAND is not null then 1 else 0 end as brand_w_info
        , row_number() over(partition by barcode order by cols_with_info desc, brand_w_info desc) as keep_rn
    from products_df
    where barcode is not null
    qualify keep_rn = 1

)
, top5quantity as (
    --next, identify the quantity of the 5th most receipt
    --This will allow us to resolve ties at 5th place
    select min(unique_receipts) as unique_receipts_at_5th_place
    from (
        --per brand, identify the number of distinct recipts scanned
        --only select the top 5-most reciepts
        select p.brand
            , count(distinct t.RECEIPT_ID) as unique_receipts
        from transactions_df t
        join users_21_up u
            on t.user_id=u.id
        left join de_duped_products p 
            on t.barcode=p.barcode
        where t.barcode is not null
        group by p.brand
        having p.brand is not null
        order by count(distinct t.RECEIPT_ID) desc
        limit 5
    )
)
--gather the final result
--identify the number of distinct reciept scans by brand for users 21+
--and pull the top 5 (including anything tied for 5th place)
select p.brand
    --, count(t.RECEIPT_ID) as reciepts
    , count(distinct t.RECEIPT_ID) as unique_receipts
from transactions_df t
join users_21_up u
    on t.user_id=u.id
left join de_duped_products p 
    on t.barcode=p.barcode
where t.barcode is not null
group by p.brand
having p.brand is not null
    and unique_receipts>=(select unique_receipts_at_5th_place from top5quantity)
order by count(distinct t.RECEIPT_ID) desc


--I believe these ties should be considered
--However, if this is not necessary, the following should be run as the final result
/*
select p.brand
    --, count(t.RECEIPT_ID) as reciepts
    , count(distinct t.RECEIPT_ID) as unique_receipts
from transactions_df t
join users_21_up u
    on t.user_id=u.id
left join de_duped_products p 
    on t.barcode=p.barcode
where t.barcode is not null
group by p.brand
having p.brand is not null
order by count(distinct t.RECEIPT_ID) desc
limit 5
*/
```
</details>

<details>
<summary>O2. Which is the leading brand in the Dips & Salsa category?</Summary>

```
with de_duped_products as (
    --de-duplciate barcodes (based on part 1 exploration, this is something which must be fixed)
    --the the rows with the most data
    --and if that is tied, use the row with brand info
    select *
        , case when CATEGORY_1 is not null then 1 else 0 end
            + case when CATEGORY_2 is not null then 1 else 0 end
            + case when CATEGORY_3 is not null then 1 else 0 end
            + case when CATEGORY_4 is not null then 1 else 0 end
            + case when MANUFACTURER is not null then 1 else 0 end
            + case when BRAND is not null then 1 else 0 end
            as cols_with_info
        , case when BRAND is not null then 1 else 0 end as brand_w_info
        , row_number() over(partition by barcode order by cols_with_info desc, brand_w_info desc) as keep_rn
    from products_df
    where barcode is not null
    qualify keep_rn = 1

)
, dips_and_salsa as (
    --only gather the category we care about
    --category2 was identified via earlier exploration
    select *
    from de_duped_products
    where CATEGORY_2='Dips & Salsa'
)
, transaction_details_by_brand as (
    --only for dip and salsa transactions, identify the brand
    --basd on on assumptions, make final quanity "zero" map to 1
    --based on assumptions, replace blanks with 0s for final sale
    select t.receipt_id
        , t.purchase_date
        , replace(t.final_sale,' ','0')::decimal as final_sale
        , replace(t.final_quantity,'zero','0')::decimal as final_quantity_
        , replace(t.final_quantity,'zero','1')::decimal as final_quantity_imputed
        , t.final_sale as final_sale_raw
        , t.final_quantity as final_quantity_raw
        , ds.brand
    from transactions_df t
    join dips_and_salsa ds
        on t.barcode=ds.barcode
        --we can join becase if we left join then we will not get any other useful information
        --we need the barcode to set up a proper connection, as nulls will give us no information about if a dip & salsa was purchased
)
, median_salsa_dip_sale as (
    --based on transactions we have, find the median dip and salsa final sale amount
    --this will be used for imputing final sale when nothing else is known
    select median(final_sale) med
    from transaction_details_by_brand
    where final_sale is not null
)
, imputed_details as (
    --take transaction_details_by_brand and impute the median sales amount where no sales amount exists
    select *
        , (case when final_sale_raw=' ' 
            then (select med from median_salsa_dip_sale)::varchar 
            else final_sale_raw 
            end)::decimal 
            as final_sale_imputed
    from transaction_details_by_brand
)
--gather the final result
--identify the top salsa and dip brand, based on total sales
--assuming median salsa and dip sales value when sales value is not prsent
select brand
    , sum(final_sale_imputed) as total_sales
    , sum(final_quantity_imputed) as total_quantity
from imputed_details
--where brand is not null
group by brand
order by total_sales desc
limit 1
--top result is not a null brand
--if it was, we could add `where brand is not null`, 
--or use these findings to inform the business that missing data is causing a major concern with findings
--I would favor seeing that a null is the most common response rather than filtering it out so that addtitional data discovery/work with software engineers could be performed
```
</details>

<details>
<summary>O3. At what percent has Fetch grown year over year?</Summary>

```
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
```
</details>

</details>

## Part 3: communicate with stakeholders
- Construct an email or slack message that is understandable to a product or business leader who is not familiar with your day-to-day work. Summarize the results of your investigation. Include:
    - Key data quality issues and outstanding questions about the data
    - One interesting trend in the data
        - Use a finding from part 2 or come up with a new insight
    - Request for action: explain what additional help, info, etc. you need to make sense of the data and resolve any outstanding issues

<details>
<summary>ANSWER:</Summary>

Hi team,

I am currently working on building an understanding of our user and transaction growth.</br>
Though my analysis, I have a some interesting initial findings as well as a few data quality callouts and outstanding questions.</br>

</br>
With my sample of data, I see we have <b>18% YOY growth</b>. </br>
The <b>age of the users at signup time has increased in the last year</b>, compared to prior year.</br>
<br>
My assumption is that our target market should be a consistent or younger age over time so that we can incorporate younger shoppers into our user base. This would set us up for success if we have fully captured the mid-age market in the future.</br>
Should we consider creating a campaign to target younger audiences?</br>
If we would like our target market to be about 40 years old, then we are hitting our desired user-base.</br>
Please let me know if you would like additional findings related to user growth.</br>

</br>
</br>

- Data quality callouts: 
    - There are multiple barcodes in the products data. Without a modified date, I am uncertain what is the most updated product information for a barcode.
    - There is both missing price and missing quantity data for numerous transaction records
    - There appears to be missing data:
        - There are transactions which tie to users who do not exist in our user data
        - There are transactions without barcodes
        - There are transactions which tie to barcodes that do not exist in our product data
- Outstanding questions:
    - Can you direct me to the teams who can provide access to the full dataset?
        - Based on my findings, I believe I am missing users and missing products in my current dataset. 
        - I also assume I am missing transactions due to the low quantity of data. This does not allow for a full picture of user engagement and would be important to understand who is a power user and how best to target users.
    - Are there standard assumptions which should be made to fill in the gaps?
        - Specifically, where there is no "final sales" information, and no "final quantity" information ("zero"), do we have standard assumptions? These appear to be highly important data points and I do not want to make assumptions that differ from the rest of the team.
        - I believe this data is missing either due to (1) bad receipt scans, or (2) product enhancements where data was not captured until a specific point in time, but cannot yet validate these assumptions.

</br>  
</br>     
<b>Request for Action:</b></br>

1. Can you send me either developer documenation or people who I can connect with to further understand the missing "final sales" and "final quantity" data?</br>
2. Can you please connect me with the teams who can provide me with more data access?</br>

</br>
Thank you so much!</br>
Michelle Bedard
</details>