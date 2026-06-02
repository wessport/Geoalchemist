"""Geocoding credit dashboard.

This Dash app mirrors the layout of the original dashboard while using generated
sample data only. Labels are intentionally generic so it does not expose private
names, pricing, or operational data.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from io import StringIO
from math import log10
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dcc, html


app = Dash(__name__, title="Geocoding Credit & Volume Dashboard", suppress_callback_exceptions=True)
server = app.server

MAX_RANGE_DAYS = 90
DEMO_END_DATE = date(2026, 6, 1)
DEMO_START_DATE = DEMO_END_DATE - timedelta(days=61)

STREAM_LABELS = {
    "geocoding_a": "Geocoding stream A",
    "geocoding_b": "Geocoding stream B",
    "assist_a": "Assist stream A",
    "assist_b": "Assist stream B",
}

PROJECTION_MODES = {
    "total": {
        "columns": ["total_spend"],
        "title": "Estimated total 30-day credit burn projection",
        "description": "Extends the recent total spend run rate across geocoding, assist, and enrichment streams.",
        "observed": "Observed cumulative total spend",
        "projected": "Projected cumulative total spend",
    },
    "core": {
        "columns": ["geocode_spend", "assist_spend"],
        "title": "Estimated core 30-day credit burn projection",
        "description": "Extends the recent geocoding plus assist spend run rate while excluding enrichment traffic.",
        "observed": "Observed cumulative core spend",
        "projected": "Projected cumulative core spend",
    },
}

WORLD_COUNTRIES_GEOJSON_URL = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"

COUNTRIES = [
    ("US", "USA", "United States", 0.88),
    ("JP", "JPN", "Japan", 1.00),
    ("GB", "GBR", "United Kingdom", 0.42),
    ("CA", "CAN", "Canada", 0.36),
    ("DE", "DEU", "Germany", 0.31),
    ("AU", "AUS", "Australia", 0.26),
    ("FR", "FRA", "France", 0.22),
    ("BR", "BRA", "Brazil", 0.20),
    ("IN", "IND", "India", 0.19),
    ("MX", "MEX", "Mexico", 0.16),
    ("NL", "NLD", "Netherlands", 0.13),
    ("SG", "SGP", "Singapore", 0.11),
    ("ES", "ESP", "Spain", 0.10),
    ("IT", "ITA", "Italy", 0.09),
    ("SE", "SWE", "Sweden", 0.08),
]


@dataclass(frozen=True)
class DateRange:
    start: date
    end: date

    @property
    def days(self) -> int:
        return max((self.end - self.start).days, 1)


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def parse_date_range(start_value: str | None, end_value: str | None) -> DateRange:
    end = parse_date(end_value) or DEMO_END_DATE
    start = parse_date(start_value) or (end - timedelta(days=30))
    start = max(start, DEMO_START_DATE)
    end = min(end, DEMO_END_DATE)
    if start >= end:
        start = max(DEMO_START_DATE, end - timedelta(days=30))
    if (end - start).days > MAX_RANGE_DAYS:
        start = end - timedelta(days=MAX_RANGE_DAYS)
    return DateRange(start=start, end=end)


def previous_date_range(date_range: DateRange) -> DateRange:
    return DateRange(
        start=max(DEMO_START_DATE, date_range.start - timedelta(days=date_range.days)),
        end=date_range.start,
    )


def format_count(value: float) -> str:
    return f"{value:,.0f}"


def format_currency(value: float) -> str:
    return f"${value:,.2f}"


def format_delta(current_value: float, previous_value: float | None, formatter: Any = format_count) -> tuple[str, str]:
    if previous_value is None:
        return "No prior comparison", "delta-neutral"
    if previous_value == 0:
        return ("New volume vs prior", "delta-up") if current_value else ("No change vs prior", "delta-neutral")
    change = (current_value - previous_value) / previous_value * 100
    absolute_change = current_value - previous_value
    if absolute_change == 0:
        return "No change vs prior", "delta-neutral"
    direction = "▲" if change > 0 else "▼"
    css_class = "delta-up" if change > 0 else "delta-down"
    decimal_places = 2 if abs(change) < 0.1 else 1
    return f"{direction} {formatter(abs(absolute_change))} ({abs(change):.{decimal_places}f}%) vs prior", css_class


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0)


def make_demo_rows() -> pd.DataFrame:
    rng = np.random.default_rng(92)
    dates = pd.date_range(DEMO_START_DATE, DEMO_END_DATE, freq="D")
    stream_specs = {
        "geocoding_a": {"weight": 1.00, "unit_cost": 0.0048, "cache": 0.61},
        "geocoding_b": {"weight": 0.32, "unit_cost": 0.0011, "cache": 0.57},
        "assist_a": {"weight": 0.78, "unit_cost": 0.0012, "cache": 0.66},
        "assist_b": {"weight": 0.22, "unit_cost": 0.0010, "cache": 0.64},
        "enrichment_a": {"weight": 0.18, "unit_cost": 0.0036, "cache": 0.52},
        "enrichment_b": {"weight": 0.13, "unit_cost": 0.0015, "cache": 0.55},
    }
    rows: list[dict[str, object]] = []
    for day in dates:
        day_index = int((day.date() - DEMO_START_DATE).days)
        weekday = 1.18 if day.weekday() < 5 else 0.68
        trend = 1 + day_index / 360
        spike = 1.0
        if date(2026, 5, 9) <= day.date() <= date(2026, 5, 19):
            spike = 1.46
        for country, iso3, country_name, country_weight in COUNTRIES:
            country_factor = country_weight * (spike if country == "JP" else 1.0)
            for stream, spec in stream_specs.items():
                base = 94_000 * spec["weight"] * country_factor * weekday * trend
                requests = max(500, int(base * rng.normal(1.0, 0.08)))
                cache_rate = float(np.clip(rng.normal(spec["cache"] + day_index / 900, 0.035), 0.30, 0.84))
                cached = int(requests * cache_rate)
                non_cached = requests - cached
                spend = non_cached * spec["unit_cost"] * rng.uniform(0.94, 1.07)
                rows.append(
                    {
                        "date": day.date(),
                        "country": country,
                        "iso3": iso3,
                        "country_name": country_name,
                        "stream": stream,
                        "requests": requests,
                        "cached": cached,
                        "non_cached": non_cached,
                        "spend": round(spend, 2),
                    }
                )
    return pd.DataFrame(rows)


DEMO_DATA = make_demo_rows()


def range_data(date_range: DateRange) -> pd.DataFrame:
    return DEMO_DATA[(DEMO_DATA["date"] >= date_range.start) & (DEMO_DATA["date"] <= date_range.end)].copy()


def country_summary(df: pd.DataFrame, stream: str) -> pd.DataFrame:
    working = df[df["stream"] == stream]
    if working.empty:
        return pd.DataFrame(columns=["country", "iso3", "requests", "share"])
    grouped = (
        working.groupby(["country", "iso3"], as_index=False)
        .agg(requests=("non_cached", "sum"))
        .sort_values("requests", ascending=False)
    )
    total = grouped["requests"].sum()
    share = grouped["requests"].div(total).mul(100) if total else 0
    return grouped.assign(share=share)


def daily_summary(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby("date", as_index=False).agg(
        total_spend=("spend", "sum"),
        geocode_spend=("spend", lambda values: values[df.loc[values.index, "stream"].isin(["geocoding_a", "geocoding_b"])].sum()),
        assist_spend=("spend", lambda values: values[df.loc[values.index, "stream"].isin(["assist_a", "assist_b"])].sum()),
        geocoding_a_calls=("non_cached", lambda values: values[df.loc[values.index, "stream"] == "geocoding_a"].sum()),
        geocoding_b_calls=("non_cached", lambda values: values[df.loc[values.index, "stream"] == "geocoding_b"].sum()),
        assist_a_calls=("requests", lambda values: values[df.loc[values.index, "stream"] == "assist_a"].sum()),
        assist_b_calls=("requests", lambda values: values[df.loc[values.index, "stream"] == "assist_b"].sum()),
        enrichment_a_calls=("non_cached", lambda values: values[df.loc[values.index, "stream"] == "enrichment_a"].sum()),
        enrichment_b_calls=("non_cached", lambda values: values[df.loc[values.index, "stream"] == "enrichment_b"].sum()),
    )
    return grouped.sort_values("date")


def dashboard_values(date_range: DateRange) -> dict[str, Any]:
    df = range_data(date_range)
    return {
        "df": df,
        "daily": daily_summary(df),
        "geocoding_a": country_summary(df, "geocoding_a"),
        "geocoding_b": country_summary(df, "geocoding_b"),
        "assist_a": country_summary(df, "assist_a"),
        "assist_b": country_summary(df, "assist_b"),
        "kpis": {
            "geocoding_a": float(df.loc[df["stream"] == "geocoding_a", "non_cached"].sum()),
            "geocoding_b": float(df.loc[df["stream"] == "geocoding_b", "non_cached"].sum()),
            "assist_a": float(df.loc[df["stream"] == "assist_a", "requests"].sum()),
            "assist_b": float(df.loc[df["stream"] == "assist_b", "requests"].sum()),
            "enrichment_a": float(df.loc[df["stream"] == "enrichment_a", "non_cached"].sum()),
            "enrichment_b": float(df.loc[df["stream"] == "enrichment_b", "non_cached"].sum()),
            "geocode_spend": float(df.loc[df["stream"].isin(["geocoding_a", "geocoding_b"]), "spend"].sum()),
            "assist_spend": float(df.loc[df["stream"].isin(["assist_a", "assist_b"]), "spend"].sum()),
            "total_spend": float(df["spend"].sum()),
        },
    }


def base_layout(title: str) -> dict[str, Any]:
    return {
        "title": {
            "text": f"<b>{title}</b>",
            "x": 0,
            "xanchor": "left",
            "font": {"size": 18, "family": "Satoshi, -apple-system, BlinkMacSystemFont, sans-serif", "color": "#111827"},
        },
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Satoshi, -apple-system, BlinkMacSystemFont, sans-serif", "color": "#111827"},
        "margin": {"t": 58, "r": 24, "b": 48, "l": 56},
        "legend": {"orientation": "h", "y": -0.22},
        "xaxis": {"gridcolor": "rgba(17,24,39,0.08)", "zeroline": False},
        "yaxis": {"gridcolor": "rgba(17,24,39,0.08)", "zeroline": False},
        "hovermode": "x unified",
    }


def remove_plot_title(fig: go.Figure, *, top_margin: int = 18, right_margin: int = 24, bottom_margin: int = 48, left_margin: int = 56) -> go.Figure:
    fig.update_layout(title=None, margin={"t": top_margin, "r": right_margin, "b": bottom_margin, "l": left_margin})
    return fig


def chart_heading(title: str, description: str) -> html.Div:
    return html.Div([html.H2(title), html.P(description, className="chart-description")], className="chart-heading")


def build_daily_spend_chart(daily: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if not daily.empty:
        fig.add_trace(go.Scatter(x=daily["date"], y=numeric(daily["total_spend"]), name="Total", mode="lines+markers"))
        fig.add_trace(go.Scatter(x=daily["date"], y=numeric(daily["geocode_spend"]), name="Geocode", mode="lines+markers"))
        fig.add_trace(go.Scatter(x=daily["date"], y=numeric(daily["assist_spend"]), name="Assist", mode="lines+markers"))
    fig.update_layout(**base_layout("Daily provisional estimated spend"), yaxis_title="USD")
    return fig


def request_volume_series() -> list[tuple[str, str]]:
    return [
        ("Geocoding stream A", "geocoding_a_calls"),
        ("Geocoding stream B", "geocoding_b_calls"),
        ("Assist stream A", "assist_a_calls"),
        ("Assist stream B", "assist_b_calls"),
        ("Enrichment stream A", "enrichment_a_calls"),
        ("Enrichment stream B", "enrichment_b_calls"),
    ]


def build_request_volume_chart(daily: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if not daily.empty:
        for label, column in request_volume_series():
            fig.add_trace(go.Scatter(x=daily["date"], y=numeric(daily[column]), name=label, mode="lines"))
    fig.update_layout(**base_layout("Daily request volume by stream"), yaxis_title="Requests")
    return fig


def daily_trend_description(mode: str | None) -> str:
    if mode == "requests":
        return "Shows daily request volume by stream to separate geocoding, assist, and enrichment traffic."
    return "Shows daily provisional spend split across total, geocoding, and assist usage."


def build_daily_trend_figure(daily: pd.DataFrame, mode: str | None) -> go.Figure:
    return remove_plot_title(build_request_volume_chart(daily)) if mode == "requests" else remove_plot_title(build_daily_spend_chart(daily))


def projection_mode(mode: str | None) -> dict[str, Any]:
    return PROJECTION_MODES.get(mode or "total", PROJECTION_MODES["total"])


def build_projection_chart(daily: pd.DataFrame, mode: str | None = "total") -> go.Figure:
    config = projection_mode(mode)
    fig = go.Figure()
    if not daily.empty:
        working = daily.copy()
        spend_columns = [numeric(working[column]) for column in config["columns"]]
        working = working.assign(
            daily_spend=sum(spend_columns),
            cumulative_spend=sum(spend_columns).cumsum(),
        )
        fig.add_trace(go.Scatter(x=working["date"], y=working["cumulative_spend"], name=config["observed"], mode="lines", line={"color": "#2563eb", "width": 3}))
        recent = working["daily_spend"].tail(min(14, len(working)))
        daily_mean = max(float(recent.mean()), 0)
        daily_std = max(float(recent.std(ddof=0)), 0)
        low_increment = max(daily_mean - daily_std, 0)
        high_increment = daily_mean + daily_std
        last_value = float(working["cumulative_spend"].iloc[-1])
        last_date = pd.to_datetime(working["date"].iloc[-1])
        dates = [(last_date + timedelta(days=offset)).date() for offset in range(1, 31)]
        projected = [last_value + daily_mean * offset for offset in range(1, 31)]
        low_projection = [last_value + low_increment * offset for offset in range(1, 31)]
        high_projection = [last_value + high_increment * offset for offset in range(1, 31)]
        fig.add_trace(go.Scatter(x=dates, y=high_projection, name="Projection high", mode="lines", line={"color": "rgba(15, 118, 110, 0.25)", "width": 0}, hovertemplate="High projection: %{y:$,.0f}<extra></extra>", showlegend=False))
        fig.add_trace(go.Scatter(x=dates, y=low_projection, name="Projection range", mode="lines", fill="tonexty", fillcolor="rgba(15, 118, 110, 0.16)", line={"color": "rgba(15, 118, 110, 0.25)", "width": 0}, hovertemplate="Low projection: %{y:$,.0f}<extra></extra>"))
        fig.add_trace(go.Scatter(x=dates, y=projected, name=config["projected"], mode="lines", line={"color": "#0f766e", "width": 3, "dash": "dash"}, hovertemplate="Projected: %{y:$,.0f}<extra></extra>"))
    fig.update_layout(**base_layout(config["title"]), yaxis_title="Cumulative USD", xaxis_rangeslider_visible=False)
    return fig


def build_country_chart(title: str, country_df: pd.DataFrame) -> go.Figure:
    top = country_df.head(12).sort_values("requests", ascending=True)
    fig = go.Figure(go.Bar(x=top["requests"], y=top["country"], orientation="h", marker={"color": "#60a5fa"}, text=[format_count(value) for value in top["requests"]], textposition="auto"))
    fig.update_layout(**base_layout(title), xaxis_title="Requests", yaxis_title="Country")
    return fig


def build_cache_chart(df: pd.DataFrame) -> go.Figure:
    cache_rows = cache_summary_rows(df)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[row["label"] for row in cache_rows], y=[row["cached"] for row in cache_rows], name="Cached", marker={"color": "#5eead4"}))
    fig.add_trace(go.Bar(x=[row["label"] for row in cache_rows], y=[row["non_cached"] for row in cache_rows], name="Non-cache", marker={"color": "#fb923c"}))
    fig.update_layout(**base_layout("Cache behavior by geocoder surface"), barmode="stack", yaxis_title="Requests")
    return fig


def map_country_data(values: dict[str, Any], selected_map_stream: str | None) -> tuple[str, pd.DataFrame]:
    stream = selected_map_stream if selected_map_stream in STREAM_LABELS else "geocoding_a"
    return STREAM_LABELS[stream], values[stream]


def build_country_map(title: str, country_df: pd.DataFrame) -> go.Figure:
    working = country_df.copy()
    fig = go.Figure()
    if not working.empty:
        working = working.assign(color_value=numeric(working["requests"]).map(lambda value: log10(value + 1)))
        fig.add_trace(
            go.Choroplethmapbox(
                geojson=WORLD_COUNTRIES_GEOJSON_URL,
                locations=working["iso3"],
                z=working["color_value"],
                text=working["country"],
                customdata=working[["requests", "share"]],
                colorscale=[[0, "#dbeafe"], [0.42, "#38bdf8"], [0.72, "#2563eb"], [1, "#f97316"]],
                marker={"line": {"color": "#ffffff", "width": 0.7}, "opacity": 0.78},
                showscale=False,
                hovertemplate="<b>%{text}</b><br>Requests: %{customdata[0]:,.0f}<br>Share: %{customdata[1]:.2f}%<extra></extra>",
            )
        )
    layout = base_layout(title)
    layout["margin"] = {"t": 50, "r": 8, "b": 4, "l": 8}
    layout.pop("hovermode", None)
    fig.update_layout(**layout, mapbox={"center": {"lat": 25, "lon": 0}, "style": "carto-positron", "zoom": 1.35})
    return fig


def map_color_legend(country_df: pd.DataFrame) -> html.Div:
    if country_df.empty:
        low_label = "Low"
        high_label = "High"
    else:
        requests = numeric(country_df["requests"])
        low_label = format_count(float(requests.min()))
        high_label = format_count(float(requests.max()))
    return html.Div(
        [html.Span("Volume color (log scale)", className="map-legend-label"), html.Span(low_label, className="map-legend-value"), html.Span(className="map-legend-ramp"), html.Span(high_label, className="map-legend-value")],
        className="map-legend",
    )


def kpi_card(label: str, value: str, hint: str, delta: tuple[str, str], theme: str) -> html.Article:
    delta_text, delta_class = delta
    return html.Article([html.Div(label, className="metric-label"), html.Div(value, className="metric-value"), html.Div(hint, className="metric-hint"), html.Div(delta_text, className=f"kpi-delta {delta_class}")], className=f"metric-tile metric-theme-{theme}", title=hint)


def build_metric_split_donut(kpis: list[tuple[str, str, Any, str, str]], values: dict[str, float], colors: list[str]) -> go.Figure:
    labels = [label for label, *_rest in kpis]
    metric_values = [values[kpi_key] for _label, kpi_key, *_rest in kpis]
    fig = go.Figure(go.Pie(labels=labels, values=metric_values, hole=0.68, marker={"colors": colors, "line": {"color": "#ffffff", "width": 2}}, sort=False, textinfo="label+percent", textposition="outside", textfont={"size": 10, "color": "#6b7280"}, hovertemplate="%{label}<br>%{value:,.0f}<br>%{percent}<extra></extra>"))
    fig.update_layout(annotations=[{"text": format_count(sum(metric_values)), "x": 0.5, "y": 0.5, "font": {"size": 14, "color": "#111827"}, "showarrow": False}], paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={"family": "Satoshi, -apple-system, BlinkMacSystemFont, sans-serif", "color": "#111827"}, margin={"t": 2, "r": 2, "b": 2, "l": 2}, showlegend=False)
    return fig


def metric_group(title: str, kpis: list[tuple[str, str, Any, str, str]], values: dict[str, float], previous_values: dict[str, float], theme: str, graph_config: dict[str, Any], donut_colors: list[str] | None = None) -> html.Section:
    cards = [kpi_card(label, formatter(values[kpi_key]), hint, format_delta(values[kpi_key], previous_values.get(kpi_key), formatter), theme) for label, kpi_key, formatter, hint, theme in kpis]
    children: list[Any] = [html.H3(title), html.Div(cards, className="metric-stack")]
    if donut_colors is not None:
        children.append(dcc.Graph(figure=build_metric_split_donut(kpis, values, donut_colors), config=graph_config, className="metric-donut"))
    return html.Section(children, className=f"metric-group metric-group-{theme}")


def html_table(rows: list[dict[str, str]], columns: list[str]) -> html.Div:
    return html.Div(html.Table([html.Thead(html.Tr([html.Th(column) for column in columns]))] + [html.Tbody([html.Tr([html.Td(row[column]) for column in columns]) for row in rows])]), className="table-wrap")


def display_table(country_df: pd.DataFrame) -> list[dict[str, str]]:
    return [{"Country": row.country, "Requests": format_count(row.requests), "Share": f"{row.share:.2f}%"} for row in country_df.head(15).itertuples(index=False)]


def market_share_rows(values: dict[str, Any]) -> list[dict[str, str]]:
    rows = []
    for stream, label in STREAM_LABELS.items():
        country_df = values[stream]
        total = float(country_df["requests"].sum()) if not country_df.empty else 0
        counts = country_df.set_index("country")["requests"].to_dict() if total else {}
        us_count = float(counts.get("US", 0))
        jp_count = float(counts.get("JP", 0))
        source_df = values["df"][values["df"]["stream"] == stream]
        cached = float(source_df["cached"].sum())
        denominator = total + cached
        rows.append(
            {
                "Source": label,
                "Requests": format_count(total),
                "US requests": format_count(us_count),
                "US share": f"{(us_count / total * 100):.2f}%" if total else "0.00%",
                "JP requests": format_count(jp_count),
                "JP share": f"{(jp_count / total * 100):.2f}%" if total else "0.00%",
                "Cached": format_count(cached),
                "Cache rate": f"{(cached / denominator * 100):.2f}%" if denominator else "0.00%",
            }
        )
    return rows


def cache_summary_rows(df: pd.DataFrame) -> list[dict[str, Any]]:
    labels = {
        "geocoding_a": "Geocoding A",
        "geocoding_b": "Geocoding B",
        "enrichment_a": "Enrichment A",
        "enrichment_b": "Enrichment B",
    }
    rows = []
    for stream, label in labels.items():
        stream_df = df[df["stream"] == stream]
        rows.append({"label": label, "cached": float(stream_df["cached"].sum()), "non_cached": float(stream_df["non_cached"].sum())})
    return rows


def cache_display_rows(df: pd.DataFrame) -> list[dict[str, str]]:
    rows = []
    for row in cache_summary_rows(df):
        total = row["cached"] + row["non_cached"]
        rows.append({"Surface": row["label"], "Cached": format_count(row["cached"]), "Non-cache": format_count(row["non_cached"]), "Cache rate": f"{(row['cached'] / total * 100):.2f}%" if total else "0.00%"})
    return rows


def combined_daily_trend_panel(daily: pd.DataFrame, graph_config: dict[str, Any]) -> html.Section:
    return html.Section(
        [html.Div([html.H2("Daily trend"), dcc.RadioItems(id="daily-trend-mode", options=[{"label": "Spend", "value": "spend"}, {"label": "Requests", "value": "requests"}], value="spend", className="chart-toggle-radio")], className="chart-toggle-heading"), html.P(daily_trend_description("spend"), id="daily-trend-description", className="chart-description"), dcc.Store(id="daily-trend-data", data=daily.to_json(orient="split", date_format="iso")), dcc.Graph(id="daily-trend-chart", figure=build_daily_trend_figure(daily, "spend"), config=graph_config, className="chart toggle-chart")],
        className="panel chart-panel toggle-panel",
    )


def credit_burn_projection_panel(daily: pd.DataFrame, graph_config: dict[str, Any]) -> html.Section:
    config = projection_mode("total")
    return html.Section(
        [html.Div([html.H2(config["title"], id="credit-burn-title"), dcc.RadioItems(id="credit-burn-mode", options=[{"label": "Total", "value": "total"}, {"label": "Core", "value": "core"}], value="total", className="chart-toggle-radio")], className="chart-toggle-heading"), html.P(config["description"], id="credit-burn-description", className="chart-description"), dcc.Store(id="credit-burn-data", data=daily.to_json(orient="split", date_format="iso")), dcc.Graph(id="credit-burn-chart", figure=remove_plot_title(build_projection_chart(daily, "total")), config=graph_config, className="chart toggle-chart")],
        className="panel chart-panel",
    )


def caveats_panel() -> html.Section:
    return html.Section(
        [
            html.H2("Notes and caveats"),
            html.Ul(
                [
                    html.Li("Uses generated sample data only; no private usage, pricing, or operational data is included."),
                    html.Li("Country-code normalization is shown because dashboard inputs often mix ISO2, ISO3, and market aliases."),
                    html.Li("Spend and projections are illustrative run-rate estimates, not billing statements or forecasts."),
                    html.Li("Assist volumes are usage proxies and should not be treated as direct billed-credit truth."),
                ]
            ),
        ],
        className="panel caveats",
    )


def render_dashboard(date_range: DateRange, selected_map_stream: str | None) -> html.Div:
    values = dashboard_values(date_range)
    previous_values = dashboard_values(previous_date_range(date_range))["kpis"]
    graph_config = {"responsive": True, "displayModeBar": False}
    map_config = {**graph_config, "scrollZoom": True}
    kpis = [
        ("Stream A", "geocoding_a", format_count, "non-cache requests", "geocode"),
        ("Stream B", "geocoding_b", format_count, "non-cache requests", "geocode"),
        ("Assist A", "assist_a", format_count, "front-door proxy", "autocomplete"),
        ("Assist B", "assist_b", format_count, "front-door proxy", "autocomplete"),
        ("Enrich A", "enrichment_a", format_count, "non-cache requests", "profile"),
        ("Enrich B", "enrichment_b", format_count, "non-cache requests", "profile"),
        ("Geocode $", "geocode_spend", format_currency, "sample unit costs", "spend"),
        ("Assist $", "assist_spend", format_currency, "sample unit costs", "spend"),
        ("Total $", "total_spend", format_currency, "sample period total", "spend"),
    ]
    map_title, map_df = map_country_data(values, selected_map_stream)
    prior_range = previous_date_range(date_range)
    kpi_delta_note = f"KPI deltas compare the selected {date_range.days}-day window with the immediately preceding {date_range.days} days ({prior_range.start:%Y-%m-%d}–{prior_range.end:%Y-%m-%d})."
    return html.Div(
        [
            html.Section(
                [
                    html.Article(
                        [
                            chart_heading(map_title, "Shows where selected-period request volume is concentrated by country; the map stream control updates this map only."),
                            dcc.Graph(figure=remove_plot_title(build_country_map(map_title, map_df), top_margin=8, right_margin=8, bottom_margin=4, left_margin=8), config=map_config, className="map-chart", style={"height": "660px"}),
                            map_color_legend(map_df),
                            html.P("Color is based on log-scaled selected-period request volume.", className="map-note"),
                        ],
                        className="panel map-panel",
                    ),
                    html.Div(
                        [
                            metric_group("Geocoding", kpis[:2], values["kpis"], previous_values, "geocode", graph_config, ["#2563eb", "#93c5fd"]),
                            metric_group("Assist", kpis[2:4], values["kpis"], previous_values, "autocomplete", graph_config, ["#7c3aed", "#c4b5fd"]),
                            metric_group("Enrichment", kpis[4:6], values["kpis"], previous_values, "profile", graph_config, ["#0f766e", "#5eead4"]),
                            metric_group("Spend", kpis[6:], values["kpis"], previous_values, "spend", graph_config),
                        ],
                        className="metric-groups",
                    ),
                    html.P(kpi_delta_note, className="kpi-footnote"),
                ],
                className="map-layout",
            ),
            html.Div([html.Span(className="section-divider-line"), html.Span("Detailed tables and charts below use the full selected dashboard window, independent of the map stream selector.", className="section-divider-text"), html.Span(className="section-divider-line")], className="section-divider"),
            html.Section([html.Div([html.P("US/JP volume and cache mix", className="eyebrow"), html.H2("Highest-volume market share by stream"), html.P("Shows selected-period request volume, US and JP contribution, and cache context where the stream has a cache concept.", className="section-description")], className="section-heading"), html_table(market_share_rows(values), ["Source", "Requests", "US requests", "US share", "JP requests", "JP share", "Cached", "Cache rate"])], className="panel"),
            combined_daily_trend_panel(values["daily"], graph_config),
            credit_burn_projection_panel(values["daily"], graph_config),
            html.Section(
                [
                    html.Article([chart_heading("Top countries by geocoding stream A", "Ranks the largest country contributors to non-cached geocoding volume in the selected period."), dcc.Graph(figure=remove_plot_title(build_country_chart("Top countries by geocoding stream A", values["geocoding_a"])), config=graph_config, className="chart")], className="panel chart-panel"),
                    html.Article([chart_heading("Top countries by geocoding stream B", "Ranks the largest country contributors to secondary non-cached geocoding volume in the selected period."), dcc.Graph(figure=remove_plot_title(build_country_chart("Top countries by geocoding stream B", values["geocoding_b"])), config=graph_config, className="chart")], className="panel chart-panel"),
                ],
                className="two-column",
            ),
            html.Section([html.Article([html.H2("Top geocoding stream A countries"), html_table(display_table(values["geocoding_a"]), ["Country", "Requests", "Share"])], className="panel"), html.Article([html.H2("Top geocoding stream B countries"), html_table(display_table(values["geocoding_b"]), ["Country", "Requests", "Share"])], className="panel")], className="two-column"),
            html.Section([chart_heading("Cache behavior by geocoder surface", "Compares cached and non-cached request volume to show where traffic is most likely to consume credits."), dcc.Graph(figure=remove_plot_title(build_cache_chart(values["df"])), config=graph_config, className="chart")], className="panel chart-panel"),
            html.Section([html.H2("Cache summary"), html_table(cache_display_rows(values["df"]), ["Surface", "Cached", "Non-cache", "Cache rate"])], className="panel"),
            caveats_panel(),
        ]
    )


def layout() -> html.Div:
    default_end = DEMO_END_DATE
    default_start = default_end - timedelta(days=30)
    return html.Div(
        [
            html.Header([html.H1("Geocoding Credit & Volume Dashboard"), html.P("High-level monitoring for geocoding/assist credit consumption, request volume, cache behavior, and normalized market share.")], className="dashboard-header"),
            html.Div(
                [
                    html.Div([html.Label("Date range"), dcc.DatePickerRange(id="date-range", start_date=default_start.isoformat(), end_date=default_end.isoformat(), min_date_allowed=DEMO_START_DATE, max_date_allowed=DEMO_END_DATE, display_format="YYYY-MM-DD", minimum_nights=1, className="date-range-picker")], className="date-control"),
                    html.Button("Refresh data", id="refresh-button", n_clicks=0),
                    html.Div([html.Label("Map stream (map only)"), dcc.Dropdown(id="map-stream", options=[{"label": label, "value": value} for value, label in STREAM_LABELS.items()], value="geocoding_a", clearable=False, className="map-stream-select"), html.Span("Changes only the country map.", className="control-help")], className="map-stream-control"),
                    html.Span(id="range-note", className="range-note"),
                ],
                className="controls-bar",
            ),
            html.Div(id="dashboard-content"),
        ],
        className="dashboard-container",
    )


app.layout = layout


@app.callback(
    Output("dashboard-content", "children"),
    Output("range-note", "children"),
    Input("refresh-button", "n_clicks"),
    Input("map-stream", "value"),
    State("date-range", "start_date"),
    State("date-range", "end_date"),
)
def update_dashboard(_n_clicks: int, selected_map_stream: str | None, start_date: str | None, end_date: str | None) -> tuple[html.Div, str]:
    date_range = parse_date_range(start_date, end_date)
    return render_dashboard(date_range, selected_map_stream), f"Selected {date_range.days}-day window."


@app.callback(Output("daily-trend-chart", "figure"), Output("daily-trend-description", "children"), Input("daily-trend-mode", "value"), State("daily-trend-data", "data"))
def update_daily_trend(mode: str | None, serialized_daily_data: str | None) -> tuple[go.Figure, str]:
    daily = pd.read_json(StringIO(serialized_daily_data), orient="split") if serialized_daily_data else pd.DataFrame()
    return build_daily_trend_figure(daily, mode), daily_trend_description(mode)


@app.callback(Output("credit-burn-title", "children"), Output("credit-burn-chart", "figure"), Output("credit-burn-description", "children"), Input("credit-burn-mode", "value"), State("credit-burn-data", "data"))
def update_credit_burn_projection(mode: str | None, serialized_daily_data: str | None) -> tuple[str, go.Figure, str]:
    daily = pd.read_json(StringIO(serialized_daily_data), orient="split") if serialized_daily_data else pd.DataFrame()
    config = projection_mode(mode)
    return config["title"], remove_plot_title(build_projection_chart(daily, mode)), config["description"]


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)
