# Phase: Deployment

This CRISP-DM phase has been modified somewhat to better align with the current project.

## Task: Produce Final Report

### Output: Final Report

Here you need to create a final written report of the data mining engagement, which includes all of the previous deliverables, summarizing and organizing the results. For this project, it might just consist of copy-and-pasting parts that you have documented in the previous phases.

---

This project developed an interactive Dash application for exploring video-game sales by region, platform, genre, publisher, and release year. The project followed a modified CRISP-DM process.

### Business Understanding

The business objective was to help senior leadership explore promising video-game markets, platforms, genres, publishers, and titles. The main questions concerned regional preferences, sales trends, popular platforms and genres, publisher consistency, best-selling titles, and differences between regional markets.

The business success criterion was that the dashboard should allow users to answer all 13 defined business questions through understandable interactive visualizations.

### Data Understanding

The main dataset, `vg_charts.csv`, contains 64,016 game-platform records and includes titles, platforms, genres, publishers, developers, critic scores, release dates, worldwide sales, and regional sales. Supporting datasets contain developer and publisher headquarters information and geographic reference data.

Important data-quality findings were:

- Only 18,922 records have a global sales value, approximately 29.56% of the dataset.
- Critic scores are available for only 6,678 records.
- Release dates are available for 56,965 records.
- There are 225 repeated title-platform combinations.
- Missing sales values represent unknown information and not zero sales.
- Recent release years have incomplete sales coverage.

These limitations mean that the dashboard provides exploratory comparisons based on observed records rather than population-level market estimates.

### Data Preparation

The data was cleaned using pandas. The notebook was used first to develop and verify the preparation workflow. For simpler deployment, the reusable `src/util/preprocess.py` utility now performs these steps from Python. Text fields are stripped of surrounding whitespace, empty strings are converted to missing values, dates are converted to datetime values, and numeric fields are converted to numeric types.

The following derived fields were created:

- `record_id` for identifying original game-platform rows.
- `release_year` for time-based analysis.
- `has_total_sales` for identifying records with observed global sales.
- `has_sales` for identifying observed regional sales values.

Developer and publisher reference data was joined using normalized keys and validated many-to-one joins. Regional sales were reshaped from wide format into a long-format table with one row per game-platform-region combination. Missing sales were preserved as missing values throughout the process.

### Visualization and App Development

The Dash application contains four tabs:

- **Regions & Platforms:** top platforms, regional platform shares, and total sales by region.
- **Trends over time:** regional sales trends, global sales by year, best-selling platforms by year, and genre popularity over time.
- **Genres:** regional genre preferences, top three genres per region, and platform genre specialization.
- **Titles & Publishers:** best-selling titles, publisher consistency, and regional title differences.

The visualizations were chosen according to the type of question. Bar charts compare categories, line and area charts show trends, heatmaps compare two categorical dimensions, and the publisher bubble chart compares mean sales, variation, and total sales.

Interactive controls allow users to select regions, years, minimum observation thresholds, sales/share modes, titles, publishers, and regional comparisons. Empty selections return an explanatory message instead of an application error.

### Evaluation

The application covers all 13 defined business questions and is approved for exploratory use. The main conclusions are that observed sales differ substantially between regions, platforms and genres have different regional patterns, publisher totals should be interpreted together with consistency measures, and title performance can differ strongly between regions.

The conclusions are limited by incomplete sales coverage, incomplete recent-year data, repeated title-platform records, limited title normalization, and the absence of per-chart observation counts. The application should not be used for precise market-size estimates or unsupported forecasts.

Overall, the project meets its stated exploratory dashboard objectives and is ready for presentation and demonstration after the documented setup and testing steps have been completed.

## Task: Produce Final Presentation

### Output: Final Presentation

Here you need to create a final presentation for the seminar, where you will present your project. See the details in the notebook `presentation.ipynb` in the `presentation` folder.

---

The presentation should last approximately 15 minutes and should be exported as one `.ppt`, `.pptx`, `.odp`, or `.pdf` file for submission through Canvas. Every group member must participate.

The recommended structure from `presentation.ipynb` is:

- **Introduction: 1–2 minutes.** Introduce the video-game datasets and the main business questions.
- **CRISP-DM walkthrough: 6–7 minutes.** Cover Business Understanding, Data Understanding, Data Preparation, Visualization and App Development, and Evaluation. Deployment is explicitly excluded from this walkthrough.
- **Live Dash demo: 5–6 minutes.** Demonstrate two or three strong features and show how user choices change the insights.
- **Conclusion and reflection: 1–2 minutes.** Summarize the main findings, limitations, lessons learned, and possible extensions.

The presentation should balance the CRISP-DM process and the final application. Code should remain in the background except when explaining an important transformation or technical decision. The group should use a clear business narrative and plan transitions between presenters.

### Output: App Demo

You also need to prepare a demonstration (demo) of your Dash application as part of your final presentation. See the details in the notebook `presentation.ipynb` in the `presentation` folder.

---

The app demo should take approximately 5–6 minutes and should focus on two or three strong features.

### Preparation before the seminar

1. Activate the project environment.
2. From the project root, start the application with:

   `python src/main.py`

   If the prepared files are missing, `src/main.py` automatically calls
   `util.preprocess.preprocess_data` to create them. The notebook remains available for
   reference and reproducibility, but is not required to start the application.

3. Open `http://127.0.0.1:8050` in a browser.
4. Test the required controls before the presentation and keep the prepared data available locally.

### Suggested demo sequence

1. Start on **Regions & Platforms**. Change the region selector and show how the top-platform chart changes. Use the regional heatmap to explain that shares make regions comparable.
2. Open **Trends over time**. Change the release-year range or minimum-observation filter and explain how the displayed years change. Mention that recent years have incomplete sales coverage.
3. Open **Titles & Publishers**. Demonstrate the publisher consistency bubble chart or compare titles between two regions. Explain the meaning of the coefficient of variation or the regional bars.
4. If time allows, demonstrate an empty-result state, such as selecting the same region in both regional comparison controls or applying a threshold that removes all publishers.

The demo should finish by connecting the displayed results to the original business questions. The presenter should state that missing sales are unknown rather than zero and that the dashboard describes observed records, not the entire market.

## Task: Review Project

### Output: Experience Documentation

Here you need to assess what went right and what went wrong, what was done well and what needs to be improved.

- Summarize important experience gained during theproject, e.g. pitfalls, misleading approaches, or hints for selecting the best suited datasets, pre-processing techniques, visualizations, and Dash application design.
- Also include a summary of things that have worked well in the CRISP-DM process, and things that haven't worked optimally (including suggestions of improvements if a future second iteration was conducted).

---

Several parts of the project worked well. The business questions were defined before selecting visualizations, which helped connect each chart to a clear analytical purpose. The data preparation preserved missing values correctly instead of treating unknown sales as zero. The regional long-format table made regional comparisons and time-series charts easier to implement. The joins were validated so that the number of game-platform rows did not increase unexpectedly. Minimum-observation filters and empty-state messages also made the dashboard more cautious and robust.

The project also showed the value of separating preprocessing from the Dash application. Prepared Pickle files allow the application to start without repeating all transformations every time, while the standalone preprocessing module provides a reproducible fallback when the files are missing.

Several issues could be improved. Sales coverage is only about 30%, and the dashboard does not show the observation count for each individual chart. Recent-year data is incomplete, which limits conclusions about industry growth. The 225 repeated title-platform combinations require further investigation, and title normalization does not merge every spelling variant. There is no cross-filtering between charts and no automated test suite for Dash callbacks.

The project also prepared critic-score and headquarters information that is not used in the current dashboard. Distribution plots, critic-score relationships, release-count trends, coverage visualizations, and geographic headquarters maps could be considered in a future iteration, or explicitly documented as outside the current scope.

The CRISP-DM process worked well for organizing the work and identifying data limitations. It was less effective where the project moved from exploratory findings to final application testing: the data understanding phase recommended coverage counts, but these were not added consistently to the application. A future iteration should add chart-level denominators, investigate repeated records, improve title normalization, add automated callback tests, and perform a clean-environment end-to-end test before deployment.

### Deployment and submission checklist

- Create or activate the Python environment.
- Install pandas, numpy, Plotly, and Dash. Jupyter and the notebook dependencies are optional unless the development workflow needs to be reproduced.
- Verify automatic preprocessing with `util.preprocess.preprocess_data`, or inspect the original notebook if reproducing the preparation workflow.
- Start the application with `python src/main.py`.
- Test all tabs, controls, empty states, and regional comparisons.
- Prepare a presentation lasting approximately 15 minutes.
- Ensure every group member participates.
- Export the presentation as `.ppt`, `.pptx`, `.odp`, or `.pdf`.
- Rehearse the 5–6 minute live application demo.
- Submit one presentation file through Canvas.
