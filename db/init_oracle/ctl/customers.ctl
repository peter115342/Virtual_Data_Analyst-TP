OPTIONS (SKIP=1)
LOAD DATA
INFILE '/container-entrypoint-initdb.d/data/customers.csv'
INTO TABLE customers
FIELDS TERMINATED BY ','
TRAILING NULLCOLS
(
    customer_id,
    customer_name,
    customer_type,
    credit_terms_days,
    primary_freight_type,
    account_status,
    contract_start_date DATE "YYYY-MM-DD",
    annual_revenue_potential
)