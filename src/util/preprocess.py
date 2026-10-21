from pathlib import Path

import pandas as pd

DATA_DIR = Path("../../data")
OUTPUT_DIR = DATA_DIR / "prepared"

def preprocess_data_dictionary(data_dir: Path = DATA_DIR, output_dir: Path = OUTPUT_DIR):
  data_dir = Path(data_dir)
  output_dir = Path(output_dir)
  dictionary_dir = data_dir / "data_dictionary"
  files = [
      "vg_charts.csv",
      "vg_developers.csv",
      "vg_publishers.csv",
      "vg_geo_cities.csv",
      "vg_geo_countries.csv",
  ]

  dictionaries = []
  for filename in files:
      path = dictionary_dir / filename
      dictionary = pd.read_csv(path)
      required = {"Field", "Description"}
      if not required.issubset(dictionary.columns):
          raise ValueError(f"{path} must contain Field and Description columns")

      current = dictionary[["Field", "Description"]].copy()
      current["source"] = Path(filename).stem
      current["Field"] = current["Field"].astype("string").str.strip()
      current["Description"] = current["Description"].astype("string").str.strip()
      dictionaries.append(current[["source", "Field", "Description"]])

  result = pd.concat(dictionaries, ignore_index=True)
  if result["Field"].isna().any() or result["Description"].isna().any():
      raise ValueError("Data dictionary contains an empty field or description")
  if result.duplicated(["source", "Field"]).any():
      raise ValueError("Data dictionary contains duplicate fields in one source")

  output_dir.mkdir(parents=True, exist_ok=True)
  output_path = output_dir / "data_dictionary_prepared.pkl"
  result.to_pickle(output_path)
  print("Saved:", output_path, result.shape)
  return result

def preprocess_data(data_dir: Path = DATA_DIR, output_dir: Path = OUTPUT_DIR):
  data_dir = Path(data_dir)
  output_dir = Path(output_dir)
  files = {
      "charts": "vg_charts.csv",
      "developers": "vg_developers.csv",
      "publishers": "vg_publishers.csv",
      "cities": "vg_geo_cities.csv",
      "countries": "vg_geo_countries.csv"
  }

  raw = {name: pd.read_csv(data_dir / filename) for name, filename in files.items()}
  for name, df in raw.items():
      print(f"{name}: {len(df):,} rows, {len(df.columns)} columns")

  # Safety check: have we loaded the full game dataset, not the dictionary?
  required = {"title", "platform", "genre", "total_sales", "release_date"}
  assert required.issubset(raw["charts"].columns), "Wrong charts file or missing columns"

  game_columns = [
      "img", "title", "platform", "genre", "publisher", "developer",
      "critic_score", "total_sales", "na_sales", "jp_sales",
      "pal_sales", "other_sales", "release_date", "last_update"
  ]

  games = raw["charts"][game_columns].copy()
  games["record_id"] = range(1, len(games) + 1)  # stable ID for each original row

  print("Selected game rows:", len(games))
  print("Missing total sales:", games["total_sales"].isna().sum())
  assert len(games) == len(raw["charts"])

  text_columns = ["title", "platform", "genre", "publisher", "developer"]
  for column in text_columns:
      games[column] = games[column].astype("string").str.strip()
      games[column] = games[column].replace("", pd.NA)

  date_columns = ["release_date", "last_update"]
  for column in date_columns:
      before = games[column].notna().sum()
      games[column] = pd.to_datetime(games[column], format="%Y-%m-%d", errors="coerce")
      failed = before - games[column].notna().sum()
      print(f"{column}: {failed} failed date conversions")

  sales_columns = ["total_sales", "na_sales", "jp_sales", "pal_sales", "other_sales"]
  for column in sales_columns + ["critic_score"]:
      before = games[column].notna().sum()
      games[column] = pd.to_numeric(games[column], errors="coerce")
      failed = before - games[column].notna().sum()
      print(f"{column}: {failed} failed numeric conversions")

  print("Repeated title-platform pairs:", games.duplicated(["title", "platform"]).sum())
  print("Missing total sales after cleaning:", games["total_sales"].isna().sum())

  games["release_year"] = games["release_date"].dt.year.astype("Int64")
  games["has_total_sales"] = games["total_sales"].notna()

  print(games[["title", "platform", "release_year", "total_sales", "has_total_sales"]].head())
  print("Rows with a release year:", games["release_year"].notna().sum())
  assert games["record_id"].is_unique

  # Create temporary keys for matching company names.
  games["developer_key"] = games["developer"].str.casefold()
  games["publisher_key"] = games["publisher"].str.casefold()

  developers = raw["developers"][["developer", "city", "country"]].copy()
  developers["developer_key"] = developers["developer"].astype("string").str.strip().str.casefold().replace("", pd.NA)
  ambiguous_dev = developers["developer_key"].duplicated(keep=False)
  print("Ambiguous developer reference rows:", ambiguous_dev.sum())
  developers = developers.loc[~ambiguous_dev & developers["developer_key"].notna(),
                              ["developer_key", "city", "country"]]
  developers = developers.rename(columns={"city": "developer_city", "country": "developer_country"})

  publishers = raw["publishers"][["publisher", "city", "country"]].copy()
  publishers["publisher_key"] = publishers["publisher"].astype("string").str.strip().str.casefold().replace("", pd.NA)
  ambiguous_pub = publishers["publisher_key"].duplicated(keep=False)
  print("Ambiguous publisher reference rows:", ambiguous_pub.sum())
  publishers = publishers.loc[~ambiguous_pub & publishers["publisher_key"].notna(),
                              ["publisher_key", "city", "country"]]
  publishers = publishers.rename(columns={"city": "publisher_city", "country": "publisher_country"})

  # validate='m:1' prevents a game row matching multiple reference rows.
  enriched = games.merge(developers, on="developer_key", how="left", validate="m:1")
  enriched = enriched.merge(publishers, on="publisher_key", how="left", validate="m:1")
  assert len(enriched) == len(games), "Unexpected row count after company joins"
  print("Games matched to a developer headquarters:", enriched["developer_country"].notna().sum())
  print("Games matched to a publisher headquarters:", enriched["publisher_country"].notna().sum())

  countries = raw["countries"].copy()
  countries["country_key"] = countries["Country"].astype("string").str.strip().str.casefold().replace("", pd.NA)

  for column in ["Latitude", "Longitude"]:
      countries[column] = pd.to_numeric(
          countries[column].astype("string").str.strip().str.strip('"').str.strip(),
          errors="coerce"
      )

  countries["iso3"] = countries["Alpha-3 code"].astype("string").str.strip().str.strip('"')
  ambiguous_countries = countries["country_key"].duplicated(keep=False)
  print("Ambiguous country reference rows:", ambiguous_countries.sum())
  country_ref = countries.loc[~ambiguous_countries & countries["country_key"].notna(),
                              ["country_key", "iso3", "Latitude", "Longitude"]]

  for prefix in ["developer", "publisher"]:
      enriched["country_key"] = enriched[f"{prefix}_country"].astype("string").str.strip().str.casefold()
      lookup = country_ref.rename(columns={
          "iso3": f"{prefix}_iso3", "Latitude": f"{prefix}_latitude",
          "Longitude": f"{prefix}_longitude"
      })
      enriched = enriched.merge(lookup, on="country_key", how="left", validate="m:1")
      enriched = enriched.drop(columns="country_key")

  assert len(enriched) == len(games)
  print("Games with publisher country coordinates:", enriched["publisher_latitude"].notna().sum())

  regions = {
      "na_sales": "North America",
      "jp_sales": "Japan",
      "pal_sales": "Europe and Africa",
      "other_sales": "Other"
  }

  regional_sales = games.melt(
      id_vars=["record_id", "title", "platform", "genre", "publisher", "release_year"],
      value_vars=list(regions),
      var_name="region",
      value_name="sales_millions"
  )
  regional_sales["region"] = regional_sales["region"].map(regions)
  regional_sales["has_sales"] = regional_sales["sales_millions"].notna()

  assert len(regional_sales) == 4 * len(games)
  print("Regional rows:", len(regional_sales))
  print(regional_sales.groupby("region")["sales_millions"].agg(
      observations="count", observed_sales=lambda s: s.sum(min_count=1)
  ))

  enriched = enriched.drop(columns=["developer_key", "publisher_key"])

  first_columns = [
      "record_id", "title", "platform", "genre", "publisher", "developer",
      "release_date", "release_year", "total_sales", "na_sales",
      "jp_sales", "pal_sales", "other_sales"
  ]
  enriched = enriched[first_columns + [c for c in enriched.columns if c not in first_columns]]

  # Checks before saving: no game rows lost/duplicated and missing sales preserved.
  assert len(enriched) == len(raw["charts"])
  assert enriched["record_id"].is_unique
  assert enriched["total_sales"].isna().sum() == raw["charts"]["total_sales"].isna().sum()
  assert enriched["total_sales"].sum() == raw["charts"]["total_sales"].sum()

  output_dir.mkdir(parents=True, exist_ok=True)
  enriched.to_pickle(output_dir / "games_prepared.pkl")
  regional_sales.to_pickle(output_dir / "regional_sales_long.pkl")
  preprocess_data_dictionary(data_dir, output_dir)

  print("Saved:")
  print(output_dir / "games_prepared.pkl", enriched.shape)
  print(output_dir / "regional_sales_long.pkl", regional_sales.shape)