---

# Phase: Data Understanding

## Task: Collect Initial Data

### Output: Initial Data Collection Report

The initial data has already been collected, and is stored in the `data` folder together with the _data dictionary_ (i.e. descriptions or each column/feature in each dataset) in the `data/data_dictionary` folder.

The datasets are:

- `vg_charts.csv`
- `vg_developers.csv`
- `vg_publishers.csv`
- `vg_geo_cities.csv`
- `vg_geo_countries.csv`

These files are sufficient for the planned dashboard because `vg_charts.csv` contains the game, platform, genre, publisher, developer, release-date, critic-score, and regional-sales measures needed for the main questions. The other four files provide optional headquarters and coordinate enrichment for publishers and developers. No additional dataset is required for the current scope, although customer-level geography, prices, reviews, and demographics are not available.

## Task: Describe Data

### Output: Data Description Report

- Here you need to describe the data that has been acquired, including the format of the data, the quantity of data (for example, the number of records (rows) and fields (columns) in each dataset/table), the identities of the fields, and any other surface features which have been discovered.
- You also have to evaluate whether the data acquired satisfies the relevant requirements (or if you need to collect more data).

#### Dataset inventory

| Dataset                |   Rows | Columns | Purpose and fields                                                                                                                                                                                                                              |
| ---------------------- | -----: | ------: | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `vg_charts.csv`        | 64,016 |      14 | Main fact table: `img`, `title`, `platform`, `genre`, `publisher`, `developer`, `critic_score`, `total_sales`, `na_sales`, `jp_sales`, `pal_sales`, `other_sales`, `release_date`, and `last_update`. Sales are measured in millions of copies. |
| `vg_developers.csv`    |    731 |       3 | Developer reference table: `developer`, headquarters `city`, and `country`.                                                                                                                                                                     |
| `vg_publishers.csv`    |    889 |       3 | Publisher reference table: `publisher`, headquarters `city`, and `country`.                                                                                                                                                                     |
| `vg_geo_cities.csv`    | 23,412 |       3 | City lookup containing `city`, `latitude`, and `longitude`.                                                                                                                                                                                     |
| `vg_geo_countries.csv` |    262 |       5 | Country lookup containing country name, ISO2 and ISO3 codes, latitude, and longitude.                                                                                                                                                           |

The files are comma-separated CSV files. The main table contains 81 platforms, 20 genres, 39,798 title strings, 3,383 publishers, and 8,862 developer strings. It has no completely duplicated rows. The supporting tables also have no completely duplicated rows. Most categorical fields are strings; sales and critic scores are floating-point values. Dates are stored as strings and must be parsed before time-based analysis. The country coordinate fields are read as strings in the supplied file and should be converted only after validating their contents.

#### Initial observations

Several attributes contain a large number of missing values. Approximately 70.4% of the values in the `total_sales` column and 89.6% of the values in the `critic_score` column are missing.

The regional sales attributes, as well as `release_date`, `last_update`, and `developer`, should also be examined for missing values and their potential effect on later analyses.

The main dataset contains repeated game titles across different platforms. Therefore, the number of records does not represent the number of unique games. A single game title may appear in multiple records when it was released on multiple platforms.

The date attributes require conversion to datetime types for time-based analysis. The country coordinate fields should also be checked and cleaned before being used in geographical visualizations.

The sales data is described in the project glossary as physical game copies sold. Consequently, it may not represent the entire video game market, including digital downloads.

#### Data suitability

The available datasets appear suitable for addressing the main objectives defined in the Business Understanding phase.

The main dataset contains the attributes required to investigate:

- Regional market preferences
- Popular genres and platforms
- Sales performance across regions
- Sales trends over release years
- Popular game titles
- Publisher performance
- Differences in platform popularity over time

The high proportion of missing sales values may limit the reliability of analyses involving sales. Missing release dates may also affect analyses of historical trends and changes in popularity over time. Missing critic scores limit the number of games that can be included in analyses comparing review scores with sales performance.

The sales data may not fully represent the overall video game market because it is described as physical game copies sold. Digital sales and other forms of market activity may not be included.

The developer and publisher datasets contain city and country information that can potentially be joined with the geographical city and country datasets. These joins may support geographical analysis of developer and publisher locations.

However, the supporting datasets cover only a subset of the unique developers and publishers in the main dataset. Join coverage should therefore be evaluated, and name standardization may be necessary to improve matching between datasets.

Overall, the available attributes appear sufficient for developing the planned dashboard and conducting the initial exploratory analyses. Whether additional data is required will depend on the results of further data quality checks and the specific analyses selected for the dashboard.

#### Conclusion

The collected data provides a useful starting point for exploratory analysis and includes the main attributes required to address the project’s business objectives.

However, further data cleaning and validation will be necessary before conducting detailed analyses, particularly those involving sales, dates, critic scores, geographical coordinates, or joins between the main and supporting datasets. The limitations of the sales data, including the possible absence of digital sales, should also be considered when interpreting the results.

## Task: Explore Data

### Output: Data Exploration Report

- Here you need to describe the results of this task, including first findings or initial hypothesis and their impact on the remainder of the project:
  - This task addresses the data mining questions (under `Phase: Business Uuderstanding -> Task: Determine Data Mining Goals`) using querying, visualization, and reporting techniques.
  - These include distribution of key attributes (e.g. sales, regions, genres, platforms, etc.) relationships between pairs of attributes, results of simple aggregations, properties of significant sub-populations (e.g. groupings of genres, platforms, etc.), and simple statistical analyses (counts, sums, means, standard deviations, etc.).
  - These analyses may directly address the data mining goals; they may also contribute to or refine the data description and quality reports, and feed into the transformation (e.g. merging, feature engineering) and other data preparation steps (e.g. cleaning) needed for further analysis.
- If appropriate, include graphs and plots to indicate data characteristics that suggest further examination of interesting data subsets.

#### Initial exploration findings

The calculations below use the non-missing values for each measure. A title can occur on multiple platforms, so title rankings aggregate its platform rows while platform rankings treat each chart row as one title-platform observation.

**Regional sales and platform preferences.** Among the 18,922 rows with `total_sales`, global sales sum to 6,605.91 million copies, with a mean of 0.349 and standard deviation of 0.807 million. Regional coverage is lower: North America has 12,637 observed rows and 3,345.52 million copies; Japan has 6,726 and 687.94 million; Europe/Africa (`pal_sales`) has 12,824 and 1,916.83 million; and Other has 15,128 and 651.12 million. North America is the largest observed market, but this is a covered-record result rather than a claim about all games.

| Region        | Highest-sales platform | Sales (millions) | Highest-sales genre | Sales (millions) |
| ------------- | ---------------------- | ---------------: | ------------------- | ---------------: |
| North America | X360                   |           528.40 | Sports              |           607.47 |
| Japan         | PS                     |            88.32 | Role-Playing        |           130.56 |
| Europe/Africa | PS3                    |           302.22 | Action              |           342.52 |
| Other         | PS2                    |           153.94 | Sports              |           128.19 |

Across observed global sales, PS2 ranks first at 1,027.76 million, followed by X360 at 859.79 million and PS3 at 839.70 million. Sports is the highest-sales genre at 1,187.51 million, followed by Action at 1,125.89 million and Shooter at 995.50 million. These totals are useful dashboard defaults, but they are affected by missing sales and by unequal numbers of rows per platform and genre.

**Time trends.** Of the 64,016 rows, 56,965 have a valid release date; non-missing dates parse successfully and range from 1971 to 2024. Restricting the annual sales comparison to years with at least 50 dated rows, 2008 has the highest observed global sales at 538.11 million across 2,936 rows, followed by 2009 at 495.36 million and 2010 at 454.02 million. Sales fall sharply in the latest years, but those years also contain incomplete sales coverage, so the data cannot establish that the industry is declining. The dashboard should show record counts and allow users to exclude incomplete tail years.

**Genres, titles, and publishers.** The highest aggregated title totals are Grand Theft Auto V (64.29 million across eight platform rows), Call of Duty: Black Ops (30.99 million across eight), and Call of Duty: Modern Warfare 3 (30.71 million across five). For publisher comparisons, a minimum of 20 rows was used. Activision has the largest observed total among those publishers at 722.77 million across 1,582 rows, followed by Electronic Arts at 644.13 million across 1,619 rows and EA Sports at 485.66 million across 804 rows. A publisher's total alone does not measure consistency, so the dashboard should show row count, mean sales, standard deviation, and coefficient of variation together. Small publishers must not be ranked against large publishers without a minimum-observation filter.

**Platform and genre specialization.** Some small platforms appear concentrated in one genre, but the strongest concentrations often come from platforms with very few rows: BBCM, C128, FDS, and Aco each have a single observed row. DSi has 73 rows, 96.1% of which are Misc, and BRW has 59 rows with 93.7% Misc. These are signals for exploration, not evidence of a general platform strategy. A minimum row threshold should be applied before describing specialization.

**Regional differences.** The largest observed regional imbalances include Guitar Hero III: Legends of Rock on Wii (3.04 million North America versus 0.00 Japan), Pro Evolution Soccer 2008 on PS2 (0.05 North America versus 2.93 Other), and Call of Duty: Advanced Warfare on X360 (2.81 North America versus 0.00 Japan). Zero values are recorded sales values, whereas blank values are unknown; this distinction must be retained in the dashboard.

These findings imply that the next phase should parse dates, expose coverage counts, keep missing measures as missing, aggregate platform rows explicitly for title-level views, and add minimum-sample filters for publisher and platform comparisons.

## Task: Verify Data Quality

### Output: Data Quality Report

Here you need to list the results of the data quality verification, i.e. if quality problems exist, possible solutions to data quality issues, etc.

This includes examining the quality of the data, addressing questions
such as:

- Is the data complete (i.e. does it cover all the cases required, or will you need to collect more data)?
- Is it correct, or does it contain errors and, if there are errors, how common are they?
- Are there missing values in the data? If so, how are they represented, where do they occur, and how common are they?

#### Completeness and missing values

Missing values are represented as blank CSV fields and are read by pandas as `NaN`. The following table reports both counts and percentages of the full table where relevant.

| Dataset / field          | Missing | Percentage |
| ------------------------ | ------: | ---------: |
| `vg_charts.developer`    |      17 |      0.03% |
| `vg_charts.critic_score` |  57,338 |     89.57% |
| `vg_charts.total_sales`  |  45,094 |     70.44% |
| `vg_charts.na_sales`     |  51,379 |     80.26% |
| `vg_charts.jp_sales`     |  57,290 |     89.49% |
| `vg_charts.pal_sales`    |  51,192 |     79.97% |
| `vg_charts.other_sales`  |  48,888 |     76.37% |
| `vg_charts.release_date` |   7,051 |     11.01% |
| `vg_charts.last_update`  |  46,137 |     72.07% |
| `vg_developers.city`     |       5 |      0.68% |
| `vg_publishers.city`     |     147 |     16.54% |
| `vg_publishers.country`  |       1 |      0.11% |

All other fields in the five datasets are complete according to the CSV profile. The high missingness in sales means that aggregations use only a subset of records and can be biased toward records for which sales were collected. Critic scores are also unsuitable as a general quality measure because only 6,678 rows contain a score. Missing release dates prevent complete time-series coverage.

#### Correctness and consistency checks

- No completely duplicated rows were found in any dataset. Repeated titles in `vg_charts.csv` are expected because the table records releases across platforms; they are not automatically duplicates.
- No negative values were found in the sales or critic-score fields. The observed critic scores range from 1 to 10, as documented, and sales values range from 0 to 20.32 million.
- For the 2,222 rows with complete global and regional sales, the largest absolute difference between `total_sales` and the sum of the four regional fields is 0.02 million, and the mean absolute difference is 0.004 million. This is acceptably close for rounded source values.
- All 56,965 non-missing release dates parse successfully. The observed year range is 1971–2024.
- No leading or trailing whitespace was found in publisher, platform, genre, or title values. Seventeen developer values contain leading or trailing whitespace and should be normalized before joining to the developer reference table. Case-folding also reveals some title variants, so title aggregation should use a documented normalization rule and retain the original display title.
- The reference tables are not guaranteed to cover every chart-table publisher or developer. Joins should therefore be left joins, with unmatched headquarters retained as unknown rather than dropped.

#### Recommended handling

The data is adequate for an exploratory dashboard but not complete enough for population-level sales estimates. In Data Preparation, parse `release_date` and `last_update` as dates, strip whitespace from join keys, preserve missing numerical measures as missing, and use explicit `Unknown` categories only for categorical display fields. Sales summaries should state their non-missing denominator and include coverage counts. Rows with missing sales should be excluded from sales totals, not treated as zero; rows with missing dates should be excluded from annual trend calculations. Critic-score analysis should be presented as a separate, small covered subset. Publisher and platform consistency/specialization views should require a minimum number of observations and should display the underlying count.
