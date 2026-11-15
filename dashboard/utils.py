import json
import pandas as pd
import streamlit as st

DATA_DIR = "data"


@st.cache_data
def load_recommendation_data():
    return pd.read_csv(f"{DATA_DIR}/recommendation_2025.csv")


@st.cache_data
def load_clustering_data():
    return pd.read_csv(f"{DATA_DIR}/clustering_result_2025.csv")


@st.cache_data
def load_historical_data():
    """Data mentah 2019-2025, dipakai untuk grafik tren historis per daerah."""
    df = pd.read_csv(f"{DATA_DIR}/dataset_bps.csv")
    df = df.dropna(how="all")  # buang baris kosong sisa export Excel
    df["Tahun"] = df["Tahun"].astype(int)
    return df


@st.cache_data
def load_geojson():
    with open(f"{DATA_DIR}/geojson_jatim.geojson") as f:
        return json.load(f)


@st.cache_data
def compute_centroids(geojson):
    result = {}
    for feat in geojson["features"]:
        nama = feat["properties"]["kabkot"]
        coords = feat["geometry"]["coordinates"]

        def flatten(c):
            if isinstance(c[0], (int, float)):
                yield c
            else:
                for x in c:
                    yield from flatten(x)

        pts = list(flatten(coords))
        lon = sum(p[0] for p in pts) / len(pts)
        lat = sum(p[1] for p in pts) / len(pts)
        result[nama] = (lon, lat)
    return result


CATEGORY_ORDER = ["Sangat Tinggi", "Tinggi", "Sedang", "Rendah"]

CATEGORY_COLORS = {
    "Sangat Tinggi": "#E63946",
    "Tinggi": "#F4A261",
    "Sedang": "#E9C46A",
    "Rendah": "#2A9D8F",
}

CATEGORY_ICONS = {
    "Sangat Tinggi": "🔴",
    "Tinggi": "🟠",
    "Sedang": "🟡",
    "Rendah": "🟢",
}

INDICATOR_DIRECTION = {
    "Kemiskinan": "Benefit",
    "IPM": "Cost",
    "TPT": "Benefit",
    "Pertumbuhan Ekonomi": "Cost",
}


def badge_html(kategori):
    color = CATEGORY_COLORS[kategori]
    return (
        f'<span style="background:{color}26;color:{color};border:1px solid {color}80;'
        f'padding:4px 12px;border-radius:14px;font-size:0.82rem;font-weight:600;">'
        f'{kategori}</span>'
    )