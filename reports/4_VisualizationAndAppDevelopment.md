## Task: Select Visualization Techniques

### Output: Visualization Techniques

The techniques were chosen to answer the business questions and to respect the
findings of Data Understanding: only about 30 % of records have a global sales
figure, missing sales are unknown (not zero), and small groups can look extreme
by chance. Missing sales are therefore excluded from all sales charts, and the
groups most affected by small samples have a minimum-observation filter.

| Business question                                  | Visualization                                                                                      | Rationale                                                                                                                                                              |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Which regions prefer which platform?               | Heatmap of platform by region, colour = share of the region's sales (%)                            | Shares make regions of very different size comparable.                                                                                                                 |
| What is the most popular platform?                 | Bar chart of top-N platforms, filterable by region                                                 | Bars are the most accurate way to compare totals.                                                                                                                      |
| Which region buys the most?                        | Bar chart of sales per region                                                                      | Four categories, one measure.                                                                                                                                          |
| How do sales vary per release year in each region? | Line chart, one line per region                                                                    | Lines show change over an ordered variable.                                                                                                                            |
| Best release year / is the industry growing?       | Bar chart of global sales per release year                                                         | Annual totals; the peak year is in the title. A minimum-observations filter hides sparse years.                                                                        |
| Most popular platform each year?                   | Bar chart of the best-selling platform per year                                                    | One winner per year, coloured by platform.                                                                                                                             |
| Which regions prefer which genre?                  | Heatmap of genre by region (share or sales)                                                        | Same reasoning as the platform heatmap.                                                                                                                                |
| Top three genres per region?                       | Grouped bar chart                                                                                  | Exactly three bars per region stays readable.                                                                                                                          |
| Genre popularity over time?                        | Area chart of genre share per year (or sales)                                                      | Shares show how the mix changes when totals vary.                                                                                                                      |
| Do platforms specialise in a genre?                | Heatmap of platform by genre, colour = share of the platform's releases                            | Counted on releases, not sales, because sales coverage is low. Small platforms are excluded, since a platform with one release is "100 % specialised" by construction. |
| Which titles sold the most?                        | Horizontal bar chart of top-N titles                                                               | Long titles are readable on a horizontal axis. Sales are summed over platforms.                                                                                        |
| Consistent or hit-or-miss publishers?              | Bubble chart: mean sales per release (x, log) vs. coefficient of variation (y), size = total sales | Total sales does not show consistency; the coefficient of variation (std / mean) does.                                                                                 |
| Popular in one region, a flop in another?          | Grouped horizontal bars for two chosen regions                                                     | Side-by-side comparison per title. Only titles with a recorded value in both regions are used.                                                                         |

## Task: Generate App Design

### Output: App Design

**Architecture**

    data/vg_*.csv
        -> src/notebooks/preprocessing.ipynb   (Phase 3, run once)
        -> data/prepared/games_prepared.pkl, regional_sales_long.pkl
        -> src/main.py   (Dash layout + callbacks + Plotly figures)
        -> web browser (http://127.0.0.1:8050)

The app only reads the prepared data and never changes it.

**Layout.** One page with a title, a coverage note, and four tabs. Each tab has
controls at the top and its charts below. A change in a control updates all
charts on that tab through a callback.

| Tab                 | Controls                                                                              | Charts                                                                                    |
| ------------------- | ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Regions & Platforms | Region dropdown, number-of-platforms slider                                           | Top platforms; platform-by-region share heatmap; sales per region                         |
| Trends over time    | Year range, minimum observations per year, share/sales switch                         | Sales per year by region; global sales per year; best platform per year; genre area chart |
| Genres              | Share/sales switch, minimum releases per platform                                     | Genre-by-region heatmap; top three genres per region; platform specialisation heatmap     |
| Titles & Publishers | Number of titles, minimum releases per publisher, two region dropdowns, minimum sales | Top titles; publisher consistency; region gap bars                                        |

**Design decisions**

- Missing sales are removed once at start-up, never replaced with zero.
- Where a chart can be distorted by little data, a slider sets a minimum count.
- A filter that removes all data shows a message instead of an error.
- The region label "Europe and Africa" is used everywhere (the `pal_sales` region).

## Task: Build App

### Output: App Description

The app is `src/main.py`. To start it:

1. Create the prepared data by running `src/notebooks/preprocessing.ipynb`
   from top to bottom (creates `data/prepared/*.pkl`).
2. Activate the conda environment with `pandas`, `numpy`, `plotly` and `dash`.
3. Run `python src/main.py` from the project root and open http://127.0.0.1:8050.

Choose a tab and use its controls; the charts on that tab update at once.

- **Regions & Platforms:** pick a region (or all) to see its most popular
  platforms. The heatmap shows each platform's share of each region's sales.
- **Trends over time:** choose the release-year range. Raise the minimum
  observations to hide years with little data. Switch the genre chart
  between share and sales.
- **Genres:** compare genre preferences between regions, see the top three
  genres per region, and check which platforms concentrate on one genre.
- **Titles & Publishers:** see the top titles. In the publisher chart, a low
  coefficient of variation means consistent sales per release, a high one means
  hit-or-miss. The last chart compares titles between two regions.

Only about 30 % of records have a global sales figure, so every result describes
records with observed sales, not the whole market. This is stated on the page.

## Task: Assess App

### Output: App Assessment

| #   | Question                                 | Where answered                          | Status                                               |
| --- | ---------------------------------------- | --------------------------------------- | ---------------------------------------------------- |
| 1   | Regions vs. platform preference          | Regions & Platforms: share heatmap      | Covered                                              |
| 2   | Most popular platform                    | Regions & Platforms: platform bar chart | Covered                                              |
| 3   | Sales per release year in each region    | Trends: region lines                    | Covered                                              |
| 4   | Most popular platform each year          | Trends: best platform per year          | Covered                                              |
| 5   | Regions vs. genre preference             | Genres: genre-by-region heatmap         | Covered                                              |
| 6   | Top three genres per region              | Genres: top three chart                 | Covered                                              |
| 7   | Genre popularity over time               | Trends: genre area chart                | Covered                                              |
| 8   | Consistent vs. hit-or-miss publishers    | Titles & Publishers: bubble chart       | Covered                                              |
| 9   | Region that buys the most                | Regions & Platforms: sales per region   | Covered                                              |
| 10  | Best-selling titles                      | Titles & Publishers: top titles         | Covered                                              |
| 11  | Best year / industry growth              | Trends: global sales per year           | Covered, with a caveat about incomplete recent years |
| 12  | Platform specialisation by genre         | Genres: platform heatmap                | Covered                                              |
| 13  | Popular in one region, a flop in another | Titles & Publishers: gap bars           | Covered                                              |

**Limitations**

- Sales coverage is about 30 %, so results are not population-level estimates.
- The 225 repeated title-platform pairs from Data Preparation were not removed,
  so some sales may be counted twice in title and publisher totals.
- Title grouping uses a trimmed, case-folded name; other spelling variants of the
  same game are not merged.
- There is no cross-filtering between charts; each tab's controls act only on
  that tab.
- (Add here anything you found broken or awkward when testing the app.)
