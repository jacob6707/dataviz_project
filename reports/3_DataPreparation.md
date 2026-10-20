# Phase: Data Preparation

## Task: Select Data

### Output: Rationale for Inclusion/Exclusion

The main dataset `vg_charts.csv` contains information about games, platforms, genres, publishers, developers, release dates, critic scores, and regional sales. All 14 original attributes were initially retained because they are relevant to the planned dashboard or may be useful as additional information.

Rows with missing sales values or missing release dates were not removed from the main dataset. These rows can still be used for analyses based on game counts, platforms, genres, publishers, and developers. Sales-based visualizations only use observations where the relevant sales value is available.

The datasets `vg_developers.csv` and `vg_publishers.csv` were selected to add optional information about the headquarters of developers and publishers. The country dataset `vg_geo_countries.csv` was selected to add country codes and coordinates where the country could be matched reliably.

The city dataset `vg_geo_cities.csv` was not joined automatically. A city name alone is not sufficient to identify a unique location because the same city name can occur in different countries. The city data may be used later if a reliable country and city matching procedure is added.

The data preparation started with 64,016 rows and 14 attributes in the main game dataset. The prepared game table still contains 64,016 game-platform rows. No original game rows were removed during the preparation process.

## Task: Clean Data

### Output: Data Cleaning Report

The categorical columns were cleaned by removing surrounding whitespace. Empty strings were converted to missing values. The original spelling and capitalization of display labels were preserved.

The columns `release_date` and `last_update` were converted from strings to datetime values. The sales columns and `critic_score` were converted to numeric values. No failed date conversions or failed numeric conversions were recorded in the executed notebook.

Missing sales values were kept as missing values (`NaN`). They were not replaced with zero because a missing value means that no sales information is available, not necessarily that no copies were sold.

Repeated `title` and `platform` combinations were counted and flagged for further investigation. They were not automatically deleted because repeated records may contain valid observations or differences that are not visible in the title and platform fields alone.

The following results were obtained during the cleaning process:

- Failed date conversions: 0
- Failed numeric conversions: 0
- Repeated title-platform pairs: 225
- Missing `total_sales` values after cleaning: 45,094

Temporary lowercase helper keys were created for matching developer and publisher names. These keys were only used during the joins and were removed before the final data was saved.

## Task: Construct Data

### Output: Derived Attributes

The following attributes were created during the data preparation process:

- `record_id`: A unique identifier for each original game-platform row. This is not a unique identifier for a game title because the same title can occur on multiple platforms.
- `release_year`: The year extracted from `release_date`. This attribute is used for yearly comparisons and time-series visualizations.
- `has_total_sales`: A Boolean value indicating whether a total sales value is available for the row.
- `has_sales`: A Boolean value in the regional table indicating whether a sales value is available for a specific region.

Temporary helper attributes were also created for the developer, publisher, and country joins. These attributes were removed from the final game table because they were only needed during data preparation.

### Output: Generated Records

No new games were generated during the data preparation process. The original game-platform records were retained.

A separate regional table was created by reshaping the four regional sales columns into a long format. Each original game-platform row is represented by four regional rows:

- North America
- Japan
- Europe/Africa
- Other

This resulted in 256,064 rows in the regional table:

```text
64,016 original game-platform rows × 4 regions = 256,064 regional rows
```

These rows do not represent new games. They are another representation of the existing regional sales values. Missing sales values remain missing and are not interpreted as zero.

## Task: Integrate Data

### Output: Merged Data

The developer and publisher reference tables were joined to the main game table using normalized company-name keys. The names were stripped of surrounding whitespace and converted to lowercase helper keys for matching.

Left joins were used so that all original game-platform rows remained in the prepared data, even if no matching developer or publisher information was available.

The joins used `validate="m:1"`. This checks that several game rows can match one reference row, but that one game row cannot match several reference rows. This prevents the joins from accidentally increasing the number of game rows.

Ambiguous reference keys were excluded from the joins until they can be checked manually. There were no ambiguous developer reference rows. Two publisher reference rows were identified as ambiguous and were excluded from the publisher join.

The following results were obtained:

- Games matched to a developer headquarters country: 18,515
- Games matched to a publisher headquarters country: 31,596
- Game rows before the joins: 64,016
- Game rows after the joins: 64,016

The country reference table was then used to add ISO3 codes and geographic coordinates for matched developer and publisher countries. The country coordinates describe the headquarters location and do not represent the sales regions.

There were 31,343 game rows with publisher country coordinates. This corresponds to approximately 48.96% of all prepared game rows.

The city coordinate table was not joined by city name alone because city names are not globally unique.

For regional analysis, the columns `na_sales`, `jp_sales`, `pal_sales`, and `other_sales` were reshaped into the columns `region` and `sales_millions`. This makes it easier to filter, group, and compare regional sales in Plotly and Dash.

## Task: Format Data

### Output: Reformatted Data

The prepared game table was formatted so that the identifying attributes and the main sales attributes appear first. The original game labels were retained, while temporary join keys were removed.

The date columns are stored as datetime values, and the numeric columns are stored as numeric values. Missing sales values remain missing.

The regional sales data was changed from wide format to long format.

In the original wide format, each region had its own column:

| title | na_sales | jp_sales | pal_sales | other_sales |
|---|---:|---:|---:|---:|
| Example Game | 2.1 | 0.4 | 1.8 | 0.3 |

In the long format, the region and its sales value are stored in separate columns:

| title | region | sales_millions |
|---|---|---:|
| Example Game | North America | 2.1 |
| Example Game | Japan | 0.4 |
| Example Game | Europe/Africa | 1.8 |
| Example Game | Other | 0.3 |

The two prepared tables were saved as Pickle files in the `data/prepared/` directory. These files can be loaded by the Dash application without repeating the complete cleaning and joining process each time the application starts.

## Main Output

### Output: Datasets

The data preparation process produced the following datasets:

| File | Purpose | Rows | Columns |
|---|---|---:|---:|
| `data/prepared/games_prepared.pkl` | Prepared game-platform data with derived attributes and optional company and country information | 64,016 | 27 |
| `data/prepared/regional_sales_long.pkl` | Regional sales in long format for filtering, grouping, and regional visualizations | 256,064 | 9 |

### Output: Dataset Descriptions

#### `games_prepared.pkl`

`games_prepared.pkl` is the main prepared dataset. Each row represents one game released on one platform.

The table contains the original game information, cleaned date and numeric fields, derived attributes, and optional developer and publisher headquarters information.

The columns are:

```text
record_id
title
platform
genre
publisher
developer
release_date
release_year
total_sales
na_sales
jp_sales
pal_sales
other_sales
img
critic_score
last_update
has_total_sales
developer_city
developer_country
publisher_city
publisher_country
developer_iso3
developer_latitude
developer_longitude
publisher_iso3
publisher_latitude
publisher_longitude
```

The table can be used for analyses involving game and platform counts, genres, publishers, developers, release years, critic scores, worldwide sales, regional sales, and publisher and developer headquarters.

Only available sales values should be included in sales aggregations. Missing sales values should not be treated as zero.

#### `regional_sales_long.pkl`

`regional_sales_long.pkl` contains the regional sales information in long format. Each original game-platform row can produce four regional rows.

The columns are:

```text
record_id
title
platform
genre
publisher
release_year
region
sales_millions
has_sales
```

The table can be used for comparing sales between regions, calculating regional rankings, creating regional bar charts, creating regional time-series charts, and filtering visualizations by region.

A missing value in `sales_millions` means that no sales value was available for that observation. A recorded value of zero remains a real zero and is not changed during preparation.

## Quality Checks

The following checks were completed:

- The number of prepared game rows remained 64,016.
- The `record_id` values remained unique.
- No game rows were lost during the developer, publisher, or country joins.
- The number of missing `total_sales` values was preserved.
- The total sum of the available `total_sales` values was preserved.
- All date conversions completed without failed conversions.
- All numeric conversions completed without failed conversions.
- Repeated title-platform pairs were identified but not automatically deleted.
- Ambiguous reference keys were excluded from the relevant joins.
- The regional table contains exactly four rows for every original game-platform row.
- Temporary join keys were removed before the final tables were saved.

## Limitations and Open Considerations

The following points may be reviewed during later project phases:

- The 225 repeated title-platform pairs need further investigation if they affect a specific dashboard analysis.
- Some developer and publisher names could not be matched to the reference tables.
- Country-name differences may cause some headquarters locations to remain unknown.
- Sales coverage is incomplete. Only 18,922 of the 64,016 rows contain a `total_sales` value, corresponding to approximately 29.56% of the main dataset.
- Sales-based charts should display the number of observations used and should not interpret missing values as zero.
- The prepared Pickle files are generated from the original CSV files and the preprocessing notebook. The team must decide whether these generated files should be included in the final submission or recreated as part of the project setup.
