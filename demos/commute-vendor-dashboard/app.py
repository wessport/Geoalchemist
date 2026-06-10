#!/usr/bin/env python3
"""Commute Vendor Analysis Dashboard — TravelTime vs Google Maps.

Interactive Dash dashboard for evaluating TravelTime commute time estimates
against Google Maps Routes API as a reference across 11 international markets.

Usage:
    python app.py
"""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, radians, sin, sqrt
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, callback, dash_table, dcc, html

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PARQUET_PATH = PROJECT_ROOT / "data" / "dashboard_data.parquet"
DB_PATH = str(PROJECT_ROOT / "commute_cache.duckdb")
SAMPLES_DIR = PROJECT_ROOT / "data" / "samples"
CITY_EXPANSION_SUMMARY_PATH = (
    PROJECT_ROOT / "data" / "coverage" / "non_us_top20_city_tt_google_summary_100.csv"
)

ALL_MARKETS = ["US", "DE", "GB", "CA", "FR", "NL", "IT", "IE", "AU", "BE", "CH"]


@dataclass(frozen=True)
class MetroArea:
    name: str
    market: str
    lat: float
    lng: float


METRO_AREAS = [
    MetroArea("New York", "US", 40.7128, -74.0060),
    MetroArea("Chicago", "US", 41.8781, -87.6298),
    MetroArea("Los Angeles", "US", 34.0522, -118.2437),
    MetroArea("Toronto", "CA", 43.6532, -79.3832),
    MetroArea("Vancouver", "CA", 49.2827, -123.1207),
    MetroArea("London", "GB", 51.5074, -0.1278),
    MetroArea("Manchester", "GB", 53.4808, -2.2426),
    MetroArea("Berlin", "DE", 52.5200, 13.4050),
    MetroArea("Munich", "DE", 48.1351, 11.5820),
    MetroArea("Paris", "FR", 48.8566, 2.3522),
    MetroArea("Amsterdam", "NL", 52.3676, 4.9041),
    MetroArea("Milan", "IT", 45.4642, 9.1900),
    MetroArea("Dublin", "IE", 53.3498, -6.2603),
    MetroArea("Sydney", "AU", -33.8688, 151.2093),
    MetroArea("Melbourne", "AU", -37.8136, 144.9631),
    MetroArea("Brussels", "BE", 50.8503, 4.3517),
    MetroArea("Zurich", "CH", 47.3769, 8.5417),
]


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    p1 = radians(lat1)
    p2 = radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(p1) * cos(p2) * sin(dlambda / 2) ** 2
    return float(2 * radius * atan2(sqrt(a), sqrt(1 - a)))


def get_metro_area(lat: float, lng: float) -> MetroArea | None:
    return min(METRO_AREAS, key=lambda metro: haversine_km(lat, lng, metro.lat, metro.lng))

# ── ggplot2 default colour palettes ─────────────────────────────────────────
# Generated via scales::hue_pal()(n) in R — equally spaced HCL hues
GGPLOT_2 = ["#F8766D", "#00BFC4"]
GGPLOT_2_ALT = ["#D89000", "#9590FF"]  # amber / purple — for adjacent charts
GGPLOT_11 = [
    "#F8766D", "#D89000", "#A3A500", "#39B600", "#00BF7D",
    "#00BFC4", "#00B0F6", "#9590FF", "#E76BF3", "#FF62BC", "#FF6A98",
]
GGPLOT_3 = ["#F8766D", "#00BA38", "#619CFF"]
CITY_EXPANSION_MARKET_COLORS = dict(zip(["CA", "GB", "FR"], GGPLOT_3))

MODE_COLORS = {"driving": GGPLOT_2[0], "transit": GGPLOT_2[1]}
MODE_COLORS_TITLE = {"Driving": GGPLOT_2[0], "Transit": GGPLOT_2[1]}
MODE_COLORS_ALT = {"Driving": GGPLOT_2_ALT[0], "Transit": GGPLOT_2_ALT[1]}
MARKET_COLOR_MAP = dict(zip(ALL_MARKETS, GGPLOT_11))

# ── Theme colours (light theme matching jobseeker-feedback-dash) ────────────
C = {
    "bg_primary": "#f8f9fa",
    "bg_secondary": "#ffffff",
    "bg_card": "#ffffff",
    "bg_input": "#f3f4f6",
    "border": "#e5e7eb",
    "border_hover": "#d1d5db",
    "text_primary": "#111827",
    "text_secondary": "#374151",
    "text_muted": "#6b7280",
}

PLOTLY_TEMPLATE = dict(
    layout=dict(
        font=dict(family="Inter, -apple-system, sans-serif", color=C["text_primary"]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="rgba(0,0,0,0.06)", linecolor=C["border"]),
        yaxis=dict(gridcolor="rgba(0,0,0,0.06)", linecolor=C["border"]),
        margin=dict(l=48, r=24, t=48, b=36),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
)

# ── Chart descriptions ──────────────────────────────────────────────────────
DESC = {
    "bias": (
        "Which direction does TravelTime err in each market?\n"
        "Negative = TT underestimates (shorter than Google). Positive = TT overestimates."
    ),
    "driving_cov": (
        "Driving coverage for both providers by market.\n"
        "Shows the percentage of driving OD pairs where each provider returned a valid route."
    ),
    "median_diff": (
        "How far off is TravelTime on average?\n"
        "Shows the median absolute difference in minutes between TT and Google for each market.\n"
        "Lower is better."
    ),
    "within_10": (
        "What share of route estimates are close enough?\n"
        "Shows the percentage of OD pairs where TravelTime was within ±10 minutes of Google."
    ),
    "transit_cov": (
        "TT = % of all transit pairs where TravelTime returned a result.\n"
        "vs Google = of pairs where Google returned a result, what % did TT also return a result?\n"
        "The gap between the two shows how much of TT's 'missing' coverage is routes Google also can't serve."
    ),
    "transit_dist": (
        "Straight-line (haversine) distance distribution of transit OD pairs by market.\n"
        "Shows median, quartiles, and outliers for each market.\n"
        "Provides context for interpreting transit accuracy and coverage."
    ),
    "od_map": (
        "Geographic distribution of OD pairs, showing origin and destination connected by lines.\n"
        "Switch between transit and driving modes. Toggle coloring by TT response status or market."
    ),
    "scatter": (
        "Each dot is one OD pair.\n"
        "Points on the dashed y=x line mean TT and Google agree exactly.\n"
        "Points above the line = TT overestimates; below = TT underestimates."
    ),
    "hist": (
        "How are the errors distributed?\n"
        "The x-axis shows TT minus Google in minutes.\n"
        "A peak left of zero means TT systematically underestimates."
    ),
    "dist_band": (
        "Does accuracy change with route distance?\n"
        "Shows within-±10 min rate by straight-line (haversine) distance band."
    ),
    "time_band": (
        "Does accuracy change with commute length?\n"
        "Shows within-±10 min rate by Google's estimated commute time band."
    ),
}


# ═══════════════════════════════════════════════════════════════════════════
# Data loading (runs once at startup)
# ═══════════════════════════════════════════════════════════════════════════

def _load_market_coord_sets() -> dict[str, set[tuple[float, ...]]]:
    return {}


def _assign_market(row: pd.Series, coord_sets: dict[str, set]) -> str:
    key = (
        round(row["origin_lat"], 6),
        round(row["origin_lng"], 6),
        round(row["dest_lat"], 6),
        round(row["dest_lng"], 6),
    )
    for market, coords in coord_sets.items():
        if key in coords:
            return market

    origin_metro = get_metro_area(row["origin_lat"], row["origin_lng"])
    if origin_metro:
        return origin_metro.market

    dest_metro = get_metro_area(row["dest_lat"], row["dest_lng"])
    if dest_metro:
        return dest_metro.market

    return "UNKNOWN"


def _load_raw_data() -> pd.DataFrame:
    """Generate public sample commute results with the original dashboard shape."""
    rng = np.random.default_rng(9357)
    rows: list[dict[str, object]] = []
    providers = {
        "google": {"coverage": 0.97, "bias": 0.0, "noise": 1.5},
        "traveltime": {"coverage": 0.90, "bias": -2.8, "noise": 6.0},
        "valhalla": {"coverage": 0.76, "bias": 5.5, "noise": 10.0},
    }
    market_factor = {
        "US": 1.00, "DE": 0.92, "GB": 0.95, "CA": 1.05, "FR": 0.94, "NL": 0.88,
        "IT": 1.03, "IE": 1.08, "AU": 1.10, "BE": 0.91, "CH": 0.89,
    }
    row_id = 1
    for metro in METRO_AREAS:
        market = metro.market
        for idx in range(120):
            mode = "transit" if idx % 2 else "driving"
            origin_lat = round(metro.lat + rng.normal(0, 0.18 if market != "AU" else 0.26), 6)
            origin_lng = round(metro.lng + rng.normal(0, 0.22 / max(cos(radians(metro.lat)), 0.4)), 6)
            dest_lat = round(metro.lat + rng.normal(0, 0.20 if mode == "driving" else 0.16), 6)
            dest_lng = round(metro.lng + rng.normal(0, 0.24 / max(cos(radians(metro.lat)), 0.4)), 6)
            distance_km = max(1.2, haversine_km(origin_lat, origin_lng, dest_lat, dest_lng))
            base_speed = 34 if mode == "driving" else 22
            base_time_min = distance_km / base_speed * 60 + (8 if mode == "transit" else 4)
            google_time_min = max(5, base_time_min * market_factor[market] + rng.normal(0, 2.5))
            for provider, profile in providers.items():
                coverage = profile["coverage"]
                if provider == "valhalla" and market not in {"US", "CA", "GB", "DE"}:
                    coverage -= 0.18
                if mode == "transit" and provider != "google":
                    coverage -= 0.07
                if rng.random() > coverage:
                    status = "no_route" if rng.random() > 0.18 else "error"
                    travel_time_seconds = np.nan
                    distance_meters = np.nan
                else:
                    status = "ok"
                    bias = profile["bias"]
                    if provider == "traveltime" and market in {"GB", "NL", "CH"}:
                        bias -= 2.0
                    if provider == "valhalla" and market in {"CA", "AU"}:
                        bias += 8.0
                    provider_time = google_time_min if provider == "google" else google_time_min + bias + rng.normal(0, profile["noise"])
                    travel_time_seconds = max(3, provider_time) * 60
                    distance_meters = distance_km * 1000 * rng.uniform(1.08, 1.45)
                rows.append({
                    "id": row_id,
                    "mode": mode,
                    "provider": provider,
                    "status": status,
                    "origin_lat": origin_lat,
                    "origin_lng": origin_lng,
                    "dest_lat": dest_lat,
                    "dest_lng": dest_lng,
                    "travel_time_seconds": travel_time_seconds,
                    "distance_meters": distance_meters,
                })
                row_id += 1
    return pd.DataFrame(rows)


_RAW_DF: pd.DataFrame | None = None


def _get_raw_data() -> pd.DataFrame:
    global _RAW_DF
    if _RAW_DF is None:
        _RAW_DF = _load_raw_data()
    return _RAW_DF


def load_paired_results() -> pd.DataFrame:
    raw = _get_raw_data()
    g = raw[(raw["provider"] == "google") & (raw["status"] == "ok")].copy()
    t = raw[(raw["provider"] == "traveltime") & (raw["status"] == "ok")].copy()

    # Round coords for join
    for col in ["origin_lat", "origin_lng", "dest_lat", "dest_lng"]:
        g[col] = g[col].round(6)
        t[col] = t[col].round(6)

    join_cols = ["mode", "origin_lat", "origin_lng", "dest_lat", "dest_lng"]
    df = g.merge(t, on=join_cols, suffixes=("_g", "_t"))
    df = df.rename(columns={
        "travel_time_seconds_g": "g_time",
        "distance_meters_g": "g_dist",
        "travel_time_seconds_t": "tt_time",
        "distance_meters_t": "tt_dist",
    })
    df = df[["mode", "origin_lat", "origin_lng", "dest_lat", "dest_lng",
             "g_time", "g_dist", "tt_time", "tt_dist"]].copy()
    df = df.sort_values(["mode", "origin_lat"]).reset_index(drop=True)

    if df.empty:
        return df

    df["haversine_km"] = df.apply(
        lambda r: haversine_km(r["origin_lat"], r["origin_lng"],
                               r["dest_lat"], r["dest_lng"]),
        axis=1,
    )
    df["abs_diff_s"] = (df["tt_time"] - df["g_time"]).abs()
    df["abs_diff_min"] = df["abs_diff_s"] / 60.0
    df["signed_diff_min"] = (df["tt_time"] - df["g_time"]) / 60.0
    df["pct_error"] = np.where(
        df["g_time"] > 0,
        (df["tt_time"] - df["g_time"]) / df["g_time"] * 100,
        np.nan,
    )
    df["g_time_min"] = df["g_time"] / 60.0
    df["tt_time_min"] = df["tt_time"] / 60.0

    df["dist_band"] = pd.cut(
        df["haversine_km"],
        bins=[0, 5, 10, 20, 35, 50, 200],
        labels=["0-5km", "5-10km", "10-20km", "20-35km", "35-50km", "50km+"],
    )
    df["time_band"] = pd.cut(
        df["g_time_min"],
        bins=[0, 15, 30, 60, 999],
        labels=["0-15min", "15-30min", "30-60min", "60min+"],
    )

    coord_sets = _load_market_coord_sets()
    df["market"] = df.apply(lambda r: _assign_market(r, coord_sets), axis=1)
    return df


def load_coverage_data() -> pd.DataFrame:
    raw = _get_raw_data()
    df = raw[["mode", "provider", "status",
              "origin_lat", "origin_lng", "dest_lat", "dest_lng"]].copy()

    coord_sets = _load_market_coord_sets()
    df["market"] = df.apply(lambda r: _assign_market(r, coord_sets), axis=1)

    # Assign metro area for origin (used in per-metro coverage breakdown)
    df["metro"] = df.apply(
        lambda r: (m.name if (m := get_metro_area(r["origin_lat"], r["origin_lng"])) else "Other"),
        axis=1,
    )
    return df


def load_valhalla_paired_results() -> pd.DataFrame:
    """Load paired results: Valhalla vs Google (both ok)."""
    raw = _get_raw_data()
    g = raw[(raw["provider"] == "google") & (raw["status"] == "ok")].copy()
    v = raw[(raw["provider"] == "valhalla") & (raw["status"] == "ok")].copy()

    for col in ["origin_lat", "origin_lng", "dest_lat", "dest_lng"]:
        g[col] = g[col].round(6)
        v[col] = v[col].round(6)

    join_cols = ["mode", "origin_lat", "origin_lng", "dest_lat", "dest_lng"]
    df = g.merge(v, on=join_cols, suffixes=("_g", "_v"))
    df = df.rename(columns={
        "travel_time_seconds_g": "g_time",
        "distance_meters_g": "g_dist",
        "travel_time_seconds_v": "vh_time",
        "distance_meters_v": "vh_dist",
    })
    df = df[["mode", "origin_lat", "origin_lng", "dest_lat", "dest_lng",
             "g_time", "g_dist", "vh_time", "vh_dist"]].copy()
    df = df.sort_values(["mode", "origin_lat"]).reset_index(drop=True)

    if df.empty:
        return df

    df["haversine_km"] = df.apply(
        lambda r: haversine_km(r["origin_lat"], r["origin_lng"],
                               r["dest_lat"], r["dest_lng"]),
        axis=1,
    )
    df["abs_diff_s"] = (df["vh_time"] - df["g_time"]).abs()
    df["abs_diff_min"] = df["abs_diff_s"] / 60.0
    df["signed_diff_min"] = (df["vh_time"] - df["g_time"]) / 60.0
    df["pct_error"] = np.where(
        df["g_time"] > 0,
        (df["vh_time"] - df["g_time"]) / df["g_time"] * 100,
        np.nan,
    )
    df["g_time_min"] = df["g_time"] / 60.0
    df["vh_time_min"] = df["vh_time"] / 60.0

    df["dist_band"] = pd.cut(
        df["haversine_km"],
        bins=[0, 5, 10, 20, 35, 50, 200],
        labels=["0-5km", "5-10km", "10-20km", "20-35km", "35-50km", "50km+"],
    )
    df["time_band"] = pd.cut(
        df["g_time_min"],
        bins=[0, 15, 30, 60, 999],
        labels=["0-15min", "15-30min", "30-60min", "60min+"],
    )

    coord_sets = _load_market_coord_sets()
    df["market"] = df.apply(lambda r: _assign_market(r, coord_sets), axis=1)
    return df


def load_city_expansion_summary() -> pd.DataFrame:
    """Generate high-search city expansion sample summary."""
    rng = np.random.default_rng(2026)
    cities = [
        ("CA", "Hamilton"), ("CA", "Ottawa"), ("CA", "Calgary"), ("CA", "Edmonton"),
        ("GB", "Southampton"), ("GB", "Leeds"), ("GB", "Bristol"), ("GB", "Glasgow"),
        ("FR", "Lyon"), ("FR", "Lille"), ("FR", "Toulouse"), ("FR", "Nantes"),
    ]
    rows = []
    for market, metro in cities:
        n = 100
        tt_ok = int(rng.integers(62, 96))
        google_ok = int(rng.integers(76, 99))
        tt_ok_among_google = min(tt_ok, int(google_ok * rng.uniform(0.70, 0.97)))
        rows.append({
            "market": market,
            "metro": metro,
            "traveltime_n": n,
            "traveltime_ok": tt_ok,
            "traveltime_no_route": max(n - tt_ok - int(rng.integers(0, 4)), 0),
            "traveltime_error": n - tt_ok - max(n - tt_ok - int(rng.integers(0, 4)), 0),
            "traveltime_coverage_pct": round(tt_ok / n * 100, 1),
            "google_ok": google_ok,
            "google_no_route": n - google_ok,
            "google_coverage_pct": round(google_ok / n * 100, 1),
            "google_ok_pairs": google_ok,
            "tt_ok_among_google_ok": tt_ok_among_google,
            "tt_coverage_among_google_ok_pct": round(tt_ok_among_google / google_ok * 100, 1) if google_ok else 0,
        })
    return pd.DataFrame(rows)


PAIRED_DF = load_paired_results()
VALHALLA_DF = load_valhalla_paired_results()
COVERAGE_DF = load_coverage_data()
CITY_EXPANSION_DF = load_city_expansion_summary()


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _filter(df: pd.DataFrame, markets: list[str], mode: str) -> pd.DataFrame:
    out = df[df["market"].isin(markets)] if markets else df
    if mode and mode != "both":
        out = out[out["mode"] == mode]
    return out


def _pct(series: pd.Series, threshold: float) -> float:
    if len(series) == 0:
        return 0.0
    return 100.0 * (series <= threshold).sum() / len(series)


def _stat_card(label: str, value: str, accent: str = "", tooltip: str = "") -> html.Div:
    cls = f"value accent-{accent}" if accent else "value"
    return html.Div(
        className="stat-card",
        title=tooltip if tooltip else None,
        children=[
            html.Span(label, className="label"),
            html.Span(value, className=cls),
        ],
    )


def _chart_desc(text: str) -> html.Div:
    lines = text.split("\n")
    children = []
    for i, line in enumerate(lines):
        if i > 0:
            children.append(html.Br())
        children.append(line)
    return html.P(
        children,
        style={
            "color": C["text_muted"],
            "fontSize": "0.8rem",
            "lineHeight": "1.6",
            "margin": "0 0 8px 0",
        },
    )


def _table_styles() -> dict:
    return dict(
        style_table={
            "borderRadius": "8px",
            "overflow": "hidden",
            "border": f"1px solid {C['border']}",
        },
        style_cell={
            "textAlign": "center",
            "padding": "12px 14px",
            "whiteSpace": "normal",
            "height": "auto",
            "backgroundColor": C["bg_secondary"],
            "color": C["text_primary"],
            "border": "none",
            "borderBottom": f"1px solid {C['border']}",
            "fontFamily": "Inter, -apple-system, sans-serif",
            "fontSize": "0.875rem",
        },
        style_header={
            "backgroundColor": C["bg_input"],
            "color": C["text_secondary"],
            "fontWeight": "600",
            "fontSize": "0.75rem",
            "textTransform": "uppercase",
            "letterSpacing": "0.05em",
            "borderBottom": f"1px solid {C['border']}",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": C["bg_input"]},
            {"if": {"state": "active"}, "backgroundColor": "#e8edf2", "border": "none"},
        ],
    )


def _city_expansion_section() -> html.Div:
    """Return the static top-20 city expansion dashboard section."""
    if CITY_EXPANSION_DF.empty:
        return html.Div(
            className="section-card",
            children=[
                html.H3("City Expansion — TravelTime vs Google", className="section-title"),
                html.P(
                    "City-expansion comparison file not found. Run the top-20 city "
                    "manifest through both providers to populate this section.",
                    style={"color": C["text_muted"], "fontSize": "0.85rem"},
                ),
            ],
        )

    df = CITY_EXPANSION_DF.copy()
    df["City"] = df["metro"] + ", " + df["market"]
    df["TT Missing Among Google OK"] = (
        df["google_ok_pairs"] - df["tt_ok_among_google_ok"]
    )
    df = df.sort_values(
        ["tt_coverage_among_google_ok_pct", "traveltime_coverage_pct", "google_ok_pairs"],
        ascending=[True, True, False],
    )

    total_pairs = int(df["traveltime_n"].sum())
    tt_ok = int(df["traveltime_ok"].sum())
    google_ok = int(df["google_ok"].sum())
    google_ok_pairs = int(df["google_ok_pairs"].sum())
    tt_ok_among_google_ok = int(df["tt_ok_among_google_ok"].sum())
    tt_coverage = 100 * tt_ok / total_pairs if total_pairs else 0
    google_coverage = 100 * google_ok / total_pairs if total_pairs else 0
    tt_vs_google = (
        100 * tt_ok_among_google_ok / google_ok_pairs if google_ok_pairs else 0
    )
    city_list_md = "\n".join(
        f"- **{market}:** {', '.join(group['metro'].tolist())}"
        for market, group in df.sort_values(["market", "metro"]).groupby("market")
    )

    display_df = df[[
        "market",
        "metro",
        "traveltime_n",
        "traveltime_ok",
        "traveltime_no_route",
        "traveltime_error",
        "traveltime_coverage_pct",
        "google_ok",
        "google_no_route",
        "google_coverage_pct",
        "google_ok_pairs",
        "tt_ok_among_google_ok",
        "TT Missing Among Google OK",
        "tt_coverage_among_google_ok_pct",
    ]].rename(columns={
        "market": "Market",
        "metro": "City",
        "traveltime_n": "Pairs",
        "traveltime_ok": "TT OK",
        "traveltime_no_route": "TT No Route",
        "traveltime_error": "TT Error",
        "traveltime_coverage_pct": "TT Cov %",
        "google_ok": "Google OK",
        "google_no_route": "Google No Route",
        "google_coverage_pct": "Google Cov %",
        "google_ok_pairs": "Google-OK Pairs",
        "tt_ok_among_google_ok": "TT OK Among Google OK",
        "tt_coverage_among_google_ok_pct": "TT Cov Among Google OK %",
    })

    coverage_chart_df = df.melt(
        id_vars=["City"],
        value_vars=["traveltime_coverage_pct", "google_coverage_pct"],
        var_name="Provider",
        value_name="Coverage %",
    )
    coverage_chart_df["Provider"] = coverage_chart_df["Provider"].map({
        "traveltime_coverage_pct": "TravelTime",
        "google_coverage_pct": "Google",
    })
    city_order = df["City"].tolist()
    fig_coverage = px.bar(
        coverage_chart_df,
        x="City",
        y="Coverage %",
        color="Provider",
        barmode="group",
        color_discrete_map={"Google": GGPLOT_2[0], "TravelTime": GGPLOT_2[1]},
        category_orders={"City": city_order},
    )
    fig_coverage.update_layout(
        yaxis_range=[0, 105],
        xaxis_tickangle=-35,
        template=PLOTLY_TEMPLATE,
        height=520,
    )

    fig_gap = px.bar(
        df,
        x="City",
        y="TT Missing Among Google OK",
        color="market",
        color_discrete_map=CITY_EXPANSION_MARKET_COLORS,
        category_orders={"City": city_order},
        hover_data=["google_ok_pairs", "tt_coverage_among_google_ok_pct"],
    )
    fig_gap.update_layout(
        xaxis_tickangle=-35,
        yaxis_title="OD pairs",
        template=PLOTLY_TEMPLATE,
        height=520,
    )

    return html.Div(className="section-card", children=[
        html.H3("City Expansion — TravelTime vs Google", className="section-title"),
        html.P(
            "High-search-volume cities from TravelTime's published transit coverage list "
            "that were not already explicit metros in the original OD suite. We expanded "
            "the test by 20 cities, with 100 generated OD pairs per city, using the same "
            "origin-destination sampling shape as the main analysis.",
            style={"color": C["text_muted"], "fontSize": "0.85rem",
                   "lineHeight": "1.6", "margin": "0 0 16px 0"},
        ),
        html.Div(
            className="city-list-card",
            children=[
                html.H4("Cities tested in this expansion"),
                dcc.Markdown(city_list_md),
            ],
        ),
        html.Div(className="stat-cards-row", children=[
            _stat_card("City Expansion Pairs", f"{total_pairs:,}"),
            _stat_card("TravelTime Coverage", f"{tt_coverage:.1f}%", "teal"),
            _stat_card("Google Coverage", f"{google_coverage:.1f}%", "blue"),
            _stat_card("TT Coverage Among Google OK", f"{tt_vs_google:.1f}%", "orange"),
        ]),
        html.Div(className="charts-row", children=[
            html.Div(className="chart-card", children=[
                html.H4("Top-20 City Expansion: Provider Coverage", className="chart-title"),
                _chart_desc(
                    "Provider coverage for the 20 added high-search cities.\n"
                    "Hamilton and Southampton are the clearest TravelTime gaps."
                ),
                dcc.Graph(figure=fig_coverage),
            ]),
            html.Div(className="chart-card", children=[
                html.H4("TravelTime Missing Routes Where Google Returned Transit", className="chart-title"),
                _chart_desc(
                    "Count of Google-ok OD pairs where TravelTime did not return a route.\n"
                    "This is the cleanest route-result gap denominator."
                ),
                dcc.Graph(figure=fig_gap),
            ]),
        ]),
        html.Div(
            className="table-container",
            style={"border": "none", "padding": "0"},
            children=[
                html.H4("City Expansion Detail"),
                dash_table.DataTable(
                    data=display_df.to_dict("records"),
                    columns=[{"name": col, "id": col} for col in display_df.columns],
                    sort_action="native",
                    filter_action="native",
                    page_size=20,
                    **_table_styles(),
                ),
            ],
        ),
    ])


# ═══════════════════════════════════════════════════════════════════════════
# App layout
# ═══════════════════════════════════════════════════════════════════════════

app = Dash(__name__)
app.title = "Commute Vendor Analysis — TravelTime & Valhalla vs Google Maps"
server = app.server

METHODOLOGY_MD = """\
**Source data:** This public version uses generated origin–destination (OD) pairs \
that mirror the shape of a production-style commute analysis. Approximately \
1,500 sample OD pairs are represented across **11 international markets**: \
US, DE, GB, CA, FR, NL, IT, IE, AU, BE, CH.

**Test execution:** Each OD pair was evaluated across **Google Maps**, \
**TravelTime**, and **Valhalla** in two modes — *driving* and *transit*. \
Departure time was fixed to **Tuesday 8:30 AM local time** for each market.

**Transit eligibility:** Transit queries were sent for OD pairs where both \
endpoints roughly fell in/near proximity (20–60 km depending on city size) \
to a sample of metro areas across each country with known transit service.

**Evaluation:** TravelTime travel-time estimates are compared against Google \
Maps as a reference. Key metrics include median/mean absolute difference, \
percentage within ±5/10/15 minutes, and directional bias.

**Valhalla:** Valhalla is also included as a third comparison provider. \
Results are compared against both Google and TravelTime at the bottom of this page.

**Data:** Generated sample data for public sharing.\
"""

app.layout = html.Div(
    className="dashboard-container",
    children=[
        # ── Header ──
        html.Div(
            className="dashboard-header",
            children=[
                html.H1("Commute Vendor Analysis"),
                html.P("TravelTime & Valhalla vs Google Maps"),
                html.Div(
                    "Valhalla comparison (US/CA transit) is at the bottom of this page.",
                    style={"fontSize": "0.8rem", "color": C["text_muted"],
                           "marginTop": "8px", "fontStyle": "italic",
                           "textAlign": "center", "width": "100%"},
                ),
            ],
        ),

        # ── Methodology + Executive Summary (side by side) ──
        html.Div(className="charts-row", children=[
            html.Div(
                className="methodology-card",
                children=[
                    html.H3("Methodology"),
                    dcc.Markdown(METHODOLOGY_MD),
                ],
            ),
            html.Div(
                className="methodology-card",
                children=[
                    html.H3("Key Findings"),
                    html.Div(id="executive-summary"),
                ],
            ),
        ]),

        # ── Filters ──
        html.Div(
            className="controls-bar",
            children=[
                html.Div(
                    className="control-group",
                    children=[
                        html.Label("Markets"),
                        dcc.Dropdown(
                            id="market-filter",
                            options=[{"label": m, "value": m} for m in ALL_MARKETS],
                            value=ALL_MARKETS,
                            multi=True,
                            placeholder="Select markets…",
                            style={"minWidth": "440px"},
                        ),
                    ],
                ),
                html.Div(
                    className="control-group",
                    children=[
                        html.Label("Mode"),
                        dcc.Dropdown(
                            id="mode-filter",
                            options=[
                                {"label": "Both", "value": "both"},
                                {"label": "Driving", "value": "driving"},
                                {"label": "Transit", "value": "transit"},
                            ],
                            value="both",
                            clearable=False,
                            style={"width": "160px"},
                        ),
                    ],
                ),
            ],
        ),

        # ── Summary stat cards ──
        html.Div(id="summary-cards"),

        # ── Section: Accuracy Overview ──
        html.Div(className="section-card", children=[
            html.H3("Accuracy Overview — TravelTime vs Google", className="section-title"),
            html.Div(
                className="table-container",
                style={"border": "none", "padding": "0", "marginBottom": "24px"},
                children=[
                    html.H4("Per-Market Accuracy"),
                    html.Div(id="accuracy-table"),
                ],
            ),
            html.Div(className="charts-row", children=[
                html.Div(className="chart-card", children=[
                    html.H4("Median Absolute Difference by Market", className="chart-title"),
                    _chart_desc(DESC["median_diff"]),
                    dcc.Graph(id="chart-median-diff"),
                ]),
                html.Div(className="chart-card", children=[
                    html.H4("Within ±10 min Accuracy by Market", className="chart-title"),
                    _chart_desc(DESC["within_10"]),
                    dcc.Graph(id="chart-within-10"),
                ]),
            ]),
        ]),

        # ── Section: Coverage & Distribution ──
        html.Div(className="section-card", children=[
            html.H3("Coverage & Distribution — TravelTime vs Google", className="section-title"),
            html.Div(className="charts-row", children=[
                html.Div(className="chart-card", children=[
                    html.H4("Transit Coverage by Market", className="chart-title"),
                    _chart_desc(DESC["transit_cov"]),
                    dcc.Graph(id="chart-transit-coverage"),
                ]),
                html.Div(className="chart-card", children=[
                    html.H4("Driving Coverage by Market", className="chart-title"),
                    _chart_desc(DESC["driving_cov"]),
                    dcc.Graph(id="chart-driving-coverage"),
                ]),
            ]),
            html.Div(className="charts-row", children=[
                html.Div(className="chart-card chart-full", children=[
                    html.H4("Transit OD Pair Distance Distribution", className="chart-title"),
                    _chart_desc(DESC["transit_dist"]),
                    dcc.Graph(id="chart-transit-dist"),
                ]),
            ]),
            html.Div(
                className="table-container",
                style={"border": "none", "padding": "0", "marginBottom": "16px", "marginTop": "8px"},
                children=[
                    html.H4("Transit Coverage by Market"),
                    html.P(
                        "Status breakdown for both providers across all transit OD pairs.\n"
                        "Google coverage serves as the benchmark — TT gaps are most meaningful "
                        "where Google returned a result.",
                        style={"color": C["text_muted"], "fontSize": "0.8rem",
                               "lineHeight": "1.6", "margin": "0 0 12px 0"},
                    ),
                    html.Div(id="coverage-table"),
                ],
            ),
            # OD pairs map
            html.Div(
                style={"marginTop": "24px", "marginBottom": "24px"},
                children=[
                    html.H4("OD Pairs Map", className="chart-title"),
                    _chart_desc(DESC["od_map"]),
                    html.Div(
                        style={"display": "flex", "alignItems": "center",
                               "gap": "24px", "marginBottom": "12px"},
                        children=[
                            html.Div(
                                style={"display": "flex", "alignItems": "center",
                                       "gap": "8px"},
                                children=[
                                    html.Label("Mode:", style={
                                        "color": C["text_secondary"], "fontSize": "0.75rem",
                                        "fontWeight": "500", "textTransform": "uppercase",
                                        "letterSpacing": "0.05em",
                                    }),
                                    dcc.RadioItems(
                                        id="map-mode-toggle",
                                        options=[
                                            {"label": " Transit", "value": "transit"},
                                            {"label": " Driving", "value": "driving"},
                                        ],
                                        value="transit",
                                        inline=True,
                                        style={"fontSize": "0.85rem"},
                                        inputStyle={"marginRight": "4px"},
                                        labelStyle={"marginRight": "16px",
                                                    "color": C["text_primary"]},
                                    ),
                                ],
                            ),
                            html.Div(
                                style={"display": "flex", "alignItems": "center",
                                       "gap": "8px"},
                                children=[
                                    html.Label("Color by:", style={
                                        "color": C["text_secondary"], "fontSize": "0.75rem",
                                        "fontWeight": "500", "textTransform": "uppercase",
                                        "letterSpacing": "0.05em",
                                    }),
                                    dcc.RadioItems(
                                        id="map-color-toggle",
                                        options=[
                                            {"label": " TT Status", "value": "status"},
                                            {"label": " Market", "value": "market"},
                                        ],
                                        value="status",
                                        inline=True,
                                        style={"fontSize": "0.85rem"},
                                        inputStyle={"marginRight": "4px"},
                                        labelStyle={"marginRight": "16px",
                                                    "color": C["text_primary"]},
                                    ),
                                ],
                            ),
                        ],
                    ),
                    dcc.Graph(id="chart-od-map"),
                ],
            ),
            html.Div(
                className="table-container",
                style={"border": "none", "padding": "0"},
                children=[
                    html.H4("Transit Coverage by Metro Area"),
                    html.P(
                        "Per-city breakdown of TravelTime transit coverage. "
                        "Metro area is determined by the origin endpoint of each OD pair.",
                        style={"color": C["text_muted"], "fontSize": "0.8rem",
                               "margin": "0 0 12px 0"},
                    ),
                    html.Div(id="metro-coverage-table"),
                ],
            ),
        ]),

        # ── Section: City Expansion ──
        _city_expansion_section(),

        # ── Section: Error Analysis ──
        html.Div(className="section-card", children=[
            html.H3("Error Analysis — TravelTime vs Google", className="section-title"),
            html.Div(className="charts-row", children=[
                html.Div(className="chart-card", children=[
                    html.H4("Google vs TravelTime Travel Time", className="chart-title"),
                    _chart_desc(DESC["scatter"]),
                    dcc.Graph(id="chart-scatter"),
                ]),
                html.Div(className="chart-card", children=[
                    html.H4("Distribution of Signed Difference (TT − Google)", className="chart-title"),
                    _chart_desc(DESC["hist"]),
                    dcc.Graph(id="chart-hist-diff"),
                ]),
            ]),
            html.Div(className="charts-row", children=[
                html.Div(className="chart-card chart-full", children=[
                    html.H4("Mean Signed Bias by Market (TT − Google)", className="chart-title"),
                    _chart_desc(DESC["bias"]),
                    dcc.Graph(id="chart-bias"),
                ]),
            ]),
        ]),

        # ── Section: Accuracy by Distance & Time ──
        html.Div(className="section-card", children=[
            html.H3("Accuracy by Distance & Time — TravelTime vs Google", className="section-title"),
            html.Div(className="charts-row", children=[
                html.Div(className="chart-card", children=[
                    html.H4("Accuracy by Distance Band (Within ±10 min)", className="chart-title"),
                    _chart_desc(DESC["dist_band"]),
                    dcc.Graph(id="chart-dist-band"),
                ]),
                html.Div(className="chart-card", children=[
                    html.H4("Accuracy by Commute Time Band (Within ±10 min)", className="chart-title"),
                    _chart_desc(DESC["time_band"]),
                    dcc.Graph(id="chart-time-band"),
                ]),
            ]),
            html.Div(
                className="table-container",
                style={"border": "none", "padding": "0", "marginBottom": "16px", "marginTop": "8px"},
                children=[
                    html.H4("Detail: By Distance Band"),
                    html.Div(id="dist-band-table"),
                ],
            ),
            html.Div(
                className="table-container",
                style={"border": "none", "padding": "0"},
                children=[
                    html.H4("Detail: By Commute Time Band"),
                    html.Div(id="time-band-table"),
                ],
            ),
        ]),

        # ── Section: Valhalla Comparison ──
        html.Div(className="section-card", children=[
            html.H3("Valhalla Comparison (US/CA Transit)", className="section-title"),
            html.P(
                "Valhalla is compared against Google Maps and TravelTime on "
                "the same OD pairs.",
                style={"color": C["text_muted"], "fontSize": "0.85rem",
                       "margin": "0 0 16px 0"},
            ),
            html.Div(style={"marginBottom": "20px"}, children=[
                html.Table(
                    style={"borderCollapse": "collapse", "fontSize": "0.875rem",
                           "marginBottom": "16px", "width": "auto"},
                    children=[
                        html.Thead(html.Tr([
                            html.Th(h, style={
                                "padding": "8px 16px", "textAlign": "left",
                                "borderBottom": f"2px solid {C['border']}",
                                "color": C["text_secondary"], "fontWeight": "600",
                                "fontSize": "0.75rem", "textTransform": "uppercase",
                                "letterSpacing": "0.05em",
                            }) for h in ["Metric", "TravelTime", "Valhalla"]
                        ])),
                        html.Tbody([
                            html.Tr([
                                html.Td(cells[0], style={
                                    "padding": "6px 16px",
                                    "borderBottom": f"1px solid {C['border']}",
                                    "color": C["text_secondary"],
                                }),
                            ] + [
                                html.Td(
                                    html.Span(c, style={"fontWeight": "600"})
                                    if bold else c,
                                    style={
                                        "padding": "6px 16px",
                                        "borderBottom": f"1px solid {C['border']}",
                                        "color": C["text_primary"],
                                        "fontFamily": "monospace",
                                    },
                                ) for c, bold in zip(cells[1:], bolds)
                            ]) for cells, bolds in [
                                (["Transit coverage (vs Google)", "84.7%", "32.4%"], [False, False]),
                                (["Within ±10 min", "65.4%", "36.5%"], [False, False]),
                                (["Median abs diff", "5.9 min", "15.6 min"], [False, False]),
                                (["Bias (mean signed diff)", "−3.4 min", "+30.7 min"], [False, True]),
                                (["Correlation w/ Google", "r=0.901", "r=0.299"], [False, False]),
                                (["Head-to-head winner", "71%", "29%"], [True, False]),
                            ]
                        ]),
                    ],
                ),
                html.P(html.Strong("Key issues:"), style={
                    "color": C["text_secondary"], "fontSize": "0.875rem",
                    "margin": "0 0 4px 0",
                }),
                html.Ul(style={
                    "color": C["text_secondary"], "fontSize": "0.875rem",
                    "lineHeight": "1.7", "paddingLeft": "20px", "margin": "0",
                }, children=[
                    html.Li([html.Strong("Canada transit feeds need major work"),
                             " — 1.6% coverage (12/758 ok)"]),
                    html.Li([html.Strong("Overestimation bias"),
                             " — Valhalla averages +31 min over Google"]),
                    html.Li([html.Strong("Significant outliers"),
                             " — DC/Baltimore routes off by 200–400 min, Portland +404 min"]),
                    html.Li([html.Strong("Coverage varies significantly by metro"),
                             " — Portland 94%, Denver 80%, but Columbus 0%, Phoenix 0%"]),
                    html.Li([html.Strong("Only NYC shows competitive accuracy currently"),
                             " — 74.5% within ±10 min (vs TT's ~65%)"]),
                ]),
            ]),
            html.Div(id="vh-summary-cards"),
            html.Div(
                className="table-container",
                style={"border": "none", "padding": "0", "marginBottom": "24px"},
                children=[
                    html.H4("Provider Comparison — US/CA Transit"),
                    html.Div(id="vh-comparison-table"),
                ],
            ),
            html.Div(className="charts-row", children=[
                html.Div(className="chart-card", children=[
                    html.H4("Valhalla vs Google — Transit Travel Time", className="chart-title"),
                    _chart_desc(
                        "Valhalla vs Google: each dot is one OD pair.\n"
                        "Points on the dashed y=x line mean perfect agreement."
                    ),
                    dcc.Graph(id="chart-vh-scatter"),
                ]),
                html.Div(className="chart-card", children=[
                    html.H4("Valhalla − Google Signed Difference", className="chart-title"),
                    _chart_desc(
                        "Distribution of signed differences (Valhalla − Google).\n"
                        "Positive = Valhalla overestimates commute time."
                    ),
                    dcc.Graph(id="chart-vh-hist"),
                ]),
            ]),
            html.Div(className="charts-row", children=[
                html.Div(className="chart-card", children=[
                    html.H4("Within ±10 min Accuracy by Metro (Transit)", className="chart-title"),
                    _chart_desc(
                        "Within ±10 min accuracy by metro area.\n"
                        "Compares TravelTime and Valhalla on the same OD pairs."
                    ),
                    dcc.Graph(id="chart-vh-metro-accuracy"),
                ]),
                html.Div(className="chart-card", children=[
                    html.H4("Transit Coverage by Metro Area", className="chart-title"),
                    _chart_desc(
                        "Transit coverage (% ok) by metro area for each provider.\n"
                        "Shows how many OD pairs each provider successfully routed."
                    ),
                    dcc.Graph(id="chart-vh-metro-coverage"),
                ]),
            ]),
        ]),
    ],
)


# ═══════════════════════════════════════════════════════════════════════════
# Callbacks
# ═══════════════════════════════════════════════════════════════════════════

@callback(
    Output("executive-summary", "children"),
    Output("summary-cards", "children"),
    Output("accuracy-table", "children"),
    Output("chart-median-diff", "figure"),
    Output("chart-within-10", "figure"),
    Output("chart-transit-coverage", "figure"),
    Output("chart-driving-coverage", "figure"),
    Output("chart-transit-dist", "figure"),
    Output("chart-scatter", "figure"),
    Output("chart-hist-diff", "figure"),
    Output("chart-bias", "figure"),
    Output("chart-dist-band", "figure"),
    Output("chart-time-band", "figure"),
    Output("coverage-table", "children"),
    Output("dist-band-table", "children"),
    Output("time-band-table", "children"),
    Output("metro-coverage-table", "children"),
    Input("market-filter", "value"),
    Input("mode-filter", "value"),
)
def update_dashboard(markets: list[str], mode: str):
    if not markets:
        markets = ALL_MARKETS

    df = _filter(PAIRED_DF, markets, mode)
    cov_df = COVERAGE_DF[COVERAGE_DF["market"].isin(markets)]

    empty_fig = go.Figure().update_layout(
        template=PLOTLY_TEMPLATE,
        annotations=[dict(text="No data", showarrow=False,
                          font=dict(size=16, color=C["text_muted"]))],
    )

    no_data_div = html.Div(
        "No data for current filters.",
        style={"padding": "20px", "color": C["text_muted"]},
    )

    # ── Executive summary ───────────────────────────────────────────────
    _es_style = {"color": C["text_secondary"], "fontSize": "0.875rem",
                 "lineHeight": "1.7", "margin": "0 0 8px 0"}
    _es_val = {"fontWeight": "600", "color": C["text_primary"]}
    if len(df) > 0:
        drv = df[df["mode"] == "driving"]
        trn = df[df["mode"] == "transit"]
        drv_w10 = _pct(drv["abs_diff_min"], 10) if len(drv) > 0 else 0
        trn_w10 = _pct(trn["abs_diff_min"], 10) if len(trn) > 0 else 0
        drv_med = drv["abs_diff_min"].median() if len(drv) > 0 else 0
        trn_med = trn["abs_diff_min"].median() if len(trn) > 0 else 0
        drv_p90 = drv["abs_diff_min"].quantile(0.9) if len(drv) > 0 else 0
        trn_p90 = trn["abs_diff_min"].quantile(0.9) if len(trn) > 0 else 0
        drv_bias = drv["signed_diff_min"].mean() if len(drv) > 0 else 0
        trn_bias = trn["signed_diff_min"].mean() if len(trn) > 0 else 0
        bullets = []
        if len(drv) > 0:
            bullets.append(html.Li([
                "Driving: ",
                html.Span(f"{drv_w10:.0f}%", style=_es_val),
                f" within ±10 min · median diff {drv_med:.1f} min · "
                f"P90 {drv_p90:.1f} min · bias {drv_bias:+.1f} min",
            ]))
        if len(trn) > 0:
            bullets.append(html.Li([
                "Transit: ",
                html.Span(f"{trn_w10:.0f}%", style=_es_val),
                f" within ±10 min · median diff {trn_med:.1f} min · "
                f"P90 {trn_p90:.1f} min · bias {trn_bias:+.1f} min",
            ]))
        bullets.append(html.Li([
            html.Span("P90", style={"fontStyle": "italic"}),
            " — only 10% of responses had a time difference greater than this.",
        ], style={"color": C["text_muted"], "fontSize": "0.8rem", "marginTop": "4px"}))
        n_markets = len(df["market"].unique())
        exec_summary = html.Div([
            html.P([
                f"Across {n_markets} market{'s' if n_markets > 1 else ''} "
                f"({len(df):,} paired OD results):"
            ], style=_es_style),
            html.Ul(bullets, style={**_es_style, "paddingLeft": "20px"}),
            html.P([
                "Bias direction: ",
                html.Span(
                    "TT underestimates" if df["signed_diff_min"].mean() < -0.5
                    else ("TT overestimates" if df["signed_diff_min"].mean() > 0.5
                          else "No systematic bias"),
                    style=_es_val,
                ),
                f" overall ({df['signed_diff_min'].mean():+.1f} min mean signed diff).",
            ], style=_es_style),
            html.P([
                html.Span("Transit coverage is strong: ", style=_es_val),
                "Where Google returned a transit route, TravelTime also returned "
                "a result ~90% of the time. Most of TT's missing coverage overlaps "
                "with routes Google can't serve either.",
            ], style=_es_style),
            html.Hr(style={"border": "none", "borderTop": f"1px solid {C['border']}",
                            "margin": "12px 0"}),
            html.P([
                html.Span("Known issue — transit wait-time inflation: ", style=_es_val),
                "TravelTime sometimes selects routes with extremely long waits "
                "for infrequent services (suburban buses, shuttles), bundling "
                "multi-hour waits into the travel time. Google avoids these by "
                "choosing better-timed alternatives.",
            ], style=_es_style),
            html.Ul([
                html.Li("Columbus, OH: TT 484 min vs Google 148 min — "
                        "included a 5 hr 54 min wait for an infrequent Bus 43."),
                html.Li("Boston: TT 280 min vs Google 134 min — "
                        "included an 82 min wait for Emerson Hospital Shuttle."),
            ], style={**_es_style, "paddingLeft": "20px", "fontSize": "0.8rem",
                      "color": C["text_muted"]}),
            html.P(
                "This routing quality issue primarily affects suburban/low-density "
                "areas and drives the long tail of transit errors (12% of routes "
                "off by >20 min).",
                style={**_es_style, "fontSize": "0.8rem", "color": C["text_muted"]},
            ),
        ])
    else:
        exec_summary = no_data_div

    # ── Summary cards ───────────────────────────────────────────────────
    if len(df) > 0:
        cards = html.Div(
            className="stat-cards-row",
            children=[
                _stat_card("Total Paired Results", f"{len(df):,}"),
                _stat_card("Mean Abs Diff", f"{df['abs_diff_min'].mean():.1f} min", "teal"),
                _stat_card("Median Abs Diff", f"{df['abs_diff_min'].median():.1f} min", "teal"),
                _stat_card("Within ±10 min", f"{_pct(df['abs_diff_min'], 10):.1f}%", "blue"),
                _stat_card("Mean Signed Diff", f"{df['signed_diff_min'].mean():+.1f} min", "orange",
                           tooltip="Negative = TT estimates shorter commutes than Google. "
                                   "Positive = TT estimates longer. Zero = no systematic bias."),
            ],
        )
    else:
        cards = html.Div(className="stat-cards-row", children=[no_data_div])

    # ── Per-market accuracy table ───────────────────────────────────────
    rows = []
    modes_to_show = ["driving", "transit"] if mode == "both" else [mode]
    for m in markets:
        for md in modes_to_show:
            mdf = df[(df["market"] == m) & (df["mode"] == md)]
            n = len(mdf)
            if n == 0:
                continue
            mean_signed = mdf["signed_diff_min"].mean()
            rows.append({
                "Market": m,
                "Mode": md.title(),
                "n": n,
                "Median Diff (min)": round(mdf["abs_diff_min"].median(), 1),
                "Mean Diff (min)": round(mdf["abs_diff_min"].mean(), 1),
                "P90 (min)": round(mdf["abs_diff_min"].quantile(0.9), 1),
                "P95 (min)": round(mdf["abs_diff_min"].quantile(0.95), 1),
                "Within ±5min %": round(_pct(mdf["abs_diff_min"], 5), 1),
                "Within ±10min %": round(_pct(mdf["abs_diff_min"], 10), 1),
                "Within ±15min %": round(_pct(mdf["abs_diff_min"], 15), 1),
                "Mean % Error": round(mdf["pct_error"].mean(), 1),
                "Bias": ("TT over" if mean_signed > 0.5
                         else ("TT under" if mean_signed < -0.5 else "Neutral")),
            })

    acc_table_df = pd.DataFrame(rows) if rows else pd.DataFrame()
    acc_table = dash_table.DataTable(
        data=acc_table_df.to_dict("records") if not acc_table_df.empty else [],
        columns=[{"name": c, "id": c} for c in acc_table_df.columns] if not acc_table_df.empty else [],
        sort_action="native",
        page_size=30,
        **_table_styles(),
    )

    # ── Chart: Median absolute difference by market ─────────────────────
    if not acc_table_df.empty:
        fig_median = px.bar(
            acc_table_df, x="Market", y="Median Diff (min)", color="Mode",
            barmode="group", color_discrete_map=MODE_COLORS_TITLE,
            category_orders={"Market": ALL_MARKETS},
        )
        fig_median.update_layout(yaxis_title="Median |TT − Google| (min)",
                                 template=PLOTLY_TEMPLATE)
    else:
        fig_median = empty_fig

    # ── Chart: Within ±10 min accuracy by market ────────────────────────
    if not acc_table_df.empty:
        fig_w10 = px.bar(
            acc_table_df, x="Market", y="Within ±10min %", color="Mode",
            barmode="group", color_discrete_map=MODE_COLORS_ALT,
            category_orders={"Market": ALL_MARKETS},
        )
        fig_w10.update_layout(yaxis_title="% within ±10 min",
                              yaxis_range=[0, 105], template=PLOTLY_TEMPLATE)
    else:
        fig_w10 = empty_fig

    # ── Chart: Transit coverage by market ───────────────────────────────
    transit_tt = cov_df[(cov_df["mode"] == "transit")
                        & (cov_df["provider"] == "traveltime")]
    transit_g = cov_df[(cov_df["mode"] == "transit")
                       & (cov_df["provider"] == "google")]
    if not transit_tt.empty:
        cov_rows_chart = []
        for m in [mk for mk in ALL_MARKETS if mk in markets]:
            t = transit_tt[transit_tt["market"] == m]
            g = transit_g[transit_g["market"] == m]
            if t.empty:
                continue
            raw_pct = 100.0 * (t["status"] == "ok").sum() / len(t)
            # vs Google: of pairs where Google ok, what % did TT also ok?
            g_ok_coords = set(zip(
                g[g["status"] == "ok"]["origin_lat"].round(6),
                g[g["status"] == "ok"]["origin_lng"].round(6),
                g[g["status"] == "ok"]["dest_lat"].round(6),
                g[g["status"] == "ok"]["dest_lng"].round(6),
            ))
            t_ok_coords = set(zip(
                t[t["status"] == "ok"]["origin_lat"].round(6),
                t[t["status"] == "ok"]["origin_lng"].round(6),
                t[t["status"] == "ok"]["dest_lat"].round(6),
                t[t["status"] == "ok"]["dest_lng"].round(6),
            ))
            both_ok = len(g_ok_coords & t_ok_coords)
            vs_g_pct = (100.0 * both_ok / len(g_ok_coords)
                        if g_ok_coords else 0)
            cov_rows_chart.append({"Market": m, "Metric": "TT",
                                   "Coverage %": round(raw_pct, 1)})
            cov_rows_chart.append({"Market": m, "Metric": "vs Google",
                                   "Coverage %": round(vs_g_pct, 1)})
        cov_chart_df = pd.DataFrame(cov_rows_chart)
        fig_tcov = px.bar(
            cov_chart_df, x="Market", y="Coverage %", color="Metric",
            barmode="group",
            color_discrete_map={"TT": "#00BFC4", "vs Google": "#9590FF"},
            category_orders={"Market": ALL_MARKETS},
        )
        fig_tcov.update_layout(xaxis_title="Market", yaxis_range=[0, 105],
                               template=PLOTLY_TEMPLATE)
    else:
        fig_tcov = empty_fig

    # ── Chart: Driving coverage by market ───────────────────────────────
    driving_tt = cov_df[(cov_df["mode"] == "driving")
                        & (cov_df["provider"] == "traveltime")]
    driving_g = cov_df[(cov_df["mode"] == "driving")
                       & (cov_df["provider"] == "google")]
    if not driving_tt.empty:
        dcov_rows = []
        for m in [mk for mk in ALL_MARKETS if mk in markets]:
            dt = driving_tt[driving_tt["market"] == m]
            dg = driving_g[driving_g["market"] == m]
            if dt.empty:
                continue
            tt_pct = 100.0 * (dt["status"] == "ok").sum() / len(dt)
            g_pct = (100.0 * (dg["status"] == "ok").sum() / len(dg)
                     if not dg.empty else 0)
            dcov_rows.append({"Market": m, "Provider": "Google",
                              "Coverage %": round(g_pct, 1)})
            dcov_rows.append({"Market": m, "Provider": "TravelTime",
                              "Coverage %": round(tt_pct, 1)})
        dcov_chart_df = pd.DataFrame(dcov_rows)
        fig_dcov = px.bar(
            dcov_chart_df, x="Market", y="Coverage %", color="Provider",
            barmode="group",
            color_discrete_map={"Google": GGPLOT_2[0],
                                "TravelTime": GGPLOT_2[1]},
            category_orders={"Market": ALL_MARKETS},
        )
        fig_dcov.update_layout(xaxis_title="Market", yaxis_range=[0, 105],
                               template=PLOTLY_TEMPLATE)
    else:
        fig_dcov = empty_fig

    # ── Chart: Transit distance distribution (box plot by market) ─────
    transit_df = df[df["mode"] == "transit"] if len(df) > 0 else df
    if len(transit_df) > 0:
        fig_tdist = px.box(
            transit_df, x="market", y="haversine_km",
            color="market", color_discrete_map=MARKET_COLOR_MAP,
            category_orders={"market": ALL_MARKETS},
            labels={"haversine_km": "Straight-line distance (km)",
                    "market": "Market"},
        )
        fig_tdist.update_layout(showlegend=False, template=PLOTLY_TEMPLATE)
    else:
        fig_tdist = empty_fig

    # ── Chart: Scatter — Google vs TravelTime ───────────────────────────
    if len(df) > 0:
        scatter_df = (df.sample(n=min(5000, len(df)), random_state=42)
                      if len(df) > 5000 else df)
        fig_scatter = px.scatter(
            scatter_df, x="g_time_min", y="tt_time_min", color="market",
            opacity=0.45,
            labels={"g_time_min": "Google (min)",
                    "tt_time_min": "TravelTime (min)", "market": "Market"},
            category_orders={"market": ALL_MARKETS},
            color_discrete_map=MARKET_COLOR_MAP,
        )
        max_val = max(scatter_df["g_time_min"].max(),
                      scatter_df["tt_time_min"].max(), 1)
        fig_scatter.add_trace(
            go.Scatter(
                x=[0, max_val], y=[0, max_val],
                mode="lines",
                line={"dash": "dash", "color": C["text_muted"], "width": 1},
                name="y = x", showlegend=True,
            )
        )
        fig_scatter.update_layout(template=PLOTLY_TEMPLATE)
    else:
        fig_scatter = empty_fig

    # ── Chart: Histogram — signed difference ────────────────────────────
    if len(df) > 0:
        fig_hist = px.histogram(
            df, x="signed_diff_min", nbins=80,
            color="mode", color_discrete_map=MODE_COLORS,
            labels={"signed_diff_min": "TT − Google (min)"},
            barmode="overlay", opacity=0.65,
        )
        fig_hist.add_vline(x=0, line_dash="dash", line_color=C["text_muted"])
        fig_hist.update_layout(yaxis_title="Count", template=PLOTLY_TEMPLATE)
    else:
        fig_hist = empty_fig

    # ── Chart: Signed bias by market ────────────────────────────────────
    if len(df) > 0:
        bias_rows = []
        for m in [mk for mk in ALL_MARKETS if mk in markets]:
            for md in df["mode"].unique():
                bdf = df[(df["market"] == m) & (df["mode"] == md)]
                if len(bdf) == 0:
                    continue
                bias_rows.append({
                    "Market": m, "Mode": md.title(),
                    "Mean Signed Diff (min)": round(bdf["signed_diff_min"].mean(), 2),
                })
        bias_df = pd.DataFrame(bias_rows)
        if not bias_df.empty:
            fig_bias = px.bar(
                bias_df, x="Market", y="Mean Signed Diff (min)",
                color="Mode", barmode="group",
                color_discrete_map=MODE_COLORS_TITLE,
                category_orders={"Market": ALL_MARKETS},
            )
            fig_bias.add_hline(y=0, line_dash="dash",
                               line_color=C["text_muted"], line_width=1)
            fig_bias.update_layout(
                yaxis_title="Mean signed diff (min)",
                template=PLOTLY_TEMPLATE,
            )
        else:
            fig_bias = empty_fig
    else:
        fig_bias = empty_fig

    # ── Chart: Accuracy by distance band ────────────────────────────────
    if len(df) > 0:
        dist_rows = []
        for band in ["0-5km", "5-10km", "10-20km", "20-35km", "35-50km", "50km+"]:
            for md in df["mode"].unique():
                bdf = df[(df["dist_band"] == band) & (df["mode"] == md)]
                if len(bdf) == 0:
                    continue
                dist_rows.append({
                    "Distance Band": band, "Mode": md.title(),
                    "Within ±10min %": round(_pct(bdf["abs_diff_min"], 10), 1),
                    "n": len(bdf),
                })
        dist_band_df = pd.DataFrame(dist_rows)
        if not dist_band_df.empty:
            fig_dist = px.bar(
                dist_band_df, x="Distance Band", y="Within ±10min %",
                color="Mode", barmode="group",
                color_discrete_map=MODE_COLORS_TITLE,
                hover_data=["n"],
            )
            fig_dist.update_layout(yaxis_range=[0, 105],
                                   template=PLOTLY_TEMPLATE)
        else:
            fig_dist = empty_fig
    else:
        fig_dist = empty_fig

    # ── Chart: Accuracy by commute time band ────────────────────────────
    if len(df) > 0:
        time_rows = []
        for band in ["0-15min", "15-30min", "30-60min", "60min+"]:
            for md in df["mode"].unique():
                bdf = df[(df["time_band"] == band) & (df["mode"] == md)]
                if len(bdf) == 0:
                    continue
                time_rows.append({
                    "Time Band": band, "Mode": md.title(),
                    "Within ±10min %": round(_pct(bdf["abs_diff_min"], 10), 1),
                    "n": len(bdf),
                })
        time_band_df = pd.DataFrame(time_rows)
        if not time_band_df.empty:
            fig_time = px.bar(
                time_band_df, x="Time Band", y="Within ±10min %",
                color="Mode", barmode="group",
                color_discrete_map=MODE_COLORS_TITLE,
                hover_data=["n"],
            )
            fig_time.update_layout(yaxis_range=[0, 105],
                                   template=PLOTLY_TEMPLATE)
        else:
            fig_time = empty_fig
    else:
        fig_time = empty_fig

    # ── Detail table: by distance band ──────────────────────────────────
    if len(df) > 0:
        dbt_rows = []
        for band in ["0-5km", "5-10km", "10-20km", "20-35km", "35-50km", "50km+"]:
            for md in modes_to_show:
                bdf = df[(df["dist_band"] == band) & (df["mode"] == md)]
                n = len(bdf)
                if n == 0:
                    continue
                dbt_rows.append({
                    "Band": band,
                    "Mode": md.title(),
                    "n": n,
                    "Median Diff": f"{bdf['abs_diff_min'].median():.1f}m",
                    "Mean % Err": f"{bdf['pct_error'].mean():+.1f}%",
                    "W ±10min": f"{_pct(bdf['abs_diff_min'], 10):.0f}%",
                    "W ±15min": f"{_pct(bdf['abs_diff_min'], 15):.0f}%",
                })
        dbt_df = pd.DataFrame(dbt_rows) if dbt_rows else pd.DataFrame()
        dist_band_tbl = dash_table.DataTable(
            data=dbt_df.to_dict("records") if not dbt_df.empty else [],
            columns=[{"name": c, "id": c} for c in dbt_df.columns] if not dbt_df.empty else [],
            sort_action="native",
            **_table_styles(),
        ) if not dbt_df.empty else no_data_div
    else:
        dist_band_tbl = no_data_div

    # ── Detail table: by commute time band ──────────────────────────────
    if len(df) > 0:
        tbt_rows = []
        for band in ["0-15min", "15-30min", "30-60min", "60min+"]:
            for md in modes_to_show:
                bdf = df[(df["time_band"] == band) & (df["mode"] == md)]
                n = len(bdf)
                if n == 0:
                    continue
                tbt_rows.append({
                    "Band": band,
                    "Mode": md.title(),
                    "n": n,
                    "Median Diff": f"{bdf['abs_diff_min'].median():.1f}m",
                    "Mean % Err": f"{bdf['pct_error'].mean():+.1f}%",
                    "W ±10min": f"{_pct(bdf['abs_diff_min'], 10):.0f}%",
                    "W ±15min": f"{_pct(bdf['abs_diff_min'], 15):.0f}%",
                })
        tbt_df = pd.DataFrame(tbt_rows) if tbt_rows else pd.DataFrame()
        time_band_tbl = dash_table.DataTable(
            data=tbt_df.to_dict("records") if not tbt_df.empty else [],
            columns=[{"name": c, "id": c} for c in tbt_df.columns] if not tbt_df.empty else [],
            sort_action="native",
            **_table_styles(),
        ) if not tbt_df.empty else no_data_div
    else:
        time_band_tbl = no_data_div

    # ── Coverage table (by market) ──────────────────────────────────────
    cov_transit_tt = cov_df[(cov_df["mode"] == "transit")
                            & (cov_df["provider"] == "traveltime")]
    cov_transit_g = cov_df[(cov_df["mode"] == "transit")
                           & (cov_df["provider"] == "google")]
    cov_rows = []
    for m in markets:
        tt = cov_transit_tt[cov_transit_tt["market"] == m]
        g = cov_transit_g[cov_transit_g["market"] == m]
        total = len(tt)
        if total == 0:
            continue
        tt_ok = int((tt["status"] == "ok").sum())
        tt_nr = int((tt["status"] == "no_route").sum())
        tt_err = int((tt["status"] == "error").sum())
        g_ok = int((g["status"] == "ok").sum()) if not g.empty else 0
        g_nr = int((g["status"] == "no_route").sum()) if not g.empty else 0
        g_err = int((g["status"] == "error").sum()) if not g.empty else 0
        cov_rows.append({
            "Market": m,
            "Pairs": total,
            "G OK": g_ok,
            "G No Route": g_nr,
            "G Error": g_err,
            "G Cov %": round(100.0 * g_ok / total, 1) if total > 0 else 0,
            "TT OK": tt_ok,
            "TT No Route": tt_nr,
            "TT Error": tt_err,
            "TT Cov %": round(100.0 * tt_ok / total, 1) if total > 0 else 0,
        })
    cov_table_df = pd.DataFrame(cov_rows) if cov_rows else pd.DataFrame()
    cov_header_tooltips = {
        "Market": "Two-letter country code",
        "Pairs": "Total transit OD pairs tested for this market",
        "G OK": "Google returned a valid transit route",
        "G No Route": "Google could not find a transit route",
        "G Error": "Google returned an API error",
        "G Cov %": "Google coverage: % of pairs where Google returned a result",
        "TT OK": "TravelTime returned a valid transit route",
        "TT No Route": "TravelTime could not find a transit route",
        "TT Error": "TravelTime returned an API error",
        "TT Cov %": "TravelTime coverage: % of pairs where TT returned a result",
    }
    cov_table = dash_table.DataTable(
        data=cov_table_df.to_dict("records") if not cov_table_df.empty else [],
        columns=[{"name": c, "id": c} for c in cov_table_df.columns]
        if not cov_table_df.empty else [],
        sort_action="native",
        tooltip_header=cov_header_tooltips,
        tooltip_delay=0,
        tooltip_duration=None,
        style_header_conditional=[{
            "if": {"column_id": col},
            "textDecoration": "underline",
            "textDecorationStyle": "dotted",
        } for col in cov_header_tooltips],
        css=[{"selector": ".dash-table-tooltip",
              "rule": ("background-color: #1f2937; color: #f9fafb; "
                       "font-family: Inter, sans-serif; font-size: 0.8rem; "
                       "border-radius: 6px; padding: 6px 10px; "
                       "max-width: 300px; white-space: normal;")}],
        **_table_styles(),
    ) if not cov_table_df.empty else no_data_div

    # ── Metro-area coverage table ───────────────────────────────────────
    if not cov_transit_tt.empty:
        metro_rows = []
        for m in markets:
            mdf_tt = cov_transit_tt[cov_transit_tt["market"] == m]
            mdf_g = cov_transit_g[cov_transit_g["market"] == m]
            if mdf_tt.empty:
                continue
            for metro_name in sorted(mdf_tt["metro"].unique()):
                if metro_name == "Other":
                    continue
                tt_metro = mdf_tt[mdf_tt["metro"] == metro_name]
                g_metro = mdf_g[mdf_g["metro"] == metro_name]
                total = len(tt_metro)
                tt_ok = int((tt_metro["status"] == "ok").sum())
                tt_nr = int((tt_metro["status"] == "no_route").sum())
                tt_err = int((tt_metro["status"] == "error").sum())
                g_ok = int((g_metro["status"] == "ok").sum()) if not g_metro.empty else 0
                g_nr = int((g_metro["status"] == "no_route").sum()) if not g_metro.empty else 0
                g_err = int((g_metro["status"] == "error").sum()) if not g_metro.empty else 0
                metro_rows.append({
                    "Market": m,
                    "Metro": metro_name,
                    "Pairs": total,
                    "G OK": g_ok,
                    "G No Route": g_nr,
                    "G Error": g_err,
                    "G Cov %": round(100.0 * g_ok / total, 1) if total > 0 else 0,
                    "TT OK": tt_ok,
                    "TT No Route": tt_nr,
                    "TT Error": tt_err,
                    "TT Cov %": round(100.0 * tt_ok / total, 1) if total > 0 else 0,
                })
        metro_df_out = pd.DataFrame(metro_rows) if metro_rows else pd.DataFrame()
        metro_table = dash_table.DataTable(
            data=metro_df_out.to_dict("records") if not metro_df_out.empty else [],
            columns=[{"name": c, "id": c} for c in metro_df_out.columns]
            if not metro_df_out.empty else [],
            sort_action="native",
            filter_action="native",
            page_size=30,
            **_table_styles(),
        ) if not metro_df_out.empty else no_data_div
    else:
        metro_table = no_data_div

    return (
        exec_summary, cards, acc_table,
        fig_median, fig_w10, fig_tcov, fig_dcov, fig_tdist,
        fig_scatter, fig_hist, fig_bias, fig_dist, fig_time,
        cov_table, dist_band_tbl, time_band_tbl, metro_table,
    )


@callback(
    Output("chart-od-map", "figure"),
    Input("market-filter", "value"),
    Input("map-mode-toggle", "value"),
    Input("map-color-toggle", "value"),
)
def update_od_map(markets: list[str], mode: str, color_by: str):
    import math

    if not markets:
        markets = ALL_MARKETS

    map_df = COVERAGE_DF[
        (COVERAGE_DF["mode"] == mode)
        & (COVERAGE_DF["provider"] == "traveltime")
        & (COVERAGE_DF["market"].isin(markets))
    ].copy()

    if map_df.empty:
        return go.Figure().update_layout(
            template=PLOTLY_TEMPLATE,
            annotations=[dict(text="No data", showarrow=False,
                              font=dict(size=16, color=C["text_muted"]))],
        )

    STATUS_COLORS = {"ok": "#00BFC4", "no_route": "#F8766D", "error": "#9590FF"}

    fig = go.Figure()

    # Draw connecting lines — group by color category for efficiency
    if color_by == "status":
        groups = {"ok": STATUS_COLORS["ok"], "no_route": STATUS_COLORS["no_route"],
                  "error": STATUS_COLORS["error"]}
        group_col = "status"
    else:
        groups = {m: MARKET_COLOR_MAP.get(m, "#999999")
                  for m in map_df["market"].unique()}
        group_col = "market"

    for group_val, color in groups.items():
        sub = map_df[map_df[group_col] == group_val]
        if sub.empty:
            continue
        # Build lat/lon arrays with None separators between each line segment
        lats = []
        lons = []
        for _, row in sub.iterrows():
            lats.extend([row["origin_lat"], row["dest_lat"], None])
            lons.extend([row["origin_lng"], row["dest_lng"], None])
        fig.add_trace(go.Scattermap(
            lat=lats, lon=lons,
            mode="lines",
            line=dict(width=2, color=color),
            opacity=0.2,
            showlegend=False,
            hoverinfo="skip",
        ))

    # Plot origin points
    if color_by == "status":
        map_df["status_label"] = map_df["status"].map(
            {"ok": "OK", "no_route": "No Route", "error": "Error"})
        for label, color in [("OK", STATUS_COLORS["ok"]),
                             ("No Route", STATUS_COLORS["no_route"]),
                             ("Error", STATUS_COLORS["error"])]:
            sub = map_df[map_df["status_label"] == label]
            if sub.empty:
                continue
            fig.add_trace(go.Scattermap(
                lat=sub["origin_lat"], lon=sub["origin_lng"],
                mode="markers",
                marker=dict(size=6, color=color),
                opacity=0.7,
                name=f"{label} (origin)",
                customdata=sub[["market", "metro", "status_label"]].values,
                hovertemplate=(
                    "Origin<br>Market: %{customdata[0]}<br>Metro: %{customdata[1]}"
                    "<br>Status: %{customdata[2]}<br>(%{lat:.4f}, %{lon:.4f})<extra></extra>"
                ),
            ))
            fig.add_trace(go.Scattermap(
                lat=sub["dest_lat"], lon=sub["dest_lng"],
                mode="markers",
                marker=dict(size=4, color=color, symbol="circle"),
                opacity=0.4,
                name=f"{label} (dest)",
                customdata=sub[["market", "metro", "status_label"]].values,
                hovertemplate=(
                    "Dest<br>Market: %{customdata[0]}<br>Metro: %{customdata[1]}"
                    "<br>Status: %{customdata[2]}<br>(%{lat:.4f}, %{lon:.4f})<extra></extra>"
                ),
            ))
    else:
        for mkt in [m for m in ALL_MARKETS if m in map_df["market"].unique()]:
            sub = map_df[map_df["market"] == mkt]
            color = MARKET_COLOR_MAP.get(mkt, "#999999")
            fig.add_trace(go.Scattermap(
                lat=sub["origin_lat"], lon=sub["origin_lng"],
                mode="markers",
                marker=dict(size=6, color=color),
                opacity=0.7,
                name=f"{mkt} (origin)",
                customdata=sub[["market", "metro", "status"]].values,
                hovertemplate=(
                    "Origin<br>Market: %{customdata[0]}<br>Metro: %{customdata[1]}"
                    "<br>Status: %{customdata[2]}<br>(%{lat:.4f}, %{lon:.4f})<extra></extra>"
                ),
            ))
            fig.add_trace(go.Scattermap(
                lat=sub["dest_lat"], lon=sub["dest_lng"],
                mode="markers",
                marker=dict(size=4, color=color, symbol="circle"),
                opacity=0.4,
                name=f"{mkt} (dest)",
                customdata=sub[["market", "metro", "status"]].values,
                hovertemplate=(
                    "Dest<br>Market: %{customdata[0]}<br>Metro: %{customdata[1]}"
                    "<br>Status: %{customdata[2]}<br>(%{lat:.4f}, %{lon:.4f})<extra></extra>"
                ),
            ))

    # Auto-fit: compute center + zoom, and constrain panning via bounds
    all_lats = pd.concat([map_df["origin_lat"], map_df["dest_lat"]])
    all_lngs = pd.concat([map_df["origin_lng"], map_df["dest_lng"]])
    lat_min, lat_max = all_lats.min(), all_lats.max()
    lng_min, lng_max = all_lngs.min(), all_lngs.max()
    center_lat = (lat_min + lat_max) / 2
    center_lng = (lng_min + lng_max) / 2
    lat_span = max(lat_max - lat_min, 0.5)
    lng_span = max(lng_max - lng_min, 0.5)
    zoom = max(0, min(math.log2(360 / lng_span), math.log2(180 / lat_span)) - 0.5)
    pad_lat = max(lat_span * 0.15, 2)
    pad_lng = max(lng_span * 0.15, 2)

    fig.update_layout(
        map=dict(
            style="carto-positron",
            center=dict(lat=center_lat, lon=center_lng),
            zoom=zoom,
            bounds=dict(
                south=lat_min - pad_lat,
                north=lat_max + pad_lat,
                west=lng_min - pad_lng,
                east=lng_max + pad_lng,
            ),
        ),
        template=PLOTLY_TEMPLATE,
        margin=dict(l=0, r=0, t=8, b=0),
        height=550,
        legend=dict(
            title=None,
            orientation="h",
            yanchor="top", y=0.99,
            xanchor="left", x=0.01,
            bgcolor="rgba(255,255,255,0.85)",
            font=dict(size=12),
        ),
    )
    return fig


@callback(
    Output("vh-summary-cards", "children"),
    Output("vh-comparison-table", "children"),
    Output("chart-vh-scatter", "figure"),
    Output("chart-vh-hist", "figure"),
    Output("chart-vh-metro-accuracy", "figure"),
    Output("chart-vh-metro-coverage", "figure"),
    Input("market-filter", "value"),
)
def update_valhalla_section(markets: list[str]):
    if not markets:
        markets = ALL_MARKETS

    empty_fig = go.Figure().update_layout(
        template=PLOTLY_TEMPLATE,
        annotations=[dict(text="No data", showarrow=False,
                          font=dict(size=16, color=C["text_muted"]))],
    )
    no_data_div = html.Div(
        "No Valhalla data for current filters.",
        style={"padding": "20px", "color": C["text_muted"]},
    )

    # Filter to US/CA (Valhalla transit coverage markets)
    vh_markets = [m for m in markets if m in ("US", "CA")]
    vh_df = VALHALLA_DF[
        (VALHALLA_DF["market"].isin(vh_markets)) & (VALHALLA_DF["mode"] == "transit")
    ] if not VALHALLA_DF.empty else pd.DataFrame()
    tt_df = PAIRED_DF[
        (PAIRED_DF["market"].isin(vh_markets)) & (PAIRED_DF["mode"] == "transit")
    ] if not PAIRED_DF.empty else pd.DataFrame()

    cov_df = COVERAGE_DF[
        (COVERAGE_DF["market"].isin(vh_markets)) & (COVERAGE_DF["mode"] == "transit")
    ]

    if vh_df.empty:
        return no_data_div, no_data_div, empty_fig, empty_fig, empty_fig, empty_fig

    # ── Summary cards ───────────────────────────────────────────────────
    vh_w10 = _pct(vh_df["abs_diff_min"], 10)
    tt_w10 = _pct(tt_df["abs_diff_min"], 10) if len(tt_df) > 0 else 0
    vh_cov_total = len(cov_df[cov_df["provider"] == "valhalla"])
    vh_cov_ok = (cov_df[cov_df["provider"] == "valhalla"]["status"] == "ok").sum()
    vh_cov_pct = 100.0 * vh_cov_ok / vh_cov_total if vh_cov_total > 0 else 0
    cards = html.Div(
        className="stat-cards-row",
        children=[
            _stat_card("Valhalla Paired", f"{len(vh_df):,}",
                       tooltip="OD pairs where both Valhalla and Google returned ok"),
            _stat_card("VH Within ±10min", f"{vh_w10:.0f}%", "orange"),
            _stat_card("TT Within ±10min", f"{tt_w10:.0f}%", "blue",
                       tooltip="TravelTime on same markets for comparison"),
            _stat_card("VH Median Diff", f"{vh_df['abs_diff_min'].median():.1f} min", "teal"),
            _stat_card("VH Coverage", f"{vh_cov_pct:.0f}%", "",
                       tooltip=f"{vh_cov_ok}/{vh_cov_total} transit pairs returned ok"),
        ],
    )

    # ── Comparison table ────────────────────────────────────────────────
    comp_rows = []
    for label, ddf, provider in [("TravelTime", tt_df, "TT"), ("Valhalla", vh_df, "VH")]:
        if len(ddf) == 0:
            continue
        for m in vh_markets:
            mdf = ddf[ddf["market"] == m]
            n = len(mdf)
            if n == 0:
                continue
            cov_prov = cov_df[
                (cov_df["provider"] == label.lower()) & (cov_df["market"] == m)
            ]
            cov_n = len(cov_prov)
            cov_ok = (cov_prov["status"] == "ok").sum() if cov_n > 0 else 0
            comp_rows.append({
                "Provider": provider,
                "Market": m,
                "Coverage": f"{100*cov_ok/cov_n:.0f}%" if cov_n > 0 else "—",
                "Paired n": n,
                "Median Diff": f"{mdf['abs_diff_min'].median():.1f}m",
                "Mean Diff": f"{mdf['abs_diff_min'].mean():.1f}m",
                "W ±5min": f"{_pct(mdf['abs_diff_min'], 5):.0f}%",
                "W ±10min": f"{_pct(mdf['abs_diff_min'], 10):.0f}%",
                "W ±15min": f"{_pct(mdf['abs_diff_min'], 15):.0f}%",
                "Bias": f"{mdf['signed_diff_min'].mean():+.1f}m",
            })
    comp_df = pd.DataFrame(comp_rows) if comp_rows else pd.DataFrame()
    comp_table = dash_table.DataTable(
        data=comp_df.to_dict("records") if not comp_df.empty else [],
        columns=[{"name": c, "id": c} for c in comp_df.columns]
        if not comp_df.empty else [],
        sort_action="native",
        **_table_styles(),
    ) if not comp_df.empty else no_data_div

    # ── Scatter: Valhalla vs Google ─────────────────────────────────────
    scatter_df = vh_df.copy()
    scatter_df["metro"] = scatter_df.apply(
        lambda r: (m.name if (m := get_metro_area(r["origin_lat"], r["origin_lng"]))
                   else "Other"),
        axis=1,
    )
    fig_scatter = px.scatter(
        scatter_df, x="g_time_min", y="vh_time_min", color="market",
        opacity=0.5,
        labels={"g_time_min": "Google (min)", "vh_time_min": "Valhalla (min)",
                "market": "Market"},
        color_discrete_map=MARKET_COLOR_MAP,
        hover_data=["metro"],
    )
    max_val = max(scatter_df["g_time_min"].max(),
                  scatter_df["vh_time_min"].max(), 1)
    fig_scatter.add_trace(go.Scatter(
        x=[0, max_val], y=[0, max_val],
        mode="lines",
        line={"dash": "dash", "color": C["text_muted"], "width": 1},
        name="y = x", showlegend=True,
    ))
    fig_scatter.update_layout(template=PLOTLY_TEMPLATE)

    # ── Histogram: signed diff ──────────────────────────────────────────
    fig_hist = px.histogram(
        vh_df, x="signed_diff_min", nbins=60,
        color="market", color_discrete_map=MARKET_COLOR_MAP,
        labels={"signed_diff_min": "Valhalla − Google (min)"},
        barmode="overlay", opacity=0.65,
    )
    fig_hist.add_vline(x=0, line_dash="dash", line_color=C["text_muted"])
    fig_hist.update_layout(yaxis_title="Count", template=PLOTLY_TEMPLATE)

    # ── Metro accuracy comparison ───────────────────────────────────────
    # Build per-metro accuracy for TT and Valhalla (transit, US/CA)
    vh_df_metro = vh_df.copy()
    vh_df_metro["metro"] = vh_df_metro.apply(
        lambda r: (m.name if (m := get_metro_area(r["origin_lat"], r["origin_lng"]))
                   else "Other"), axis=1,
    )
    tt_df_metro = tt_df.copy()
    if len(tt_df_metro) > 0:
        tt_df_metro["metro"] = tt_df_metro.apply(
            lambda r: (m.name if (m := get_metro_area(r["origin_lat"], r["origin_lng"]))
                       else "Other"), axis=1,
        )

    acc_rows = []
    all_metros = sorted(set(vh_df_metro["metro"].unique()))
    for metro_name in all_metros:
        if metro_name == "Other":
            continue
        vhm = vh_df_metro[vh_df_metro["metro"] == metro_name]
        if len(vhm) >= 3:
            acc_rows.append({
                "Metro": metro_name,
                "Provider": "Valhalla",
                "Within ±10min %": round(_pct(vhm["abs_diff_min"], 10), 1),
                "n": len(vhm),
            })
        if len(tt_df_metro) > 0:
            ttm = tt_df_metro[tt_df_metro["metro"] == metro_name]
            if len(ttm) >= 3:
                acc_rows.append({
                    "Metro": metro_name,
                    "Provider": "TravelTime",
                    "Within ±10min %": round(_pct(ttm["abs_diff_min"], 10), 1),
                    "n": len(ttm),
                })

    acc_metro_df = pd.DataFrame(acc_rows)
    if not acc_metro_df.empty:
        metro_order = (
            acc_metro_df[acc_metro_df["Provider"] == "Valhalla"]
            .sort_values("n", ascending=False)["Metro"].tolist()
        )
        fig_metro_acc = px.bar(
            acc_metro_df, x="Metro", y="Within ±10min %", color="Provider",
            barmode="group",
            color_discrete_map={"Valhalla": "#E76BF3", "TravelTime": "#00BFC4"},
            category_orders={"Metro": metro_order},
            hover_data=["n"],
        )
        fig_metro_acc.update_layout(yaxis_range=[0, 105], template=PLOTLY_TEMPLATE)
    else:
        fig_metro_acc = empty_fig

    # ── Metro coverage comparison ───────────────────────────────────────
    cov_rows = []
    for provider in ["google", "traveltime", "valhalla"]:
        prov_cov = cov_df[cov_df["provider"] == provider]
        for metro_name in sorted(prov_cov["metro"].unique()):
            if metro_name == "Other":
                continue
            mdf = prov_cov[prov_cov["metro"] == metro_name]
            total = len(mdf)
            ok = (mdf["status"] == "ok").sum()
            if total == 0:
                continue
            cov_rows.append({
                "Metro": metro_name,
                "Provider": provider.title() if provider != "traveltime" else "TravelTime",
                "Coverage %": round(100.0 * ok / total, 1),
                "n": total,
            })
    cov_metro_df = pd.DataFrame(cov_rows)
    if not cov_metro_df.empty:
        # Order by Valhalla coverage descending
        vh_order = (
            cov_metro_df[cov_metro_df["Provider"] == "Valhalla"]
            .sort_values("Coverage %", ascending=False)["Metro"].tolist()
        )
        fig_metro_cov = px.bar(
            cov_metro_df, x="Metro", y="Coverage %", color="Provider",
            barmode="group",
            color_discrete_map={
                "Google": GGPLOT_2[0], "TravelTime": GGPLOT_2[1],
                "Valhalla": "#E76BF3",
            },
            category_orders={"Metro": vh_order},
            hover_data=["n"],
        )
        fig_metro_cov.update_layout(yaxis_range=[0, 105], template=PLOTLY_TEMPLATE)
    else:
        fig_metro_cov = empty_fig

    return cards, comp_table, fig_scatter, fig_hist, fig_metro_acc, fig_metro_cov


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
