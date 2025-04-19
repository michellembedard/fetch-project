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