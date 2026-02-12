#bin/bash

brew install --cask snowflake-snowsql

# -a account -u user -r role -w warehouse -d db -s schema
# to figure the information run in snowflake dashboard sql:
# SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_REGION(), CURRENT_ROLE();

snowsql -a cr56839-VVYELLG \
        -u CAIOHANDRADELIMA \
        -r ACCOUNTADMIN \
        -w COMPUTE_WH \
        -d trading_ANALYTICS \
        -s BRONZE \
        -o log_level=DEBUG

        Otr@conta1Health