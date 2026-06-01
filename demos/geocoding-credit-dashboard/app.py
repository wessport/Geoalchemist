from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html


PALETTE = {
    "ink": "#111827",
    "muted": "#667085",
    "border": "#d9dee8",
    "panel": "#ffffff",
    "bg": "#f7f8fb",
    "blue": "#2563eb",
    "teal": "#14b8a6",
    "amber": "#f59e0b",
    "rose": "#e11d48",
    "purple": "#7c3aed",
}

PROVIDER_COLORS = {
    "Primary Geocoder": PALETTE["blue"],
    "Fallback Geocoder": PALETTE["rose"],
    "Autocomplete": PALETTE["teal"],
    "Batch Cleanup": PALETTE["purple"],
}


def make_demo_data() -> pd.DataFrame:
    rng = np.random.default_rng(77)
    dates = pd.date_range("2026-04-01", "2026-06-01", freq="D")
    countries = [
        ("Japan", "JPN", 1.00),
        ("United States", "USA", 0.75),
        ("United Kingdom", "GBR", 0.34),
        ("Canada", "CAN", 0.30),
        ("Germany", "DEU", 0.24),
        ("Australia", "AUS", 0.18),
    ]
    providers = [
        ("Primary Geocoder", 0.42, 1.00),
        ("Fallback Geocoder", 0.90, 0.18),
        ("Autocomplete", 0.12, 0.72),
        ("Batch Cleanup", 0.28, 0.20),
    ]

    rows: list[dict[str, object]] = []
    for day in dates:
        day_index = (day - dates[0]).days
        weekday = 1.22 if day.weekday() < 5 else 0.72
        trend = 1 + day_index / 260
        japan_spike = 1.0
        if pd.Timestamp("2026-05-10") <= day <= pd.Timestamp("2026-05-20"):
            japan_spike = 1.42

        for country, iso3, country_weight in countries:
            country_factor = country_weight * (japan_spike if country == "Japan" else 1.0)
            for provider, cost_per_1k, provider_weight in providers:
                base = 86_000 * country_factor * provider_weight * weekday * trend
                requests = max(900, int(base * rng.normal(1.0, 0.08)))
                cache_rate = np.clip(
                    rng.normal(0.58 + day_index / 850, 0.035)
                    - (0.07 if provider == "Fallback Geocoder" else 0),
                    0.32,
                    0.82,
                )
                billable = int(requests * (1 - cache_rate))
                credits = max(100, int(billable * rng.uniform(0.9, 1.12)))
                cost = round(credits / 1000 * cost_per_1k, 2)
                rows.append(
                    {
                        "date": day,
                        "country": country,
                        "iso3": iso3,
                        "provider": provider,
                        "requests": requests,
                        "cache_rate": cache_rate,
                        "credits": credits,
                        "cost": cost,
                    }
                )
    return pd.DataFrame(rows)


DATA = make_demo_data()
MIN_DATE = DATA["date"].min().date()
MAX_DATE = DATA["date"].max().date()


def filtered_data(start_date: str, end_date: str) -> pd.DataFrame:
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    return DATA[(DATA["date"] >= start) & (DATA["date"] <= end)].copy()


def metric_card(label: str, value: str, note: str, accent: str) -> html.Div:
    return html.Div(
        className="metric-card",
        style={"--accent": accent},
        children=[
            html.Div(label, className="metric-label"),
            html.Div(value, className="metric-value"),
            html.Div(note, className="metric-note"),
        ],
    )


def figure_layout(fig: go.Figure, subtitle: str | None = None) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=24, r=24, t=64, b=38),
        font=dict(family="Inter, sans-serif", color=PALETTE["ink"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="#e9edf5", zeroline=False)
    if subtitle:
        fig.add_annotation(
            text=subtitle,
            xref="paper",
            yref="paper",
            x=0,
            y=1.12,
            showarrow=False,
            align="left",
            font=dict(size=13, color=PALETTE["muted"]),
        )
    return fig


app = Dash(__name__, title="Geocoding Credit Dashboard")
server = app.server

app.layout = html.Div(
    className="page",
    children=[
        html.Div(
            className="hero",
            children=[
                html.Div("Synthetic demo", className="eyebrow"),
                html.H1("Geocoding Credit & Volume Dashboard"),
                html.P(
                    "A public demo for monitoring geocoding credit usage, request volume, cache behavior, and cost patterns."
                ),
            ],
        ),
        html.Div(
            className="controls",
            children=[
                html.Div(
                    className="control-block",
                    children=[
                        html.Label("Date range"),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=MIN_DATE,
                            max_date_allowed=MAX_DATE,
                            start_date=MIN_DATE,
                            end_date=MAX_DATE,
                            display_format="YYYY-MM-DD",
                        ),
                    ],
                ),
                html.Div(
                    className="control-block",
                    children=[
                        html.Label("Map metric"),
                        dcc.Dropdown(
                            id="map-metric",
                            clearable=False,
                            value="credits",
                            options=[
                                {"label": "Credits used", "value": "credits"},
                                {"label": "Estimated cost", "value": "cost"},
                                {"label": "Request volume", "value": "requests"},
                            ],
                        ),
                    ],
                ),
            ],
        ),
        html.Div(id="metrics", className="metrics-grid"),
        html.Div(
            className="chart-grid",
            children=[
                html.Div(
                    className="panel wide",
                    children=[
                        html.H2("Daily credit usage"),
                        dcc.Graph(id="credit-trend", config={"displayModeBar": False}),
                    ],
                ),
                html.Div(
                    className="panel",
                    children=[
                        html.H2("Spend by provider"),
                        dcc.Graph(id="provider-cost", config={"displayModeBar": False}),
                    ],
                ),
                html.Div(
                    className="panel",
                    children=[
                        html.H2("Country view"),
                        dcc.Graph(id="country-map", config={"displayModeBar": False}),
                    ],
                ),
            ],
        ),
        html.Div(
            className="note",
            children="This demo uses synthetic data only. It is designed to show the shape of the dashboard without exposing real providers, pricing, or internal usage data.",
        ),
    ],
)


@app.callback(
    Output("metrics", "children"),
    Output("credit-trend", "figure"),
    Output("provider-cost", "figure"),
    Output("country-map", "figure"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("map-metric", "value"),
)
def update_dashboard(start_date: str, end_date: str, map_metric: str):
    df = filtered_data(start_date, end_date)
    daily = df.groupby("date", as_index=False).agg(
        credits=("credits", "sum"), cost=("cost", "sum"), requests=("requests", "sum")
    )
    provider = df.groupby("provider", as_index=False).agg(cost=("cost", "sum"), credits=("credits", "sum"))
    country = df.groupby(["country", "iso3"], as_index=False).agg(
        credits=("credits", "sum"), cost=("cost", "sum"), requests=("requests", "sum")
    )

    total_cost = df["cost"].sum()
    total_credits = int(df["credits"].sum())
    total_requests = int(df["requests"].sum())
    cache_rate = 1 - (df["credits"].sum() / df["requests"].sum())
    japan_cost = country.loc[country["country"] == "Japan", "cost"].sum()

    cards = [
        metric_card("Estimated spend", f"${total_cost:,.0f}", "Synthetic period total", PALETTE["blue"]),
        metric_card("Credits used", f"{total_credits / 1_000_000:.1f}M", "Non-cached billable activity", PALETTE["teal"]),
        metric_card("Requests", f"{total_requests / 1_000_000:.1f}M", "Geocoding + autocomplete", PALETTE["purple"]),
        metric_card("Japan share", f"{japan_cost / total_cost:.0%}", "Useful for spotting market spikes", PALETTE["amber"]),
        metric_card("Cache offset", f"{cache_rate:.0%}", "Estimated requests avoided", PALETTE["rose"]),
    ]

    trend_fig = px.area(
        daily,
        x="date",
        y="credits",
        color_discrete_sequence=[PALETTE["blue"]],
    )
    trend_fig.update_traces(line=dict(width=3), fillcolor="rgba(37, 99, 235, 0.16)")
    trend_fig.update_layout(yaxis_title="Credits", xaxis_title=None, showlegend=False)
    figure_layout(trend_fig, "Daily totals make spikes easier to spot before they become monthly budget surprises.")

    cost_fig = px.bar(
        provider.sort_values("cost"),
        x="cost",
        y="provider",
        orientation="h",
        color="provider",
        color_discrete_map=PROVIDER_COLORS,
    )
    cost_fig.update_layout(xaxis_title="Estimated cost", yaxis_title=None, showlegend=False)
    figure_layout(cost_fig, "Provider-level spend helps separate normal volume from expensive fallback behavior.")

    metric_labels = {"credits": "Credits used", "cost": "Estimated cost", "requests": "Requests"}
    map_fig = px.choropleth(
        country,
        locations="iso3",
        color=map_metric,
        hover_name="country",
        color_continuous_scale=["#dbeafe", PALETTE["blue"], PALETTE["purple"]],
        projection="natural earth",
    )
    map_fig.update_layout(coloraxis_colorbar=dict(title=metric_labels[map_metric]), geo=dict(bgcolor="rgba(0,0,0,0)"))
    figure_layout(map_fig, "The country view is intentionally high-level: useful for finding where to investigate next.")

    return cards, trend_fig, cost_fig, map_fig


app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Newsreader:opsz,wght@6..72,500;6..72,700&display=swap" rel="stylesheet">
        <style>
            :root { color-scheme: light; }
            * { box-sizing: border-box; }
            body { margin: 0; background: #f7f8fb; color: #111827; font-family: Inter, sans-serif; }
            .page { max-width: 1420px; margin: 0 auto; padding: 72px 48px 54px; }
            .hero { border-bottom: 1px solid #d9dee8; padding-bottom: 32px; }
            .eyebrow { color: #2563eb; font-weight: 800; letter-spacing: .11em; text-transform: uppercase; font-size: 12px; margin-bottom: 12px; }
            h1 { font-family: Newsreader, serif; font-size: clamp(48px, 6vw, 84px); line-height: .9; letter-spacing: -0.055em; margin: 0 0 20px; }
            h2 { margin: 0 0 12px; font-size: 18px; letter-spacing: -0.02em; }
            .hero p { max-width: 720px; color: #475467; font-size: 18px; line-height: 1.6; margin: 0; }
            .controls { margin: 24px 0; background: white; border: 1px solid #d9dee8; border-radius: 22px; padding: 20px; display: flex; gap: 22px; align-items: end; box-shadow: 0 16px 40px rgba(17, 24, 39, 0.04); }
            .control-block { min-width: 280px; }
            label { display: block; color: #667085; font-size: 12px; font-weight: 800; margin-bottom: 8px; }
            .DateRangePickerInput, .Select-control { border: 1px solid #a7b0c2 !important; border-radius: 10px !important; min-height: 44px; }
            .metrics-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 16px; margin: 24px 0; }
            .metric-card { background: white; border: 1px solid #d9dee8; border-radius: 20px; padding: 18px; border-top: 4px solid var(--accent); box-shadow: 0 12px 28px rgba(17, 24, 39, 0.04); }
            .metric-label { color: #667085; font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: .08em; }
            .metric-value { font-size: 31px; font-weight: 800; letter-spacing: -0.06em; margin: 10px 0 6px; }
            .metric-note { color: #667085; font-size: 13px; line-height: 1.35; }
            .chart-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px; }
            .panel { background: white; border: 1px solid #d9dee8; border-radius: 24px; padding: 22px; min-height: 440px; box-shadow: 0 16px 40px rgba(17, 24, 39, 0.04); }
            .panel.wide { grid-column: 1 / -1; }
            .note { margin-top: 22px; color: #667085; font-size: 14px; line-height: 1.6; }
            @media (max-width: 980px) {
                .page { padding: 42px 20px; }
                .controls { display: block; }
                .control-block { min-width: 0; margin-bottom: 18px; }
                .metrics-grid, .chart-grid { grid-template-columns: 1fr; }
                .panel.wide { grid-column: auto; }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""


if __name__ == "__main__":
    app.run_server(debug=True)
