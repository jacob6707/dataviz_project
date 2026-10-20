# Mythic Realm Studios - Game Market Explorer

An interactive Plotly and Dash dashboard that lets senior leadership explore video game
sales by region, platform, genre, publisher and release year. The project follows a
modified CRISP-DM process; the report for each phase is in the `reports/` folder.

## Requirements

- [Miniconda or Anaconda](https://docs.conda.io/en/latest/miniconda.html)
- Python 3.12 (or similar)

## Setup

1. Open a terminal in the project root (the folder that contains `data/`, `src/` and `reports/`).

2. Create and activate a conda environment:

```bash
   conda create -n ./.conda python=3.12 -y
   conda activate ./.conda
```

3. Install the packages:

```bash
   conda install -c conda-forge pandas numpy plotly dash ipykernel jupyter -y
```

(If conda cannot find a package, use `pip install pandas numpy plotly dash ipykernel jupyter`.)

## Step 1: Create the prepared data (run once)

The app does not read the raw CSV files directly. It reads two prepared files that are
created by the preprocessing notebook.

1. Open `src/notebooks/preprocessing.ipynb` and select the `dataviz` kernel.
2. Run all cells from top to bottom.

This creates `data/prepared/games_prepared.pkl` and `data/prepared/regional_sales_long.pkl`.
The `data/prepared/` folder is excluded by `.gitignore`, so it must be created on each new
machine. Without these files the app will not start.

## Step 2: Run the app

From the project root:

```bash
python src/main.py
```

Then open http://127.0.0.1:8050 in a browser. Stop the app with `Ctrl+C`.

## Using the app

The dashboard has four tabs. Each tab has controls at the top; the charts below update
immediately.

| Tab                 | What it shows                                                                                                  |
| ------------------- | -------------------------------------------------------------------------------------------------------------- |
| Regions & Platforms | Most popular platforms (all regions or one), each region's platform preferences, sales per region              |
| Trends over time    | Sales per release year by region, global sales per year, best platform per year, genre popularity over time    |
| Genres              | Genre preferences by region, top three genres per region, which platforms specialise in a genre                |
| Titles & Publishers | Best-selling titles, consistent vs. hit-or-miss publishers, titles that sell in one region but flop in another |

**Important:** only about 30 % of records have a global sales figure. All sales results
describe records with observed sales, not the whole market. Missing sales are never
counted as zero.

## Project structure

```text
data/
  vg_*.csv                  Original datasets
  data_dictionary/          Column descriptions
  prepared/                 Created by preprocessing.ipynb (not in git)
reports/                    CRISP-DM reports, one per phase
src/
  main.py                   The Dash application
  notebooks/
    preprocessing.ipynb     Cleans and prepares the data (Phase 3)
  util/
    boxart_download.py      Optional helper for downloading box art
project.ipynb               Project template and instructions
```
