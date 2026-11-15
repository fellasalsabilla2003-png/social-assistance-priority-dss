import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy.spatial import ConvexHull
from sklearn.decomposition import PCA
from utils import load_clustering_data


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


def render():
    st.markdown(
        "<div style='font-size:2rem;font-weight:800;color:#0B1E3D;line-height:1.1;'>"
        "ANALISIS ML (K-MEANS)</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='font-size:0.92rem;color:#5B6B82;margin-top:2px;margin-bottom:14px;'>"
        "Pengelompokan 38 Kabupaten/Kota berdasarkan kemiripan karakteristik sosial ekonomi (unsupervised learning)</div>",
        unsafe_allow_html=True,
    )

    cl = load_clustering_data()
    fitur = ["Kemiskinan", "IPM", "TPT", "TPAK", "RLS", "HLS", "Pertumbuhan Ekonomi"]

    # ================= METODOLOGI =================
    with st.container(border=True):
        section_title("METODOLOGI")
        st.markdown("""
        - **Metode:** K-Means Clustering (unsupervised) — mengidentifikasi pola/karakteristik, **bukan** prediksi (tidak ada target/label).
        - **Variabel input (7 indikator):** Kemiskinan, IPM, TPT, TPAK, RLS, HLS, Pertumbuhan Ekonomi.
        - **Preprocessing:** Standardisasi (StandardScaler) sebelum clustering, karena skala antar-variabel berbeda jauh.
        - **Penentuan jumlah cluster (k):** Elbow Method + Silhouette Score, k final = **2**.
        """)

    st.write("")

    # ================= ELBOW + SILHOUETTE (gambar hasil eksplorasi k) =================
    col_elbow, col_sil = st.columns(2)
    with col_elbow:
        with st.container(border=True):
            section_title("ELBOW METHOD")
            try:
                st.image("models/elbow_plot.png", use_container_width=True)
            except Exception:
                st.warning("File models/elbow_plot.png tidak ditemukan.")
    with col_sil:
        with st.container(border=True):
            section_title("SILHOUETTE SCORE")
            try:
                st.image("models/silhouette_plot.png", use_container_width=True)
            except Exception:
                st.warning("File models/silhouette_plot.png tidak ditemukan.")

    st.write("")

    # ================= SCATTER PCA + PROFIL CLUSTER =================
    col_scatter, col_profil = st.columns([1.3, 1])

    with col_scatter:
        with st.container(border=True):
            section_title("VISUALISASI HASIL CLUSTER (PCA 2 KOMPONEN)")

            pca = PCA(n_components=2)
            komponen = pca.fit_transform(cl[fitur])
            cl_plot = cl.copy()
            cl_plot["PC1"] = komponen[:, 0]
            cl_plot["PC2"] = komponen[:, 1]
            cl_plot["Cluster"] = cl_plot["Cluster"].astype(str)

            warna_cluster = {"0": "#3B82F6", "1": "#F4A261"}
            fig = go.Figure()

            for label, warna in warna_cluster.items():
                subset = cl_plot[cl_plot["Cluster"] == label][["PC1", "PC2"]].values
                if len(subset) >= 3:
                    hull = ConvexHull(subset)
                    hull_pts = subset[hull.vertices]
                    hull_pts = np.vstack([hull_pts, hull_pts[0]])
                    fig.add_trace(go.Scatter(
                        x=hull_pts[:, 0], y=hull_pts[:, 1],
                        mode="lines", fill="toself",
                        fillcolor=hex_to_rgba(warna, 0.1),
                        line=dict(color=warna, width=1.5),
                        showlegend=False, hoverinfo="skip",
                    ))

            for label, warna in warna_cluster.items():
                subset = cl_plot[cl_plot["Cluster"] == label]
                fig.add_trace(go.Scatter(
                    x=subset["PC1"], y=subset["PC2"], mode="markers",
                    marker=dict(color=warna, size=9, line=dict(color="white", width=1)),
                    name=f"Cluster {label}",
                    text=subset["Kabupaten/Kota"],
                    hovertemplate="%{text}<extra></extra>",
                ))

            fig.update_layout(
                margin=dict(t=10, b=0, l=0, r=0), height=420,
                xaxis_title="Komponen Utama 1 (PC1)", yaxis_title="Komponen Utama 2 (PC2)",
                legend=dict(title="Cluster", orientation="h", y=-0.15),
            )
            st.plotly_chart(fig, use_container_width=True)
            var_explained = pca.explained_variance_ratio_.sum() * 100
            st.caption(
                f"PCA mereduksi 7 dimensi menjadi 2 komponen (menjelaskan {var_explained:.1f}% variansi data) "
                f"khusus untuk keperluan visualisasi — proses clustering asli tetap menggunakan 7 dimensi penuh."
            )

    with col_profil:
        with st.container(border=True):
            section_title("PROFIL RATA-RATA PER CLUSTER")
            profil = cl.groupby("Cluster")[fitur].mean().round(2)
            profil.index = [f"Cluster {i}" for i in profil.index]
            st.dataframe(profil.T, use_container_width=True)
            st.caption(
                f"Cluster 0: {(cl['Cluster']==0).sum()} daerah · "
                f"Cluster 1: {(cl['Cluster']==1).sum()} daerah"
            )

    st.write("")

    # ================= DAFTAR ANGGOTA PER CLUSTER (collapsible) =================
    with st.container(border=True):
        section_title("DAFTAR ANGGOTA PER CLUSTER")
        for c in sorted(cl["Cluster"].unique()):
            anggota = cl[cl["Cluster"] == c].sort_values("Kabupaten/Kota")["Kabupaten/Kota"].tolist()
            with st.expander(f"Cluster {c} ({len(anggota)} daerah)"):
                st.write(", ".join(anggota))