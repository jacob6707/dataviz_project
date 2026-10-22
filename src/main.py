import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, ctx, dcc, html

DATA = Path(__file__).resolve().parent.parent/"data"/"prepared"

# Command-line arguments
parser = argparse.ArgumentParser(prog="Mythic Realm Studios Game Market Explorer", 
                                    description="Interactive dashboard for exploring game sales data")
parser.add_argument("--port", "-p", type=int, help="Port to run the server on", default=8050, nargs="?")
parser.add_argument("--host", "-H", type=str, help="Host to run the server on", default="127.0.0.1", nargs="?")
parser.add_argument("--debug", "-d", action="store_true", help="Run the server in debug mode", default=False)
parser.add_argument("--data-dir", "-D", type=str, help="Directory containing the prepared data files", default=str(DATA), nargs="?")
parser.add_argument("--raw-data-dir", "-R", type=str, help="Directory containing the raw data files (if preprocessing is needed)", default=str(Path(DATA).resolve().parent), nargs="?")
args = parser.parse_args()

#DATA:

prepared_dir = Path(args.data_dir)
raw_data_dir = Path(args.raw_data_dir)
dictionary_path = prepared_dir / "data_dictionary_prepared.pkl"
if (not (prepared_dir / "games_prepared.pkl").exists()
        or not (prepared_dir / "regional_sales_long.pkl").exists()
        or not dictionary_path.exists()):
    from util.preprocess import preprocess_data
    preprocess_data(raw_data_dir, prepared_dir)

games = pd.read_pickle(prepared_dir / "games_prepared.pkl")
reg = pd.read_pickle(prepared_dir / "regional_sales_long.pkl")
dictionary = pd.read_pickle(dictionary_path)

descriptions = (dictionary.sort_values("source")
                .drop_duplicates("Field")
                .set_index("Field")["Description"]
                .to_dict())
descriptions.update({
    "record_id": "Stable identifier for the original game-platform record",
    "release_year": "Year the game was released",
    "has_total_sales": "Whether global sales are available",
    "sales_millions": "Sales of copies in millions",
    "region": "Sales region",
})

def column_label(column, fallback=None):
    return descriptions.get(column, fallback or column.replace("_", " ").title())

#genres with less than 2% of all releases are grouped, so every genre chart stays readable
OTHER_GENRES = "Other genres"
genre_share = games["genre"].value_counts(normalize=True)
MAIN_GENRES = list(genre_share[genre_share >= 0.02].index)
GENRES = MAIN_GENRES + [OTHER_GENRES]

def group_genre(s):
    return s.where(s.isin(MAIN_GENRES) | s.isna(), OTHER_GENRES)

games["genre"] = group_genre(games["genre"])
reg = reg.assign(genre=group_genre(reg["genre"]))

#missing values are unknown, keep only the ones with values
reg = reg[reg["sales_millions"].notna()]
tot = games[games["total_sales"].notna()]

REGIONS = ["North America", "Japan", "Europe and Africa", "Other"]
Y0, Y1 = int(games["release_year"].min()), int(games["release_year"].max())
COVERAGE = games["total_sales"].notna().mean() * 100

#STYLE:

#one colour per region and genre, used in every chart
REGION_COLORS = {"North America": "#2E6FBA", "Japan": "#D1495B",
                 "Europe and Africa": "#3A9D6B", "Other": "#E3A33B"}
GENRE_COLORS = dict(zip(MAIN_GENRES, px.colors.qualitative.Dark24), **{OTHER_GENRES: "#9aa5b1"})
BASE_COLOR = "#2E6FBA"
PUB_CLASSES = ["Consistent (ratio < 1)", "Mixed (1 to 1.5)", "Hit-or-miss (ratio > 1.5)"]
PUB_COLORS = dict(zip(PUB_CLASSES, ["#2E6FBA", "#E3A33B", "#C8372D"]))
HEAT_SCALE = "Blues"
CHART_H = 430

#share of records with a sales figure per release year; years after the last
#one above 10% are marked as "almost no sales data"
coverage = games.groupby("release_year")["total_sales"].agg(lambda x: x.notna().mean())
LOW_FROM = int(coverage[coverage >= 0.10].index.max()) + 1

CSS = """
body { margin:0; background:#e9edf2; font-family:'Segoe UI',Arial,sans-serif; color:#1f2933; }
.page { max-width:1200px; margin:0 auto; padding:24px 16px 48px; }
.page-header { margin:0 0 22px; padding:0 0 16px; border-bottom:1px solid #c5cdd8; }
.page h1 { margin:0; font-size:30px; font-weight:700; letter-spacing:-0.5px; }
.subtitle { margin:4px 0 14px; font-size:16px; color:#52606d; }
.intro { margin:0 0 4px; color:#52606d; font-size:13.5px; line-height:1.55; }
.intro b { color:#323f4b; }
.tip { margin:2px 0 6px; font-size:12.5px; color:#7b8794; }
.tip b { color:#52606d; }
input[type=checkbox], input[type=radio] { accent-color:#2E6FBA; }
.js-plotly-plot .legend .legendtoggle { pointer-events:none !important; cursor:default !important; }
.checks { display:grid; grid-template-columns:repeat(auto-fill, minmax(190px, 1fr)); gap:4px 16px; }
.checks label { display:flex !important; align-items:center; margin:0 !important; font-weight:400 !important; font-size:13px; }
.btn-row { display:flex; gap:16px; margin:2px 0 4px; }
.link-btn { background:none; border:none; padding:0; color:#2E6FBA; font-size:12.5px; font-weight:600; cursor:pointer; }
.link-btn:hover { text-decoration:underline; }
.key { display:flex; flex-wrap:wrap; gap:6px 22px; align-items:center; margin:8px 0 0; font-size:13px; color:#323f4b; }
.key b { color:#52606d; font-weight:600; }
.group-dot { display:inline-block; width:10px; height:10px; border-radius:50%; margin:0 6px 0 2px; }
.card { background:#fff; border:1px solid #dde3ea; border-radius:12px; padding:20px 24px 12px;
        margin:0 0 20px; box-shadow:0 1px 3px rgba(16,24,40,.06); }
.card h3 { margin:0 0 4px; font-size:19px; }
.desc { margin:0 0 14px; color:#52606d; font-size:14px; line-height:1.5; }
.controls { display:flex; flex-wrap:wrap; gap:8px 28px; padding:12px 16px 8px; margin:0 0 8px;
            background:#f7f9fb; border-radius:8px; }
.control { flex:1 1 240px; min-width:220px; }
.control label { font-weight:600; font-size:13px; display:block; margin-bottom:6px; }
.note { font-size:13px; color:#52606d; font-style:italic; margin:0 0 4px; min-height:1px; }
.hint { display:flex; gap:8px; align-items:center; margin:0 0 12px; font-size:13px; color:#52606d; }
.hint b { flex:none; width:16px; height:16px; border-radius:50%; border:1.5px solid #7b8794; color:#7b8794;
          font-size:11px; line-height:1; font-weight:700; display:flex; align-items:center; justify-content:center; }
/* folder tabs */
.folder-bar { display:flex !important; gap:4px; border:none !important; align-items:flex-end; }
.folder-tab { flex:none !important; width:auto !important; min-width:180px; text-align:center;
              padding:9px 24px !important; margin-bottom:5px !important; border:none !important;
              border-radius:10px !important; background:#d6dce4 !important; color:#6b7785 !important;
              font-weight:500; cursor:pointer; }
.folder-tab:hover { background:#e1e6ec !important; }
.folder-tab--selected, .folder-tab--selected:hover { position:relative; z-index:2; top:1px; cursor:default;
              margin-bottom:0 !important; padding-bottom:14px !important; background:#f6f8fa !important;
              color:#1f2933 !important; font-weight:700; border:1px solid #c5cdd8 !important;
              border-bottom:none !important; border-radius:12px 12px 0 0 !important; }
.folder-tab--selected::before, .folder-tab--selected::after { content:""; position:absolute; bottom:0;
              width:13px; height:12px; }
.folder-tab--selected::before { left:-12px;
    background:radial-gradient(circle at 0 0, transparent 11px, #c5cdd8 11px, #c5cdd8 12px, #f6f8fa 12px); }
.folder-tab--selected::after { right:-12px;
    background:radial-gradient(circle at 100% 0, transparent 11px, #c5cdd8 11px, #c5cdd8 12px, #f6f8fa 12px); }
.folder-tab--selected:first-child::before { display:none; }
.tab-parent:has(.folder-tab--selected:first-child) .folder-body { border-top-left-radius:0; }
.folder-body { background:#f6f8fa; border:1px solid #c5cdd8; border-radius:12px; padding:4px 20px 8px; }
.tab-intro { margin:14px 0 14px; font-size:15px; color:#323f4b; }
"""

def empty(msg="No data for this selection"):
    f = go.Figure()
    f.add_annotation(text=msg, showarrow=False, font={"size": 16})
    f.update_xaxes(visible=False)
    f.update_yaxes(visible=False)
    f.update_layout(template="plotly_white", height=CHART_H)
    return f

def finish(fig, height=CHART_H):
    #headings live in the cards, so the figures get no title.
    #legends and colour bars always sit above the plot, left-aligned
    fig.update_layout(template="plotly_white", height=height, title=None,
                      margin={"l": 70, "r": 20, "t": 24, "b": 60},
                      font={"family": "Segoe UI, Arial, sans-serif", "size": 13},
                      bargap=0.3, bargroupgap=0.08)
    #outside ticks without a visible line give the labels some air next to the plot
    fig.update_yaxes(ticks="outside", ticklen=8, tickcolor="rgba(0,0,0,0)",
                     automargin=True, title_standoff=12)
    fig.update_xaxes(ticks="outside", ticklen=8, tickcolor="rgba(0,0,0,0)",
                     automargin=True, title_standoff=12)

    names = [t.name for t in fig.data if t.showlegend is not False and t.name]
    if names:
        #rough number of legend rows, so the plot area starts below the legend
        rows = max(1, -(-sum(len(n) + 6 for n in names) * 8 // (fig.layout.width or 1000)))
        fig.update_layout(legend={"orientation": "h", "x": 0, "xanchor": "left",
                                  "y": 1.02, "yanchor": "bottom", "title": {"text": ""},
                                  "font": {"size": 12}, "itemclick": False, "itemdoubleclick": False},
                          margin={"t": 24 + 22 * rows, "l": 70, "r": 20, "b": 60})
    if fig.data and fig.data[0].type == "heatmap":   #room for the colour bar above the plot
        fig.update_layout(margin={"t": 110, "l": 70, "r": 20, "b": 60})
    return fig

def low_data_band(fig, x_max):
    #grey band over the years that have almost no sales data
    if x_max >= LOW_FROM:
        fig.add_vrect(x0=LOW_FROM - 0.5, x1=x_max + 0.5, fillcolor="#7b8794", opacity=0.12,
                      line_width=0, layer="below", annotation_text="almost no sales data",
                      annotation_position="top left", annotation_font={"size": 11, "color": "#52606d"})
    return fig

def years(df, rng, min_obs):
    d = df[df["release_year"].notna()]
    d = d[d["release_year"].between(rng[0], rng[1])]
    n = d.groupby("release_year")["release_year"].transform("size")
    d = d[n >= min_obs]
    return d.assign(release_year=d["release_year"].astype(int))

def title_key(s):
    return s.astype("string").str.strip().str.casefold()

def control(label, comp, width=None):
    flex = {"flex": f"1 1 {width}"} if width else None
    return html.Div([html.Label(label), comp], className="control", style=flex)

def slider(id_, lo, hi, step, val):
    return dcc.Slider(id=id_, min=lo, max=hi, step=step, value=val,
                      marks={lo: str(lo), hi: str(hi)},
                      tooltip={"placement": "bottom"})

INPUT_STYLE = {"marginRight": "6px"}
LABEL_STYLE = {"display": "inline-flex", "alignItems": "center", "margin": "0 20px 6px 0",
               "fontWeight": 400, "fontSize": "13px"}
TOGGLES = {}   #checklist id -> all values, used by the "Show all" / "Clear" buttons

def radio(id_, value):
    return dcc.RadioItems(id=id_, value=value, inline=True,
                          inputStyle=INPUT_STYLE, labelStyle=LABEL_STYLE,
                          options=[{"label": "Share (%)", "value": "share"},
                                   {"label": "Sales (millions)", "value": "sales"}])

def toggle(id_, values, label, width="100%"):
    #checkboxes to show or hide parts of a chart, with buttons to get everything back
    TOGGLES[id_] = values
    checks = dcc.Checklist(id=id_, value=values, className="checks", inline=True, inputStyle=INPUT_STYLE,
                           labelStyle=LABEL_STYLE, options=[{"label": v, "value": v} for v in values])
    buttons = html.Div([html.Button("Show all", id=f"{id_}-all", n_clicks=0, className="link-btn"),
                        html.Button("Clear", id=f"{id_}-none", n_clicks=0, className="link-btn")],
                       className="btn-row")
    return control(label, html.Div([checks, buttons]), width=width)

def time_controls(p, mode=False):
    #every time chart has its own sliders inside its card
    c = [control("Release years", dcc.RangeSlider(
            id=f"{p}-years", min=Y0, max=Y1, step=1, value=[1990, Y1],
            marks={y: str(y) for y in range(Y0 - Y0 % 10 + 10, Y1 + 1, 10)},
            tooltip={"placement": "bottom"}), width="420px"),
         control("Min. observations per year", slider(f"{p}-min", 0, 300, 10, 50), width="260px")]
    if mode:
        c.append(control("Show as", radio(f"{p}-mode", "share"), width="200px"))
    return c

def group_dot(kind):
    return html.Span(className="group-dot", style={"background": PUB_COLORS[kind]})

#fixed legend for the bubble chart, it only explains the encoding and cannot be clicked
bubble_key = html.Div([html.B("Colour: "), *[html.Span([group_dot(k), k]) for k in PUB_CLASSES],
                       html.Span([html.B("Size: "), "total sales"])], className="key")

def hint(text):
    return html.Div([html.B("i"), html.Span(text)], className="hint")

def section(title, desc, graph_id, controls=None, note_id=None, figure=None, hint_text=None, tip=None, key=None):
    #one card per chart: heading, explanation, own controls, chart
    kids = [html.H3(title), html.P(desc, className="desc")]
    if hint_text:
        kids.append(hint(hint_text))
    if controls:
        kids.append(html.Div(controls, className="controls"))
    if note_id:
        kids.append(html.Div(id=note_id, className="note"))
    if tip:
        kids.append(html.Div([html.B("Tip: "), tip], className="tip"))
    if key:
        kids.append(key)
    kids.append(dcc.Graph(id=graph_id, figure=figure if figure is not None else {},
                          config={"displaylogo": False}))
    return html.Section(kids, className="card")

region_opts = [{"label": r, "value": r} for r in REGIONS]

#charts without controls are drawn once
rt = reg.groupby("region")["sales_millions"].sum().reindex(REGIONS).reset_index()
region_total_fig = finish(px.bar(
    rt, x="region", y="sales_millions", color="region", color_discrete_map=REGION_COLORS,
    labels={"region": column_label("region"), "sales_millions": column_label("sales_millions")}),
    height=360)
region_total_fig.update_layout(showlegend=False)

gs = reg.groupby(["region", "genre"], as_index=False)["sales_millions"].sum()
top3 = gs.sort_values("sales_millions", ascending=False).groupby("region").head(3)

#heat maps: same scale logic everywhere, from 0 to a round maximum with both ends labelled
def nice_max(v):
    step = 5 if v <= 40 else 10 if v <= 100 else 100
    return math.ceil(v / step) * step

def heatmap(df, fmt, bar_title, blank_below=0):
    zmax = nice_max(float(np.nanmax(df.values)))
    tick = 5 if zmax <= 40 else 10 if zmax <= 100 else 100
    text = df.apply(lambda col: col.map(lambda v: "" if pd.isna(v) or v < blank_below else format(v, fmt)))
    fig = go.Figure(go.Heatmap(
        z=df.values, x=list(df.columns), y=list(df.index), zmin=0, zmax=zmax,
        colorscale=HEAT_SCALE, xgap=1, ygap=1, text=text.values, texttemplate="%{text}",
        hovertemplate="%{y} / %{x}: %{z:.1f}<extra></extra>",
        colorbar={"orientation": "h", "x": 0, "xanchor": "left", "y": 1.0, "yanchor": "bottom",
                  "len": 420, "lenmode": "pixels", "thickness": 14, "outlinecolor": "#9aa5b1",
                  "outlinewidth": 1, "tickvals": list(range(0, int(zmax) + 1, tick))}))
    #title as annotation, so it starts exactly where the bar and the other legends start
    fig.add_annotation(text=bar_title, xref="paper", yref="paper", x=0, y=1, xanchor="left",
                       yanchor="bottom", yshift=44, showarrow=False, font={"size": 12})
    #dtick=1 forces a label for every row and column, otherwise plotly skips some
    fig.update_yaxes(autorange="reversed", tickmode="linear", dtick=1)
    fig.update_xaxes(tickmode="linear", dtick=1)
    return fig

#LAYOUT:

app = Dash(__name__, title="Game market")
app.index_string = app.index_string.replace("</head>", f"<style>{CSS}</style></head>")

LOW_HINT = (f"Sales figures are almost entirely missing for release years from {LOW_FROM} on, "
            "so a decline there says nothing about the industry.")

tab_platforms = dcc.Tab(label="Regions & Platforms", value="t1", className="folder-tab", selected_className="folder-tab--selected", children=[
    html.P("Which platforms lead the market, and how do regional preferences differ?", className="tab-intro"),
    section("Which platforms sell the most?",
            "Total sales of the best-selling platforms. Select a region to see its ranking, "
            "or keep all regions for the global view.",
            "p-bar", note_id="p-bar-note", controls=[
                control("Region", dcc.Dropdown(
                    id="p-region", clearable=False, value="All regions",
                    options=[{"label": "All regions", "value": "All regions"}] + region_opts)),
                control("Number of platforms", slider("p-n", 5, 20, 1, 10))]),
    section("Do regions prefer different platforms?",
            "Each cell shows how much of a region's total sales comes from one platform; darker "
            "cells mean a larger share. Only the top platforms are listed, so a column adds up "
            "to less than 100 %. Shares are used instead of volumes because the regions differ "
            "greatly in size.",
            "p-heat", controls=[
                control("Number of platforms", slider("p-heat-n", 5, 20, 1, 10))]),
    section("How large is each region?",
            "Total sales per region, based on records with reported sales. "
            "This puts the platform shares above into perspective.",
            "p-region-total", figure=region_total_fig),
])

tab_time = dcc.Tab(label="Trends over time", value="t2", className="folder-tab", selected_className="folder-tab--selected", children=[
    html.P("How have sales and genre preferences developed across release years?", className="tab-intro"),
    section("How have sales developed in each region?",
            "Sales by release year, one line per region.", "t-lines",
            controls=time_controls("tl") + [toggle("tl-regions", REGIONS, "Show or hide regions")],
            hint_text=LOW_HINT),
    section("Which release year sold the most worldwide?",
            "Global sales of all games released in a given year; the annotation marks the peak.",
            "t-global", note_id="t-global-note", controls=time_controls("tg"),
            hint_text=LOW_HINT),
    section("Which platform led each release year?",
            "The platform with the highest sales in each release year, showing how "
            "console generations succeed one another.", "t-best-platform",
            controls=time_controls("tb")),
    section("How has the genre mix changed?",
            "Genre composition of each release year's sales, shown as shares of the full year or "
            "as absolute sales. Genres with under 2 % of all releases are grouped as 'Other genres'.",
            "t-genre", controls=time_controls("tge", mode=True)
            + [toggle("tge-genres", GENRES, "Show or hide genres")]),
])

tab_genres = dcc.Tab(label="Genres", value="t3", className="folder-tab", selected_className="folder-tab--selected", children=[
    html.P("Which genres dominate each region, and which platforms specialise in a genre?", className="tab-intro"),
    section("Which genres do regions prefer?",
            "Each cell shows a genre's share of a region's total sales (share view, every column "
            "adds up to 100 %) or its absolute sales (sales view); darker cells mean a larger value. "
            "Genres with under 2 % of all releases are grouped as 'Other genres'.",
            "g-heat", controls=[control("Show as", radio("g-mode", "share"))]),
    section("Which are the top three genres in each region?",
            "The three best-selling genres per region, in millions of copies.",
            "g-top3", controls=[toggle("g3-regions", REGIONS, "Show or hide regions")]),
    section("Do platforms specialise in a genre?",
            "Share of each platform's releases by genre; every row adds up to 100 %. A single "
            "dark cell indicates a platform focused on one genre. Cells below 0.5 % are left blank "
            "and genres with under 2 % of all releases are grouped as 'Other genres'.",
            "g-spec", controls=[
                control("Min. releases per platform", slider("g-min", 100, 2000, 100, 1000))]),
])

tab_titles = dcc.Tab(label="Titles & Publishers", value="t4", className="folder-tab", selected_className="folder-tab--selected", children=[
    html.P("Which titles and publishers perform best, and where do regional results diverge?", className="tab-intro"),
    section("Which titles sold the most worldwide?",
            "Sales of each title, summed across all platforms it was released on.",
            "ti-bar", controls=[control("Number of titles", slider("ti-n", 5, 30, 1, 15))]),
    section("Which publishers sell steadily, and which depend on hits?",
            "Each bubble is one publisher. Horizontal position: average sales per release. "
            "Vertical position: how unpredictable these sales are, measured as standard deviation "
            "divided by mean. Below 1 means steady results; above 1.5 means a few blockbusters "
            "carry many weak releases. Bubble size shows total sales.",
            "pu-scatter", tip="Hover over a bubble to see which publisher it is.", key=bubble_key, controls=[
                control("Min. releases with sales per publisher", slider("pu-min", 5, 200, 5, 20)),
                toggle("pu-groups", PUB_CLASSES, "Show or hide publisher groups")]),
    section("Which titles are strong in one region but weak in another?",
            "Titles with the largest sales gap between a strong and a weak region, "
            "showing where a game needs a different regional strategy. Only titles with reported "
            "sales in both regions are compared.",
            "x-bars", note_id="x-note", controls=[
                control("Strong in", dcc.Dropdown(id="x-a", options=region_opts,
                                                  value="North America", clearable=False)),
                control("Weak in", dcc.Dropdown(id="x-b", options=region_opts,
                                                value="Japan", clearable=False)),
                control("Min. sales in strong region (millions)", slider("x-min", 1, 5, 1, 1))]),
])

app.layout = html.Div(className="page", children=[
    html.Header(className="page-header", children=[
        html.H1("Game Market Explorer"),
        html.P("Mythic Realm Studios \u00b7 Video game sales by region, platform, genre and publisher",
               className="subtitle"),
        html.P([html.B("Data basis: "),
                f"{len(games):,} game-platform records, of which only {COVERAGE:.1f}% include a global "
                "sales figure. All sales results therefore describe records with reported sales, not the "
                "whole market. Missing values are never treated as zero."], className="intro"),
    ]),
    dcc.Tabs(value="t1", className="folder-bar", content_className="folder-body",
             children=[tab_platforms, tab_time, tab_genres, tab_titles]),
])

#CALLBACKS:

#one callback per chart, so a chart only reacts to the controls in its own card

#"Show all" and "Clear" buttons of every checkbox group
def register_reset(checklist_id, values):
    @app.callback(Output(checklist_id, "value"),
                  Input(f"{checklist_id}-all", "n_clicks"), Input(f"{checklist_id}-none", "n_clicks"),
                  prevent_initial_call=True)
    def reset(_all, _none):
        return values if ctx.triggered_id == f"{checklist_id}-all" else []

for checklist_id, values in TOGGLES.items():
    register_reset(checklist_id, values)

#Regions and platforms
@app.callback(Output("p-bar", "figure"), Output("p-bar-note", "children"),
              Input("p-region", "value"), Input("p-n", "value"))
def platform_bar(region, n):
    d = reg if region == "All regions" else reg[reg["region"] == region]
    top = d.groupby("platform")["sales_millions"].sum().nlargest(n).reset_index()
    fig = px.bar(top, x="platform", y="sales_millions",
                 labels={"platform": column_label("platform"),
                         "sales_millions": column_label("sales_millions")})
    fig.update_traces(marker_color=REGION_COLORS.get(region, BASE_COLOR))
    return finish(fig), f"Showing: {region}"

@app.callback(Output("p-heat", "figure"), Input("p-heat-n", "value"))
def platform_heat(n):
    pv = reg.pivot_table(index="platform", columns="region",
                         values="sales_millions", aggfunc="sum").reindex(columns=REGIONS)
    share = pv.div(pv.sum()) * 100
    overall = reg.groupby("platform")["sales_millions"].sum().nlargest(n).index
    table = share.loc[overall]
    fig = heatmap(table, ".1f", "Share of the region's total sales (%)")
    return finish(fig, height=190 + 32 * len(table))

#Trends over time
def _filtered(rng, min_obs):
    return years(reg, rng, min_obs), years(tot, rng, min_obs)

@app.callback(Output("t-lines", "figure"), Input("tl-years", "value"), Input("tl-min", "value"),
              Input("tl-regions", "value"))
def trend_lines(rng, min_obs, regions):
    r, _ = _filtered(rng, min_obs)
    r = r[r["region"].isin(regions)]
    if r.empty:
        return empty("No data for this selection" if regions else "Select at least one region")
    by_reg = r.groupby(["release_year", "region"], as_index=False)["sales_millions"].sum()
    fig = px.line(by_reg, x="release_year", y="sales_millions", color="region", markers=True,
                  color_discrete_map=REGION_COLORS, category_orders={"region": REGIONS},
                  labels={"release_year": column_label("release_year"),
                          "region": column_label("region"),
                          "sales_millions": column_label("sales_millions")})
    return finish(low_data_band(fig, int(by_reg["release_year"].max())))

@app.callback(Output("t-global", "figure"), Output("t-global-note", "children"),
              Input("tg-years", "value"), Input("tg-min", "value"))
def trend_global(rng, min_obs):
    _, g = _filtered(rng, min_obs)
    if g.empty:
        return empty(), ""
    yearly = g.groupby("release_year", as_index=False)["total_sales"].sum()
    peak = yearly.loc[yearly["total_sales"].idxmax()]
    fig = px.bar(yearly, x="release_year", y="total_sales",
                 labels={"release_year": column_label("release_year"),
                         "total_sales": column_label("total_sales")})
    fig.update_traces(marker_color=BASE_COLOR)
    fig.add_annotation(x=peak["release_year"], y=peak["total_sales"], text="peak",
                       showarrow=True, arrowhead=2, ay=-30)
    return finish(low_data_band(fig, int(yearly["release_year"].max()))), f"Peak: {int(peak['release_year'])} ({peak['total_sales']:.0f} M copies)"

@app.callback(Output("t-best-platform", "figure"),
              Input("tb-years", "value"), Input("tb-min", "value"))
def trend_best_platform(rng, min_obs):
    _, g = _filtered(rng, min_obs)
    if g.empty:
        return empty()
    py = g.groupby(["release_year", "platform"], as_index=False)["total_sales"].sum()
    best = py.loc[py.groupby("release_year")["total_sales"].idxmax()]
    fig = px.bar(best, x="release_year", y="total_sales", color="platform",
                 labels={"release_year": column_label("release_year"),
                         "platform": column_label("platform"),
                         "total_sales": column_label("total_sales")})
    return finish(low_data_band(fig, int(best["release_year"].max())))

@app.callback(Output("t-genre", "figure"),
              Input("tge-years", "value"), Input("tge-min", "value"), Input("tge-mode", "value"),
              Input("tge-genres", "value"))
def trend_genre(rng, min_obs, mode, genres):
    _, g = _filtered(rng, min_obs)
    if g.empty:
        return empty()
    if not genres:
        return empty("Select at least one genre")
    ge = g.groupby(["release_year", "genre"], as_index=False)["total_sales"].sum()
    if mode == "share":
        ge["total_sales"] = (ge["total_sales"]
                             / ge.groupby("release_year")["total_sales"].transform("sum") * 100)
    ge = ge[ge["genre"].isin(genres)]   #shares stay relative to the full year
    fig = px.area(ge, x="release_year", y="total_sales", color="genre",
                  color_discrete_map=GENRE_COLORS, category_orders={"genre": GENRES},
                  labels={"release_year": column_label("release_year"),
                          "genre": column_label("genre"),
                          "total_sales": "Share of year (%)" if mode == "share"
                          else column_label("total_sales")})
    return finish(low_data_band(fig, int(ge["release_year"].max())), height=470)

#Genres
@app.callback(Output("g-heat", "figure"), Input("g-mode", "value"))
def genre_heat(mode):
    pv = reg.pivot_table(index="genre", columns="region",
                         values="sales_millions", aggfunc="sum").reindex(columns=REGIONS)
    if mode == "share":
        pv = pv.div(pv.sum()) * 100
    pv = pv.loc[pv.sum(axis=1).sort_values(ascending=False).index]
    fig = heatmap(pv, ".0f" if mode == "sales" else ".1f",
                  "Share of the region's total sales (%)" if mode == "share"
                  else "Sales (millions of copies)")
    return finish(fig, height=190 + 32 * len(pv))

@app.callback(Output("g-top3", "figure"), Input("g3-regions", "value"))
def genre_top3(regions):
    t = top3[top3["region"].isin(regions)]
    if t.empty:
        return empty("Select at least one region")
    fig = px.bar(t, x="region", y="sales_millions", color="genre", barmode="group",
                 color_discrete_map=GENRE_COLORS, category_orders={"region": REGIONS},
                 labels={"region": column_label("region"), "genre": column_label("genre"),
                         "sales_millions": column_label("sales_millions")})
    return finish(fig)

@app.callback(Output("g-spec", "figure"), Input("g-min", "value"))
def genre_specialisation(min_rows):
    counts = games["platform"].value_counts()
    sub = games[games["platform"].isin(counts[counts >= min_rows].index)]
    if sub.empty:
        return empty("No platform has that many releases")
    ct = pd.crosstab(sub["platform"], sub["genre"], normalize="index").reindex(columns=GENRES, fill_value=0) * 100
    ct = ct.loc[counts.reindex(ct.index).sort_values(ascending=False).index]
    ct.columns = [c.replace("-", "-<br>").replace(" ", "<br>") for c in ct.columns]   #short, horizontal labels
    fig = heatmap(ct, ".0f", "Share of the platform's releases (%)", blank_below=0.5)
    fig.update_xaxes(tickangle=0)
    return finish(fig, height=210 + 30 * len(ct))

#Titles and publishers
@app.callback(Output("ti-bar", "figure"), Input("ti-n", "value"))
def best_titles(n):
    top = (tot.groupby(title_key(tot["title"]))
              .agg(title=("title", "first"), sales=("total_sales", "sum"))
              .nlargest(n, "sales"))
    fig = px.bar(top, x="sales", y="title", orientation="h",
                 labels={"sales": column_label("total_sales"), "title": column_label("title")})
    fig.update_traces(marker_color=BASE_COLOR)
    fig.update_yaxes(autorange="reversed")
    return finish(fig, height=max(CHART_H, 60 + 26 * n))


@app.callback(Output("pu-scatter", "figure"),
              Input("pu-min", "value"), Input("pu-groups", "value"))
def publisher_bubbles(min_rows, groups):
    p = (tot[tot["publisher"].notna()].groupby("publisher")["total_sales"]
         .agg(n="size", total="sum", mean="mean", std="std").reset_index())
    p = p[(p["n"] >= min_rows) & (p["mean"] > 0)].copy()
    if p.empty:
        return empty("No publisher has that many releases with sales")
    p["cv"] = p["std"] / p["mean"]
    p["kind"] = pd.cut(p["cv"], [0, 1, 1.5, float("inf")], labels=PUB_CLASSES)
    p = p[p["kind"].isin(groups)]
    if p.empty:
        return empty("Select at least one publisher group")
    p = p.sort_values("total", ascending=False)   #big bubbles first, small ones stay on top

    fig = px.scatter(p, x="mean", y="cv", size="total", color="kind",
                     hover_name="publisher", log_x=True, size_max=30,
                     color_discrete_map=PUB_COLORS, category_orders={"kind": PUB_CLASSES},
                     hover_data={"kind": False, "n": True,
                                 "total": ":.1f", "mean": ":.2f", "cv": ":.2f"},
                     labels={"n": "Releases with sales", "total": "Total sales (millions)",
                             "mean": "Average sales per release (millions, log scale)",
                             "cv": "Hit-or-miss ratio (std ÷ mean)", "kind": "Publisher type"})
    fig.update_traces(marker={"opacity": 0.75, "line": {"width": 1, "color": "white"}})
    fig.update_layout(showlegend=False)
    fig.add_hline(y=1, line={"dash": "dot", "color": "#9aa5b1", "width": 1})
    fig.add_hline(y=1.5, line={"dash": "dot", "color": "#9aa5b1", "width": 1})
    fig.update_xaxes(tickvals=[0.01, 0.03, 0.1, 0.3, 1, 3],
                     ticktext=["0.01", "0.03", "0.1", "0.3", "1", "3"], minor={"showgrid": False})
    return finish(fig, height=520)

@app.callback(Output("x-bars", "figure"), Output("x-note", "children"),
              Input("x-a", "value"), Input("x-b", "value"), Input("x-min", "value"))
def region_gap(a, b, min_sales):
    note = f"Strong in {a}, weak in {b}"
    if a == b:
        return empty("Choose two different regions"), ""
    o = reg[reg["region"].isin([a, b])].assign(key=lambda d: title_key(d["title"]))
    w = o.pivot_table(index="key", columns="region", values="sales_millions", aggfunc="sum")
    if a not in w or b not in w:
        return empty(), ""
    w = w.dropna(subset=[a, b])
    w = w[w[a] >= min_sales]
    if w.empty:
        return empty("No titles match; lower the minimum sales"), ""
    w["gap"] = w[a] - w[b]
    top = w.nlargest(15, "gap")[[a, b]]
    top.index = o.groupby("key")["title"].first().reindex(top.index)
    fig = px.bar(top, orientation="h", barmode="group", color_discrete_map=REGION_COLORS,
                 labels={"value": column_label("sales_millions"),
                         "index": column_label("title"),
                         "variable": column_label("region")})
    fig.update_yaxes(autorange="reversed", title_text=column_label("title"))
    return finish(fig, height=max(CHART_H, 140 + 38 * len(top))), note

if __name__ == "__main__":
    app.run(debug=args.debug, host=args.host, port=args.port, threaded=False)