{{
  config(
    materialized='incremental',
    unique_key='month',
    incremental_strategy='delete+insert'
  )
}}

with region_daily as (

    select
        observation_date,
        max(iff(was_raining, 1, 0)) = 1 as region_was_raining
    from {{ ref('trading_daily_rain') }}

    {% if is_incremental() %}
    where observation_date >= (
        select max(month) from {{ this }}
    )
    {% endif %}

    group by observation_date
)

select
    date_trunc('month', observation_date) as month,
    sum(iff(region_was_raining, 1, 0)) as rainy_days_in_month,
    count(*) as total_days_observed

from region_daily
group by date_trunc('month', observation_date)
order by month
