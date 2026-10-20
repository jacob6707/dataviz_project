from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html

#DATA:

DATA = Path(__file__).resolve().parent.parent/"data"/"prepared"
games = pd.read_pickle(DATA/"games_prepared.pkl")
reg = pd.read_pickle(DATA/"regional_sales_long.pkl")

#missing values are unknown, keep only the ones with values
reg = reg[reg["sales_millions"].notna()]
tot = games[games["total_sales"].notna()]

REGIONS = ["North America", "Japan", "Europe and Africa", "Other"]
Y0, Y1 = int(games["release_year"].min()), int(games["release_year"].max())
COVERAGE = games["total_sales"].notna().mean() * 100

def empty(msg="No data for this selection"):
    f = go.Figure()
    f.add_annotation(text=msg, showarrow=False, font={"size":16})
    f.update_xaxes(visible=False)
    f.update_yaxes(visible=False)
    return f

def years(df, rng, min_obs):
    d = df[df["release_year"].notna()]
    d = d[d["release_year"].between(rng[0],rng[1])]
    n = d.groupby("release_year")["release_year"].transform("size")
    d = d[n >= min_obs]
    return d.assign(release_year=d["release_year"].astype(int))

def title_key(s):
    return s.astype("string").str.strip().str.casefold()

def control(label,comp, width="30%"):
    return html.Div(
        [html.Label(label, style={"fontWeight": "bold"}),comp],
        style={"display": "inline-block", "verticalAlign": "top",
               "width": width, "padding": "8px 16px"},
    )

def slider(id_, lo, hi, step,val):
    return dcc.Slider(id=id_, min=lo, max = hi, step=step, value=val,
                      marks={lo: str(lo), hi: str(hi)},
                      tooltip={"placement": "bottom"}
                      )
def radio(id_, value):
    return dcc.RadioItems(id = id_, value = value, inline=True, options=[
        {"label": "Share (%)", "value": "share"},
        {"label": "Sales (millions)", "value": "sales"}])

region_opts = [{"label":r,"value":r} for r in REGIONS]

#LAYOUT: 

app = Dash(__name__, title="Game market")

tab_platforms = dcc.Tab(label="Regions & Platforms", value="t1", children=[
    html.Div([
        control("Region", dcc.Dropdown(
            id="p-region", clearable=False, value="All regions",
            options=[{"label": "All regions", "value": "All regions"}] + region_opts)),
        control("Number of platforms", slider("p-n", 5, 20, 1, 10)),
    ]),
    dcc.Graph(id="p-bar"),
    dcc.Graph(id="p-heat"),
    dcc.Graph(id="p-region-total"),
])

tab_time = dcc.Tab(label="Trends over time", value="t2", children=[
    html.Div([
        control("Release years", dcc.RangeSlider(
            id="t-years", min=Y0, max=Y1, step=1, value=[1990, Y1],
            marks={y: str(y) for y in range(Y0 - Y0 % 10 + 10, Y1 + 1, 10)},
            tooltip={"placement": "bottom"}), width="45%"),
        control("Min. observations per year", slider("t-min", 0, 300, 10, 50), width="25%"),
        control("Genre chart", radio("t-mode", "share"), width="25%"),
    ]),
    html.P("Recent years have incomplete sales data, so a drop in the last years "
           "does not prove the industry is shrinking.",
           style={"padding": "0 16px", "color": "#555"}),
    dcc.Graph(id="t-lines"),
    dcc.Graph(id="t-global"),
    dcc.Graph(id="t-best-platform"),
    dcc.Graph(id="t-genre"),
])

tab_genres = dcc.Tab(label="Genres", value="t3", children=[
    html.Div([
        control("Region x genre", radio("g-mode", "share")),
        control("Min. releases per platform", slider("g-min", 20, 500, 10, 100)),
    ]),
    dcc.Graph(id="g-heat"),
    dcc.Graph(id="g-top3"),
    dcc.Graph(id="g-spec"),
])

tab_titles = dcc.Tab(label="Titles & Publishers", value="t4", children=[
    html.Div([
        control("Number of titles", slider("ti-n", 5, 30, 1, 15)),
        control("Min. releases with sales per publisher", slider("pu-min", 5, 200, 5, 20), width="40%"),
    ]),
    dcc.Graph(id="ti-bar"),
    dcc.Graph(id="pu-scatter"),
    html.H4("Popular in one region, a flop in another", style={"padding": "0 16px"}),
    html.Div([
        control("Strong in", dcc.Dropdown(id="x-a", options=region_opts, value="North America", clearable=False)),
        control("Weak in", dcc.Dropdown(id="x-b", options=region_opts, value="Japan", clearable=False)),
        control("Min. sales in strong region (M)", slider("x-min", 1, 5, 1, 1)),
    ]),
    dcc.Graph(id="x-bars"),
])

app.layout = html.Div(
    style={"maxWidth": "1200px", "margin": "0 auto", "fontFamily": "Arial, sans-serif"},
    children=[
        html.H1("Game Market Explorer"),
        html.P(f"{len(games):,} game-platform records. Only {COVERAGE:.1f}% have a global sales "
               "figure, so every sales result describes records with observed sales, not the "
               "whole market. Missing sales are never counted as zero.",
               style={"color": "#555"}),
        dcc.Tabs(value="t1", children=[tab_platforms, tab_time, tab_genres, tab_titles]),
    ],
)

#CALLBACKS:

#Regions and platforms
@app.callback(Output("p-bar", "figure"), Output("p-heat", "figure"),
              Output("p-region-total", "figure"),
              Input("p-region", "value"), Input("p-n", "value"))
def platforms(region, n):
    d = reg if region == "All regions" else reg[reg["region"] == region]
    top = d.groupby("platform")["sales_millions"].sum().nlargest(n).reset_index()
    bar = px.bar(top, x="platform", y="sales_millions",
                 labels={"sales_millions": "Sales (millions)"},
                 title=f"Most popular platforms: {region}")
    pv = reg.pivot_table(index="platform", columns="region",
                         values="sales_millions", aggfunc="sum").reindex(columns=REGIONS)
    share = pv.div(pv.sum()) * 100
    overall = reg.groupby("platform")["sales_millions"].sum().nlargest(n).index
    heat = px.imshow(share.loc[overall], text_auto=".1f", aspect="auto",
                     labels={"color": "% of region sales"},
                     title="Platform share of each region's sales (%)")

    rt = reg.groupby("region")["sales_millions"].sum().reindex(REGIONS).reset_index()
    rtot = px.bar(rt, x="region", y="sales_millions", color="region",
                  labels={"sales_millions": "Sales (millions)"},
                  title="Which region buys the most?")
    return bar, heat, rtot


#Trends over time
@app.callback(Output("t-lines", "figure"), Output("t-global", "figure"),
              Output("t-best-platform", "figure"), Output("t-genre", "figure"),
              Input("t-years", "value"), Input("t-min", "value"), Input("t-mode", "value"))
def time_trends(rng, min_obs, mode):
    r = years(reg, rng, min_obs)
    g = years(tot, rng, min_obs)
    if r.empty or g.empty:
        e = empty()
        return e, e, e, e

    by_reg = r.groupby(["release_year", "region"], as_index=False)["sales_millions"].sum()
    lines = px.line(by_reg, x="release_year", y="sales_millions", color="region",
                    markers=True, category_orders={"region": REGIONS},
                    labels={"sales_millions": "Sales (millions)"},
                    title="Sales per release year in each region")

    yearly = g.groupby("release_year", as_index=False)["total_sales"].sum()
    peak = yearly.loc[yearly["total_sales"].idxmax()]
    glob = px.bar(yearly, x="release_year", y="total_sales",
                  labels={"total_sales": "Global sales (millions)"},
                  title=f"Global sales per release year (peak: {int(peak['release_year'])})")

    py = g.groupby(["release_year", "platform"], as_index=False)["total_sales"].sum()
    best = py.loc[py.groupby("release_year")["total_sales"].idxmax()]
    bestfig = px.bar(best, x="release_year", y="total_sales", color="platform",
                     labels={"total_sales": "Sales (millions)"},
                     title="Best-selling platform in each release year")

    ge = g.groupby(["release_year", "genre"], as_index=False)["total_sales"].sum()
    if mode == "share":
        ge["total_sales"] = (ge["total_sales"]
                             / ge.groupby("release_year")["total_sales"].transform("sum") * 100)
    area = px.area(ge, x="release_year", y="total_sales", color="genre",
                   labels={"total_sales": "Share of year (%)" if mode == "share" else "Sales (millions)"},
                   title="Genre popularity over time")
    return lines, glob, bestfig, area

#Genres
@app.callback(Output("g-heat", "figure"), Output("g-top3", "figure"),
              Output("g-spec", "figure"),
              Input("g-mode", "value"), Input("g-min", "value"))
def genres(mode, min_rows):
    pv = reg.pivot_table(index="genre", columns="region",
                         values="sales_millions", aggfunc="sum").reindex(columns=REGIONS)
    if mode == "share":
        pv = pv.div(pv.sum()) * 100
    pv = pv.loc[pv.sum(axis=1).sort_values(ascending=False).index]
    heat = px.imshow(pv, text_auto=".0f" if mode == "sales" else ".1f", aspect="auto",
                     labels={"color": "% of region" if mode == "share" else "Sales (millions)"},
                     title="Which regions prefer which genre?")

    gs = reg.groupby(["region", "genre"], as_index=False)["sales_millions"].sum()
    top3 = (gs.sort_values("sales_millions", ascending=False).groupby("region").head(3))
    top3fig = px.bar(top3, x="region", y="sales_millions", color="genre", barmode="group",
                     category_orders={"region": REGIONS},
                     labels={"sales_millions": "Sales (millions)"},
                     title="Top three genres per region")

    counts = games["platform"].value_counts()
    sub = games[games["platform"].isin(counts[counts >= min_rows].index)]
    if sub.empty:
        return heat, top3fig, empty("No platform has that many releases")
    ct = pd.crosstab(sub["platform"], sub["genre"], normalize="index") * 100
    ct = ct.loc[counts.reindex(ct.index).sort_values(ascending=False).index]
    spec = px.imshow(ct, text_auto=".0f", aspect="auto",
                     labels={"color": "% of platform's releases"},
                     title=f"Do platforms specialise in a genre? (platforms with >= {min_rows} releases)")
    spec.update_layout(height=200 + 28 * len(ct))
    return heat, top3fig, spec

#Titles and publishers
@app.callback(Output("ti-bar", "figure"), Output("pu-scatter", "figure"),
              Input("ti-n", "value"), Input("pu-min", "value"))
def titles_publishers(n, min_rows):
    top = (tot.groupby(title_key(tot["title"]))
              .agg(title=("title", "first"), sales=("total_sales", "sum"))
              .nlargest(n, "sales"))
    tbar = px.bar(top, x="sales", y="title", orientation="h",
                  labels={"sales": "Global sales (millions)", "title": ""},
                  title="Best-selling titles worldwide")
    tbar.update_yaxes(autorange="reversed")

    p = (tot[tot["publisher"].notna()].groupby("publisher")["total_sales"]
         .agg(n="size", total="sum", mean="mean", std="std").reset_index())
    p = p[(p["n"] >= min_rows) & (p["mean"] > 0)].copy()
    if p.empty:
        return tbar, empty("No publisher has that many releases with sales")
    p["cv"] = p["std"] / p["mean"]
    pub = px.scatter(p, x="mean", y="cv", size="total", hover_name="publisher",
                     hover_data={"n": True, "total": ":.1f", "mean": ":.2f", "cv": ":.2f"},
                     log_x=True, size_max=45,
                     labels={"mean": "Mean sales per release (M, log)", "cv": "Coefficient of variation"},
                     title="Consistent (low CV) or hit-or-miss (high CV)? Bubble size = total sales")
    return tbar, pub

@app.callback(Output("x-bars", "figure"),
              Input("x-a", "value"), Input("x-b", "value"), Input("x-min", "value"))
def region_gap(a, b, min_sales):
    if a == b:
        return empty("Choose two different regions")
    o = reg[reg["region"].isin([a, b])].assign(key=lambda d: title_key(d["title"]))
    w = o.pivot_table(index="key", columns="region", values="sales_millions", aggfunc="sum")
    if a not in w or b not in w:
        return empty()
    w = w.dropna(subset=[a, b]) 
    w = w[w[a] >= min_sales]
    if w.empty:
        return empty("No titles match; lower the minimum sales")
    w["gap"] = w[a] - w[b]
    top = w.nlargest(15, "gap")[[a, b]]
    top.index = o.groupby("key")["title"].first().reindex(top.index)
    fig = px.bar(top, orientation="h", barmode="group",
                 labels={"value": "Sales (millions)", "index": "", "variable": "Region"},
                 title=f"Titles strong in {a} but weak in {b}")
    fig.update_yaxes(autorange="reversed")
    return fig

if __name__ == "__main__":
    app.run(debug=True, threaded=False)