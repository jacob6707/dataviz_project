---

# Phase: Evaluation

This CRISP-DM phase has been modified somewhat to better align with the currect project.

## Task: Evaluate Results

### Output: Assessment of Data Mining Results

You need to assesses the degree to which the Dash Application and its visualizations meet the business objectives, and determine if there is some business reason why this Dash Application is deficient.

Summarize the assessment results here in terms of business success criteria, including a final statement regarding whether you regard the project as meeting the business objectives or not.

The Dash application addresses all 13 data-mining questions defined in the Business Understanding phase.

It provides visualizations for regional platform preferences, popular platforms, regional sales, yearly trends, best-selling platforms by year, genre preferences, top genres, genre popularity over time, platform specialization, best-selling titles, publisher consistency, and regional title differences.

The selected visualizations are appropriate for the questions. Bar charts are used for category comparisons, line and area charts for trends, heatmaps for region-by-category comparisons, and scatter/bubble charts for publisher consistency.

The data preparation process supports the analysis appropriately. Missing sales values are retained as unknown rather than replaced with zero. Regional sales were reshaped into a long-format table, and minimum-observation filters were added for publisher and platform comparisons.

However, the results must be interpreted as exploratory rather than population-level estimates. Only 18,922 of 64,016 game-platform records have a global sales value, representing approximately 29.56% of the dataset. Regional sales also have substantial missingness, so rankings and trends may be affected by unequal data coverage.

The latest release years are especially incomplete. A decline in recent sales cannot be interpreted as proof that the video-game industry is shrinking. The application includes a warning and a minimum-observation filter, but it does not display the number of observations used for every chart.

There are also 225 repeated title-platform combinations. These records were retained because they may represent valid observations, but they could cause some title and publisher totals to be counted more than once. Title grouping uses trimmed and case-folded names, but spelling variants are not fully reconciled.

Overall, the application meets the stated business objectives for an exploratory dashboard, provided that these limitations are considered.

### Output: Approved Visualizations and App Functionality

After assessing the Dash application and its visualizations with respect to the business success criteria, either approve or disapprove the Dash application and its visualizations, given your (the project group's) own judgement.

The Dash application and its current visualizations are approved for the stated exploratory purpose.

This approval is subject to the following conditions:

- Sales results are based only on records with observed sales.
- Missing sales are not interpreted as zero.
- Recent-year trends are not treated as definitive evidence of industry growth or decline.
- Publisher and platform comparisons are interpreted together with their minimum-observation filters.
- Title and publisher totals are interpreted cautiously because repeated title-platform rows were not removed.
- The application is tested using the required preprocessing and startup procedure before demonstration or deployment.

The application provides interactive controls for regions, years, minimum observations, genres, publishers, titles, and regional comparisons. It also provides an empty-state message when a filter removes all available data.

The approval is qualified rather than unconditional. The application is suitable for demonstrating the project objectives, but it should not be used for precise market-size estimates or unsupported business forecasts.

## Task: Review Process

### Output: Review of Process

Here you need to perform a more thorough review of
the _data mining_ engagement in order to determine if there is any important factor or task that has somehow been overlooked, e.g.:

- Did we select and pre-process the datasets appropriately?
- Did we select appropriate visualizations given the underlying data?
- Did we correctly build the Dash application?
- etc.

Summarize the process review and highlight activities that have been missed and those that should really be repeated.

The project followed the main CRISP-DM activities appropriately:

- The business objectives and data-mining questions were defined.
- The available datasets were described and assessed.
- Missing values and data-quality limitations were documented.
- Dates and numeric fields were converted to suitable data types.
- Developer and publisher data were joined using validated many-to-one joins.
- Regional sales were reshaped into a long-format table.
- The selected visualizations were connected to the business questions.
- The Dash application was separated from the preprocessing workflow.

Several activities should be repeated or improved before final deployment.

First, the preprocessing notebook and standalone preprocessing module should be run from a clean environment to verify that the workflow is reproducible. The relative data path in the notebook should also be checked because it depends on the notebook working directory.

Second, every tab and control in the Dash application should be tested manually, including:

- Running the application after deleting the prepared-data directory.
- Selecting each available region.
- Changing the year range and minimum-observation filter.
- Switching between sales and share views.
- Selecting the same region in both regional comparison controls.
- Choosing filters that produce no results.
- Choosing publisher thresholds that remove all publishers.

Third, the 225 repeated title-platform combinations should be investigated to determine whether they are valid separate observations or duplicated records.

Fourth, the dashboard should display observation counts or coverage information for individual charts, especially annual sales charts and regional comparisons. The current global coverage note does not show how much data supports each specific result.

Fifth, the project describes distribution plots, relationship plots, and choropleth maps as possible visualization techniques, but these are not currently included. The application does not provide:

- A sales distribution plot.
- A critic-score distribution.
- A critic-score versus sales relationship plot.
- A release-count trend.
- A missing-data or coverage visualization.
- A geographic visualization of developer or publisher headquarters.

These views are not required to answer the 13 explicitly listed business questions, but they should either be added or documented as outside the project scope.

Finally, the evaluation, deployment, and application demonstration should be completed using the same environment setup described in the README. The README should also be checked against the current startup behavior, since the application can automatically run preprocessing when prepared files are missing.

The main remaining risks are incomplete sales coverage, unresolved repeated title-platform records, incomplete recent-year data, limited title normalization, and the absence of automated tests for the Dash callbacks.

## Task: Determine Next Steps

### Output: List of Possible Actions

Depending on the results of the assessment and the process review, the project team decides how to proceed.

Here we would normally list potential further actions, and rationale (reasons for and against each option), but we will skip this step in this project.

### Output: Decisions

Here we would normally describe the decision as to how to proceed, along with the rationale (e.g. if we need to perform an additional iteration, or proceed to deployment), but we will skip this step in this project, and decide to go ahead with the deployment phase.
