{{ config(materialized='table') }}

with base as (

    select
        station_id,
        station_name,

        -- Normalize timestamp
        observation_time::timestamptz as observation_time_utc,
        date_trunc('day', observation_time::timestamptz) as observation_date,

        -- Measurements
        temperature_c,
        dewpoint_c,
        relative_humidity,

        wind_direction_deg,
        wind_speed_kmh,
        wind_gust_kmh,

        barometric_pressure_pa,
        visibility_m,

        precipitation_last_3h_mm,

        (
          coalesce(precipitation_last_3h_mm, 0) > 0
          OR coalesce(trading_description, '') ilike '%rain%'
        ) as is_raining,

        trading_description,

        longitude,
        latitude,
        elevation_m,

        ingested_at

    from {{ ref('observations') }}

    where observation_time is not null
)

select *
from base
