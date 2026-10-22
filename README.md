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
   conda create -p ./.conda python=3.12 -y
   conda activate ./.conda
```

3. Install the packages:

```bash
  python -m pip install -r src/requirements.txt
```

## Run the app

From the project root, run:

```bash
python src/main.py
```

If the prepared files do not exist, the application automatically preprocesses the raw CSV
files in `data/` and creates these files:

- `data/prepared/games_prepared.pkl`
- `data/prepared/regional_sales_long.pkl`
- `data/prepared/data_dictionary_prepared.pkl`

Open http://127.0.0.1:8050 in a browser. Stop the server with `Ctrl+C`.

### Command-line options

The application supports the following options:

| Option                 | Description                        | Default         |
| ---------------------- | ---------------------------------- | --------------- |
| `--port`, `-p`         | Port for the Dash server           | `8050`          |
| `--host`, `-H`         | Host address for the Dash server   | `127.0.0.1`     |
| `--debug`, `-d`        | Enable Dash debug mode             | Disabled        |
| `--data-dir`, `-D`     | Directory containing prepared data | `data/prepared` |
| `--raw-data-dir`, `-R` | Directory containing raw CSV files | `data`          |

Examples:

```bash
# Use another port
python src/main.py --port 8051

# Enable debug mode
python src/main.py --debug

# Use custom data directories
python src/main.py --data-dir C:\\path\\to\\prepared --raw-data-dir C:\\path\\to\\data
```

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
  prepared/                 Created automatically by the app (not in git)
reports/                    CRISP-DM reports, one per phase
src/
  main.py                   The Dash application
    requirements.txt        Python dependencies for the application
  notebooks/
      preprocessing.ipynb   Optional preprocessing reference notebook
  util/
    boxart_download.py      Optional helper for downloading box art
    preprocess.py           Utility for preprocessing data, copied over from
                            preprocessing.ipynb, with added data description
                            preprocessing
project.ipynb               Project template and instructions
```
