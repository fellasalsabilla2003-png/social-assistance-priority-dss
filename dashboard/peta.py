import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils import (
    load_recommendation_data, load_geojson, compute_centroids,
    CATEGORY_ORDER, CATEGORY_COLORS,
)


def section_title(text):
    st.markdown(
        f"<div style='display:inline-block; background:#EAF4FC; color:#0B1E3D; "
        f"font-weight:800; font-size:0.95rem; padding:6px 14px; border-radius:6px; "
        f"margin-bottom:10px;'>{text}</div>",
        unsafe_allow_html=True,
    )


def render():
    df = load_recommendation_data()

    if "filter_kategori" not in st.session_state:
        st.session_state["filter_kategori"] = list(CATEGORY_ORDER)
    if "filter_search" not in st.session_state:
        st.session_state["filter_search"] = ""
    if "selected_region" not in st.session_state:
        st.session_state["selected_region"] = None

    # ================= HEADER =================
    st.markdown(
        "<div style='font-size:2rem;font-weight:800;color:#0B1E3D;line-height:1.1;'>"
        "PETA PRIORITAS</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='font-size:0.92rem;color:#5B6B82;margin-top:2px;margin-bottom:14px;'>"
        "Peta interaktif 38 Kabupaten/Kota Jawa Timur berdasarkan hasil TOPSIS — Tahun 2025</div>",
        unsafe_allow_html=True,
    )

    # ================= FILTER BAR =================
    with st.container(border=True):
        f1, f2, f3 = st.columns([2, 2, 0.8])
        with f1:
            kategori_pilih = st.multiselect(
                "Kategori Prioritas", options=CATEGORY_ORDER,
                default=st.session_state["filter_kategori"], key="peta_filter_kategori_widget",
            )
            st.session_state["filter_kategori"] = kategori_pilih if kategori_pilih else list(CATEGORY_ORDER)
        with f2:
            search = st.text_input(
                "Cari Kabupaten/Kota", value=st.session_state["filter_search"],
                placeholder="contoh: Bangkalan", key="peta_search_widget",
            )
            st.session_state["filter_search"] = search
        with f3:
            st.write("")
            if st.button("Reset Filter", use_container_width=True, key="peta_reset_btn"):
                st.session_state["filter_kategori"] = list(CATEGORY_ORDER)
                st.session_state["filter_search"] = ""
                st.session_state["selected_region"] = None
                st.rerun()

    df_filtered = df[df["Kategori_Prioritas"].isin(st.session_state["filter_kategori"])]
    if st.session_state["filter_search"]:
        df_filtered = df_filtered[
            df_filtered["Kabupaten/Kota"].str.contains(st.session_state["filter_search"], case=False)
        ]

    st.write("")

    # ================= PETA (besar) + PANEL DETAIL =================
    col_map, col_detail = st.columns([1.8, 1])

    with col_map:
        with st.container(border=True):
            section_title(f"PETA 38 KABUPATEN/KOTA JAWA TIMUR — 2025 ({len(df_filtered)} ditampilkan)")

            geojson = load_geojson()
            centroids = compute_centroids(geojson)

            fig = px.choropleth(
                df_filtered, geojson=geojson, locations="Kabupaten/Kota",
                featureidkey="properties.kabkot", color="Kategori_Prioritas",
                category_orders={"Kategori_Prioritas": CATEGORY_ORDER},
                color_discrete_map=CATEGORY_COLORS, hover_name="Kabupaten/Kota",
                hover_data={
                    "Priority_Score": ":.4f", "Ranking": True,
                    "Kategori_Prioritas": True, "Indikator_Dominan": True,
                },
            )
            fig.update_geos(
                visible=True, resolution=50,
                showcoastlines=True, coastlinecolor="#8FA8C2",
                showland=True, landcolor="#F6F9FC",
                showocean=True, oceancolor="#DCEEFB",
                showcountries=True, countrycolor="#C7D3E3",
                lataxis_range=[-9.3, -5.6], lonaxis_range=[110.3, 116.8],
            )

            lons = [centroids[n][0] for n in df_filtered["Kabupaten/Kota"] if n in centroids]
            lats = [centroids[n][1] for n in df_filtered["Kabupaten/Kota"] if n in centroids]
            names = [n for n in df_filtered["Kabupaten/Kota"] if n in centroids]
            fig.add_trace(go.Scattergeo(
                lon=lons, lat=lats, mode="text", text=names,
                textfont=dict(size=9, color="#0B1E3D", family="Arial Black"),
                showlegend=False, hoverinfo="skip",
            ))

            fig.update_layout(
                geo2=dict(
                    scope="asia", projection_type="mercator",
                    showland=True, landcolor="#E5EDF5",
                    showcountries=True, countrycolor="#B8C4D9",
                    showocean=True, oceancolor="#DCEEFB",
                    lataxis_range=[-11, 8], lonaxis_range=[94, 142],
                    domain=dict(x=[0.0, 0.2], y=[0.7, 1.0]),
                    bgcolor="rgba(0,0,0,0)",
                )
            )
            fig.add_trace(go.Scattergeo(
                lon=[112.5], lat=[-7.6], mode="markers+text",
                marker=dict(size=8, color="#0B1E3D", symbol="star"),
                text=["Jatim"], textposition="bottom center",
                textfont=dict(size=8, color="#0B1E3D"),
                showlegend=False, hoverinfo="skip", geo="geo2",
            ))

            fig.update_layout(
                margin=dict(t=0, b=0, l=0, r=0), height=650,
                legend=dict(title="Kategori Prioritas", orientation="h", y=-0.02),
            )

            map_event = st.plotly_chart(
                fig, use_container_width=True, on_select="rerun", key="peta_page_map"
            )
            try:
                points = map_event["selection"]["points"]
            except Exception:
                points = []
            if points:
                lokasi = points[0].get("location")
                if lokasi:
                    st.session_state["selected_region"] = lokasi
                    st.rerun()

            st.caption("Klik wilayah untuk melihat detail lengkap di panel sebelah kanan.")

    with col_detail:
        with st.container(border=True):
            section_title("LEGENDA & DISTRIBUSI")
            counts = df_filtered["Kategori_Prioritas"].value_counts()
            for kategori in CATEGORY_ORDER:
                jumlah = int(counts.get(kategori, 0))
                color = CATEGORY_COLORS[kategori]
                st.markdown(f"""
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                    <div style="width:14px; height:14px; background:{color}; border-radius:3px;"></div>
                    <div style="font-size:0.85rem; color:#0B1E3D;">{kategori}</div>
                    <div style="margin-left:auto; font-size:0.85rem; font-weight:700; color:#0B1E3D;">{jumlah}</div>
                </div>
                """, unsafe_allow_html=True)

        with st.container(border=True):
            section_title("DETAIL DAERAH TERPILIH")
            region = st.session_state["selected_region"]

            if region and region in df["Kabupaten/Kota"].values:
                row = df[df["Kabupaten/Kota"] == region].iloc[0]
                color = CATEGORY_COLORS[row["Kategori_Prioritas"]]

                st.markdown(f"<div style='font-size:1.2rem;font-weight:800;color:#0B1E3D;'>{row['Kabupaten/Kota']}</div>", unsafe_allow_html=True)
                st.markdown(
                    f"<span style='background:{color}22;color:{color};border:1px solid {color}80;"
                    f"padding:4px 12px;border-radius:14px;font-size:0.8rem;font-weight:700;'>"
                    f"{row['Kategori_Prioritas']}</span>",
                    unsafe_allow_html=True,
                )
                st.write("")

                c1, c2 = st.columns(2)
                c1.metric("Priority Score", f"{row['Priority_Score']:.4f}")
                c2.metric("Ranking", f"#{int(row['Ranking'])} / 38")

                st.markdown(f"**Indikator Dominan:**  \n{row['Indikator_Dominan']}")
                st.info(f"**Rekomendasi:**  \n{row['Rekomendasi']}")

                st.caption("Buka menu 'Detail Daerah' di sidebar untuk melihat tren historis dan informasi lengkap.")

                if st.button("Bersihkan Pilihan", use_container_width=True, key="clear_selected_region"):
                    st.session_state["selected_region"] = None
                    st.rerun()
            else:
                st.info("Klik salah satu wilayah pada peta untuk melihat detail lengkapnya di sini.")