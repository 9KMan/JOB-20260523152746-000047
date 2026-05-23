# Gold Layer

The Gold layer contains the star schema with fact and dimension tables.

## Models

### Fact Tables
- `fct_daily_aggregates` - Daily aggregates per source

### Dimension Tables
- `dim_sources` - Source dimension
- `dim_time` - Time dimension (pre-generated for 5 years)
- `dim_customers_scd2` - Customer dimension with SCD Type 2
- `dim_products_scd2` - Product dimension with SCD Type 2

## SCD Type 2

Slowly Changing Dimensions Type 2 tracks historical changes:
- `effective_date` - When the record became active
- `expiry_date` - When the record was replaced
- `is_current` - Whether this is the current record

## Usage

Connect BI tools (Metabase, Superset) directly to the Gold layer tables.
