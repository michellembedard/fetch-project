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

ANSWER:
Questions Chosen:
C1. What are the top 5 brands by receipts scanned among users 21 and over?
O2. Which is the leading brand in the Dips & Salsa category?
O3. At what percent has Fetch grown year over year?

## Part 3: communicate with stakeholders
- Construct an email or slack message that is understandable to a product or business leader who is not familiar with your day-to-day work. Summarize the results of your investigation. Include:
    - Key data quality issues and outstanding questions about the data
    - One interesting trend in the data
        - Use a finding from part 2 or come up with a new insight
    - Request for action: explain what additional help, info, etc. you need to make sense of the data and resolve any outstanding issues

ANSWER:
