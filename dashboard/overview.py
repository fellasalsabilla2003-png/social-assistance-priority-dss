import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy.spatial import ConvexHull
from sklearn.decomposition import PCA
from utils import (
    load_recommendation_data, load_geojson, load_clustering_data, load_historical_data,
    compute_centroids, CATEGORY_ORDER, CATEGORY_COLORS,
)


def kpi_card(col, label, value, color, key=None, sub=None, button_label=None, on_click_kategori=None):
    with col:
        with st.container(border=True):
            st.markdown(
                f"<div style='height:4px;background:{color};border-radius:4px;margin-bottom:8px;'></div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='font-size:0.78rem;font-weight:600;color:#5B6B82;"
                f"text-transform:uppercase;letter-spacing:0.03em;'>{label}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='font-size:1.9rem;font-weight:800;color:#0B1E3D;line-height:1.15;'>{value}</div>",
                unsafe_allow_html=True,
            )
            if sub:
                st.markdown(f"<div style='font-size:0.74rem;color:#8B98AC;'>{sub}</div>", unsafe_allow_html=True)
            if button_label and key:
                if st.button(button_label, key=key, use_container_width=True):
                    if on_click_kategori:
                        st.session_state["filter_kategori"] = [on_click_kategori]
                        st.session_state["notif_focus_kategori"] = on_click_kategori
                        st.session_state["selected_region"] = None
                    else:
                        st.session_state["selected_region"] = sub
                        st.session_state["notif_focus_kategori"] = None
                    st.rerun()


def section_title(text):
    st.markdown(
        f"<div style='display:inline-block; background:#EAF4FC; color:#0B1E3D; "
        f"font-weight:800; font-size:0.95rem; padding:6px 14px; border-radius:6px; "
        f"margin-bottom:10px;'>{text}</div>",
        unsafe_allow_html=True,
    )


def hex_to_rgba(hex_color, alpha=0.1):
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def notif_card(row):
    color = CATEGORY_COLORS[row["Kategori_Prioritas"]]
    st.markdown(f"""
    <div style="background:#FAFCFE; border:1px solid #E1EBF5; border-left:4px solid {color};
                border-radius:8px; padding:10px 12px; margin-bottom:8px;">
        <div style="font-size:0.78rem; font-weight:700; color:{color};">
            PRIORITAS {row['Kategori_Prioritas'].upper()} — {row['Kabupaten/Kota']}
        </div>
        <div style="font-size:0.74rem; color:#5B6B82; margin-top:3px;">
            Indikator dominan: {row['Indikator_Dominan_1']} + {row['Indikator_Dominan_2']}
        </div>
        <div style="font-size:0.74rem; color:#0B1E3D; margin-top:3px;">
            {row['Rekomendasi']}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render():
    df = load_recommendation_data()

    if "filter_kategori" not in st.session_state:
        st.session_state["filter_kategori"] = list(CATEGORY_ORDER)
    if "filter_search" not in st.session_state:
        st.session_state["filter_search"] = ""
    if "selected_region" not in st.session_state:
        st.session_state["selected_region"] = None
    if "notif_focus_kategori" not in st.session_state:
        st.session_state["notif_focus_kategori"] = None

    # ================= HEADER (full width, tanpa box tahun) =================
    st.markdown(
        "<div style='font-size:2.2rem;font-weight:800;color:#0B1E3D;line-height:1.1;'>"
        "BANTUAN SOSIAL JAWA TIMUR 2025</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='font-size:0.95rem;color:#5B6B82;margin-top:2px;margin-bottom:14px;'>"
        "Sistem Pendukung Keputusan Bantuan Sosial Provinsi Jawa Timur</div>",
        unsafe_allow_html=True,
    )

    # ================= FILTER BAR (tanpa Pilih Tahun) =================
    with st.container(border=True):
        f1, f2, f3 = st.columns([2, 2, 0.8])

        with f1:
            kategori_pilih = st.multiselect(
                "Kategori Prioritas",
                options=CATEGORY_ORDER,
                default=st.session_state["filter_kategori"],
            )
            st.session_state["filter_kategori"] = kategori_pilih if kategori_pilih else list(CATEGORY_ORDER)

        with f2:
            search = st.text_input(
                "Cari Kabupaten/Kota",
                value=st.session_state["filter_search"],
                placeholder="contoh: Bangkalan",
            )
            st.session_state["filter_search"] = search

        with f3:
            st.write("")
            if st.button("Reset Filter", use_container_width=True):
                st.session_state["filter_kategori"] = list(CATEGORY_ORDER)
                st.session_state["filter_search"] = ""
                st.session_state["selected_region"] = None
                st.session_state["notif_focus_kategori"] = None
                st.rerun()

    st.write("")
    st.caption(
        f"Menampilkan filter: {len(st.session_state['filter_kategori'])} kategori dipilih"
        + (f' · pencarian: "{st.session_state["filter_search"]}"' if st.session_state["filter_search"] else "")
    )
    st.write("")

    # ================= KPI CARDS =================
    counts = df["Kategori_Prioritas"].value_counts()
    total = len(df)
    top1 = df.sort_values("Ranking").iloc[0]

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    kpi_card(k1, "Total Kab/Kota", total, "#0B1E3D", sub="Jawa Timur")
    for col, kategori in zip([k2, k3, k4, k5], CATEGORY_ORDER):
        jumlah = int(counts.get(kategori, 0))
        kpi_card(
            col, kategori, jumlah, CATEGORY_COLORS[kategori],
            key=f"kpi_btn_{kategori}", button_label="Lihat",
            on_click_kategori=kategori,
        )
    kpi_card(
        k6, "Prioritas Tertinggi", f"{top1['Priority_Score']:.4f}", "#0B1E3D",
        sub=top1["Kabupaten/Kota"], key="kpi_btn_top1", button_label="Lihat Detail",
    )

    st.markdown("<hr style='margin:20px 0; border-color:#E1EBF5;'>", unsafe_allow_html=True)

    # ================= DATA TERFILTER =================
    df_filtered = df[df["Kategori_Prioritas"].isin(st.session_state["filter_kategori"])]
    if st.session_state["filter_search"]:
        df_filtered = df_filtered[
            df_filtered["Kabupaten/Kota"].str.contains(st.session_state["filter_search"], case=False)
        ]

    if set(st.session_state["filter_kategori"]) != set(CATEGORY_ORDER):
        st.warning(
            f"⚠️ Filter aktif — hanya menampilkan kategori: **{', '.join(st.session_state['filter_kategori'])}**. "
            f"Klik 'Reset Filter' untuk menampilkan semua kategori."
        )

    # ================= PETA + DISTRIBUSI + NOTIFIKASI — HORIZONTAL =================
    col_map, col_side = st.columns([1.7, 1])

    with col_map:
        with st.container(border=True):
            section_title("PETA DAERAH PRIORITAS JAWA TIMUR TAHUN 2025")

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
                textfont=dict(size=8, color="#0B1E3D", family="Arial Black"),
                showlegend=False, hoverinfo="skip",
            ))

            fig.update_layout(
                geo2=dict(
                    scope="asia", projection_type="mercator",
                    showland=True, landcolor="#E5EDF5",
                    showcountries=True, countrycolor="#B8C4D9",
                    showocean=True, oceancolor="#DCEEFB",
                    lataxis_range=[-11, 8], lonaxis_range=[94, 142],
                    domain=dict(x=[0.0, 0.22], y=[0.66, 1.0]),
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
                margin=dict(t=0, b=0, l=0, r=0), height=500,
                legend=dict(title="Kategori Prioritas", orientation="h", y=-0.02),
            )

            map_event = st.plotly_chart(
                fig, use_container_width=True, on_select="rerun", key="map_chart"
            )
            try:
                points = map_event["selection"]["points"]
            except Exception:
                points = []
            if points:
                lokasi = points[0].get("location")
                if lokasi:
                    st.session_state["selected_region"] = lokasi
                    st.session_state["notif_focus_kategori"] = None
                    st.rerun()

            st.caption("Klik wilayah pada peta untuk melihat detail di panel Notifikasi.")

    with col_side:
        with st.container(border=True):
            section_title("DISTRIBUSI KATEGORI")
            dist_counts = df_filtered["Kategori_Prioritas"].value_counts().reindex(CATEGORY_ORDER).fillna(0)
            dist_df = dist_counts.reset_index()
            dist_df.columns = ["Kategori", "Jumlah"]
            fig2 = px.pie(
                dist_df, names="Kategori", values="Jumlah", color="Kategori",
                color_discrete_map=CATEGORY_COLORS, hole=0.55,
            )
            fig2.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=200, showlegend=True,
                              legend=dict(font=dict(size=10)))
            st.plotly_chart(fig2, use_container_width=True)

        with st.container(border=True):
            section_title("NOTIFIKASI & REKOMENDASI")

            if st.session_state["selected_region"]:
                rows = df[df["Kabupaten/Kota"] == st.session_state["selected_region"]]
            elif st.session_state["notif_focus_kategori"]:
                rows = df[df["Kategori_Prioritas"] == st.session_state["notif_focus_kategori"]].sort_values("Ranking")
            else:
                rows = df.sort_values("Ranking").head(3)

            for _, row in rows.iterrows():
                notif_card(row)

    st.markdown("<hr style='margin:20px 0; border-color:#E1EBF5;'>", unsafe_allow_html=True)

    # ================= TREN + K-MEANS — 2 KOLOM LEBIH LEBAR =================
    col_tren, col_cluster = st.columns([1, 1])

    with col_tren:
        with st.container(border=True):
            section_title("TREN RATA-RATA INDIKATOR (2019-2025)")
            hist = load_historical_data()
            tren = hist.groupby("Tahun")[["Kemiskinan", "IPM", "TPT", "Pertumbuhan Ekonomi"]].mean().reset_index()
            fig3 = px.line(
                tren, x="Tahun", y=["Kemiskinan", "IPM", "TPT", "Pertumbuhan Ekonomi"],
                markers=True,
            )
            fig3.update_xaxes(dtick=1)
            fig3.update_layout(
                margin=dict(t=10, b=0, l=0, r=0), height=320,
                legend=dict(title=None, orientation="h", y=-0.18, font=dict(size=10)),
                xaxis_title=None, yaxis_title=None,
            )
            st.plotly_chart(fig3, use_container_width=True)
            st.caption("Rata-rata 38 Kabupaten/Kota per tahun · 4 kriteria TOPSIS")

    with col_cluster:
        with st.container(border=True):
            section_title("HASIL KLASTER K-MEANS")
            cl = load_clustering_data()
            fitur = ["Kemiskinan", "IPM", "TPT", "TPAK", "RLS", "HLS", "Pertumbuhan Ekonomi"]
            pca = PCA(n_components=2)
            komponen = pca.fit_transform(cl[fitur])
            cl_plot = cl.copy()
            cl_plot["PC1"] = komponen[:, 0]
            cl_plot["PC2"] = komponen[:, 1]
            cl_plot["Cluster"] = cl_plot["Cluster"].astype(str)

            warna_cluster = {"0": "#3B82F6", "1": "#F4A261"}

            fig4 = go.Figure()

            # Garis pembatas (convex hull) mengelilingi tiap cluster
            for label, warna in warna_cluster.items():
                subset = cl_plot[cl_plot["Cluster"] == label][["PC1", "PC2"]].values
                if len(subset) >= 3:
                    hull = ConvexHull(subset)
                    hull_pts = subset[hull.vertices]
                    hull_pts = np.vstack([hull_pts, hull_pts[0]])
                    fig4.add_trace(go.Scatter(
                        x=hull_pts[:, 0], y=hull_pts[:, 1],
                        mode="lines", fill="toself",
                        fillcolor=hex_to_rgba(warna, 0.1),
                        line=dict(color=warna, width=1.5),
                        showlegend=False, hoverinfo="skip",
                    ))

            # Titik-titik daerah
            for label, warna in warna_cluster.items():
                subset = cl_plot[cl_plot["Cluster"] == label]
                fig4.add_trace(go.Scatter(
                    x=subset["PC1"], y=subset["PC2"], mode="markers",
                    marker=dict(color=warna, size=8, line=dict(color="white", width=1)),
                    name=f"Cluster {label}",
                    text=subset["Kabupaten/Kota"],
                    hovertemplate="%{text}<extra></extra>",
                ))

            fig4.update_layout(
                margin=dict(t=10, b=0, l=0, r=0), height=320,
                xaxis_title="PC1", yaxis_title="PC2",
                legend=dict(title="Cluster", orientation="h", y=-0.18, font=dict(size=10)),
            )
            st.plotly_chart(fig4, use_container_width=True)
            st.caption(f"K-Means (k=2) · PCA 2 komponen untuk visualisasi · "
                      f"Cluster 0: {(cl['Cluster']==0).sum()} daerah, Cluster 1: {(cl['Cluster']==1).sum()} daerah")

    st.markdown("<hr style='margin:20px 0; border-color:#E1EBF5;'>", unsafe_allow_html=True)

    # ================= RANKING — FULL WIDTH + SCROLL (tidak diubah) =================
    with st.container(border=True):
        section_title("RANKING PRIORITAS BANTUAN SOSIAL TAHUN 2025")

        tabel_ranking = df.sort_values("Ranking")[
            ["Ranking", "Kabupaten/Kota", "Priority_Score", "Kategori_Prioritas",
             "Indikator_Dominan", "Rekomendasi"]
        ].rename(columns={
            "Priority_Score": "Skor Prioritas",
            "Kategori_Prioritas": "Kategori",
            "Indikator_Dominan": "Indikator Dominan (Top 2)",
        })

        st.dataframe(
            tabel_ranking,
            use_container_width=True,
            hide_index=True,
            height=380,
            column_config={
                "Ranking": st.column_config.NumberColumn(width="small"),
                "Skor Prioritas": st.column_config.NumberColumn(format="%.4f", width="small"),
                "Kategori": st.column_config.TextColumn(width="small"),
            },
        )
        st.caption(f"Menampilkan {len(tabel_ranking)} dari 38 Kabupaten/Kota · Scroll untuk melihat semua.")