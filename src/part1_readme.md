# Part 1
## Are there any data quality issues present?
    - Within transactions, there is missing final sale and final quantity data
        - These both appear to be business-critical data points, so it is concerning that these are missing. I would like to connect with other data team or software engineering members to gather historical context and learn if there are any assumptions we can make around the missing data.
    - There are not always barcodes for transactions
        - This is not concerning since I imagine that there are niche stores, etc that would be selling products without a traditional barcode.
            - However, if there is an automatic process to create a barcode in the data if one does not exist, then this is cause for concern and something I would want to reach out to developers to understand further.
    - There are products without barcodes
        - This is not concerning since I assume that they contain manually entered product information that has not been incorporated into an automatic system which generates the barcode.
    - There is missing data across the board.
        - My assumption is that only a sample of transactions, users, and products was provided and that there is more data available.
## Are there any fields that are challenging to understand?
    - It is challenging to understand the transactions `FINAL_SALE` field.
        - It is unclear whether this is a sale amount for the full line item, a sale amount which must be multiplied by the quantity, or some total sale amount.
            - I am assuming this is the sale amount for the full line item in my analysis.
    - It is challenging to understand the transactions `FINAL_QUANTITY` field.
        - It is unclear what "zero" means.
            - I am assuming that this is a field which was added later and never backfilled. Any receipts prior to the app update which added the quantity was imputed with a text field of "zero". 
            - Since 1 is the most common quantity amount, I will assume that any "zero" values can reasonably be assumed to have a true quantity of 1.