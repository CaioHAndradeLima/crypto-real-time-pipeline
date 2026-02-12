{{
  config(
    materialized='incremental',
    unique_key=['station_id', 'month'],
    incremental_strategy='delete+insert'
  )
}}

select
    station_id,
    date_trunc('month', observation_date) as month,

    sum(total_precip_mm) as monthly_precip_mm,
    count(*) as days_with_data,
    sum(iff(was_raining, 1, 0)) as rainy_days

from {{ ref('trading_daily_rain') }}

{% if is_incremental() %}
where date_trunc('month', observation_date) >= (
    select max(month) from {{ this }}
)
{% endif %}

group by
    station_id,
    date_trunc('month', observation_date)
