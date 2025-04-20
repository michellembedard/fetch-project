--OPTION 1B: REMOVE USER RESTRICTION
with de_duped_products as (
    --next, de-duplicate barcodes (based on part 1 exploration, this is something which must be fixed)
    --keep the rows with the most data
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
        --per brand, identify the number of distinct receipts scanned
        --only select the top 5-most receipts
        select p.brand
            , count(distinct t.RECEIPT_ID) as unique_receipts
        from transactions_df t
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
--identify the number of distinct receipt scans by brand for all transactions (as we assume that this will mirror the 21+ age group)
--and pull the top 5 (including anything tied for 5th place)
select p.brand
    --, count(t.RECEIPT_ID) as receipts
    , count(distinct t.RECEIPT_ID) as unique_receipts
from transactions_df t
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
    --, count(t.RECEIPT_ID) as receipts
    , count(distinct t.RECEIPT_ID) as unique_receipts
from transactions_df t
left join de_duped_products p 
    on t.barcode=p.barcode
where t.barcode is not null
group by p.brand
having p.brand is not null
order by count(distinct t.RECEIPT_ID) desc
limit 5
*/