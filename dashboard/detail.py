import streamlit as st
import plotly.express as px
from utils import (
    load_recommendation_data, load_historical_data,
    CATEGORY_ORDER, CATEGORY_COLORS, INDICATOR_DIRECTION, badge_html,
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

    if "selected_region" not in st.session_state or not st.session_state["selected_region"]:
        st.session_state["selected_region"] = df.sort_values("Ranking").iloc[0]["Kabupaten/Kota"]

    # ================= HEADER + PEMILIH DAERAH =================
    col_title, col_pilih = st.columns([3, 1.4])
    with col_title:
        st.markdown(
            "<div style='font-size:2rem;font-weight:800;color:#0B1E3D;line-height:1.1;'>"
            "DETAIL DAERAH</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='font-size:0.92rem;color:#5B6B82;margin-top:2px;'>"
            "Informasi lengkap satu Kabupaten/Kota — skor, indikator, rekomendasi, dan tren historis</div>",
            unsafe_allow_html=True,
        )
    with col_pilih:
        daftar_daerah = sorted(df["Kabupaten/Kota"].unique())
        idx_default = daftar_daerah.index(st.session_state["selected_region"])
        pilihan = st.selectbox("Pilih Kabupaten/Kota", options=daftar_daerah, index=idx_default, key="detail_selectbox")
        if pilihan != st.session_state["selected_region"]:
            st.session_state["selected_region"] = pilihan
            st.rerun()

    region = st.session_state["selected_region"]
    row = df[df["Kabupaten/Kota"] == region].iloc[0]
    color = CATEGORY_COLORS[row["Kategori_Prioritas"]]

    st.write("")

    # ================= HEADER STATUS DAERAH =================
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        with c1:
            st.markdown(f"<div style='font-size:1.5rem;font-weight:800;color:#0B1E3D;'>{region}</div>", unsafe_allow_html=True)
            st.markdown(badge_html(row["Kategori_Prioritas"]), unsafe_allow_html=True)
        c2.metric("Priority Score", f"{row['Priority_Score']:.4f}")
        c3.metric("Ranking", f"#{int(row['Ranking'])} / 38")
        c4.metric("Kategori", row["Kategori_Prioritas"])

    st.write("")

    # ================= 4 INDIKATOR TOPSIS + INFO TAMBAHAN =================
    col_topsis, col_tambahan = st.columns([1.4, 1])

    with col_topsis:
        with st.container(border=True):
            section_title("4 KRITERIA TOPSIS")
            hist = load_historical_data()
            row_2025 = hist[(hist["Kabupaten/Kota"] == region) & (hist["Tahun"] == 2025)]
            if len(row_2025) > 0:
                row_2025 = row_2025.iloc[0]
                cols = st.columns(4)
                for col, (indikator, arah) in zip(cols, INDICATOR_DIRECTION.items()):
                    with col:
                        with st.container(border=True):
                            st.markdown(
                                f"<div style='font-size:0.75rem;color:#5B6B82;text-transform:uppercase;'>{indikator}</div>",
                                unsafe_allow_html=True,
                            )
                            st.markdown(
                                f"<div style='font-size:1.3rem;font-weight:800;color:#0B1E3D;'>{row_2025[indikator]:.2f}</div>",
                                unsafe_allow_html=True,
                            )
                            simbol = "⬆️ Benefit" if arah == "Benefit" else "⬇️ Cost"
                            st.caption(simbol)
            else:
                st.info("Data 2025 untuk daerah ini tidak ditemukan.")

        with st.container(border=True):
            section_title("INDIKATOR DOMINAN")
            st.markdown(f"**{row['Indikator_Dominan']}**")
            st.caption(
                "Indikator dengan kontribusi tertinggi terhadap Priority Score daerah ini "
                "(bukan hubungan sebab-akibat, murni dekomposisi kontribusi TOPSIS)."
            )

        with st.container(border=True):
            section_title("REKOMENDASI SISTEM")
            st.info(row["Rekomendasi"])
            st.markdown(f"**Dasar Rekomendasi:**  \n{row['Dasar_Rekomendasi']}")

    with col_tambahan:
        with st.container(border=True):
            section_title("INFORMASI TAMBAHAN")
            row_info = hist[(hist["Kabupaten/Kota"] == region) & (hist["Tahun"] == 2025)]
            if len(row_info) > 0:
                row_info = row_info.iloc[0]
                info_items = [
                    ("Rata-rata Lama Sekolah (RLS)", f"{row_info['RLS']:.2f} tahun"),
                    ("Harapan Lama Sekolah (HLS)", f"{row_info['HLS']:.2f} tahun"),
                    ("Tingkat Partisipasi Angkatan Kerja (TPAK)", f"{row_info['TPAK']:.2f} %"),
                    ("Jumlah Penduduk", f"{row_info['Jumlah Penduduk']:.1f} ribu jiwa"),
                ]
                for label, value in info_items:
                    st.markdown(f"""
                    <div style="padding:8px 0; border-bottom:1px solid #EEF3F8;">
                        <div style="font-size:0.75rem; color:#5B6B82;">{label}</div>
                        <div style="font-size:1rem; font-weight:700; color:#0B1E3D;">{value}</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.caption("Informasi pendukung — bukan kriteria penghitung Priority Score TOPSIS.")

    st.write("")

    # ================= TREN HISTORIS 2019-2025 =================
    with st.container(border=True):
        section_title(f"TREN INDIKATOR {region.upper()} (2019-2025)")
        hist_region = hist[hist["Kabupaten/Kota"] == region].sort_values("Tahun")

        if len(hist_region) > 1:
            indikator_pilih = st.multiselect(
                "Pilih indikator untuk ditampilkan",
                options=["Kemiskinan", "IPM", "TPT", "Pertumbuhan Ekonomi", "RLS", "HLS", "TPAK"],
                default=["Kemiskinan", "IPM", "TPT", "Pertumbuhan Ekonomi"],
                key="detail_tren_indikator",
            )
            if indikator_pilih:
                fig = px.line(
                    hist_region, x="Tahun", y=indikator_pilih, markers=True,
                )
                fig.update_xaxes(dtick=1)
                fig.update_layout(
                    margin=dict(t=10, b=0, l=0, r=0), height=350,
                    legend=dict(title=None, orientation="h", y=-0.15),
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Pilih minimal 1 indikator untuk menampilkan grafik.")
        else:
            st.info("Data historis untuk daerah ini tidak cukup untuk membuat grafik tren.")