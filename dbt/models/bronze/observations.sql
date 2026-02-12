{{ config(materialized='view') }}

select
    station_id,
    station_name,
    observation_time,
    temperature_c,
    dewpoint_c,
    relative_humidity,
    wind_direction_deg,
    wind_speed_kmh,
    wind_gust_kmh,
    barometric_pressure_pa,
    visibility_m,
    precipitation_last_3h_mm,
    trading_description,
    longitude,
    latitude,
    elevation_m,
    payload,
    ingested_at
from trading.bronze.observations
