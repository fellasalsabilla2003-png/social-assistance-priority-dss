import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_recommendation_data, CATEGORY_ORDER, CATEGORY_COLORS, badge_html


def section_title(text):
    st.markdown(
        f"<div style='display:inline-block; background:#EAF4FC; color:#0B1E3D; "
        f"font-weight:800; font-size:0.95rem; padding:6px 14px; border-radius:6px; "
        f"margin-bottom:10px;'>{text}</div>",
        unsafe_allow_html=True,
    )


def render():
    df = load_recommendation_data()

    if "selected_region" not in st.session_state:
        st.session_state["selected_region"] = None

    # ================= HEADER =================
    st.markdown(
        "<div style='font-size:2rem;font-weight:800;color:#0B1E3D;line-height:1.1;'>"
        "INDIKATOR DOMINAN</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='font-size:0.92rem;color:#5B6B82;margin-top:2px;margin-bottom:14px;'>"
        "Indikator dengan kontribusi tertinggi terhadap Priority Score TOPSIS tiap daerah — "
        "bukan hubungan sebab-akibat, murni dekomposisi kontribusi matematis</div>",
        unsafe_allow_html=True,
    )

    # ================= RINGKASAN: SEBERAPA SERING TIAP INDIKATOR JADI DOMINAN =================
    with st.container(border=True):
        section_title("FREKUENSI INDIKATOR DOMINAN (SELURUH 38 DAERAH)")

        gabungan = df["Indikator_Dominan_1"].tolist() + df["Indikator_Dominan_2"].dropna().tolist()
        freq = pd.Series(gabungan).value_counts().reset_index()
        freq.columns = ["Indikator", "Jumlah Daerah"]

        col_chart, col_ket = st.columns([1.4, 1])
        with col_chart:
            fig = px.bar(
                freq, x="Indikator", y="Jumlah Daerah", color="Indikator",
                color_discrete_sequence=["#0B1E3D", "#3B82F6", "#5EA0F5", "#8FBFF7"],
                text="Jumlah Daerah",
            )
            fig.update_layout(
                margin=dict(t=10, b=0, l=0, r=0), height=320,
                showlegend=False, xaxis_title=None, yaxis_title="Jumlah Daerah",
            )
            st.plotly_chart(fig, use_container_width=True)
        with col_ket:
            st.markdown("**Klik salah satu bar di chart tidak tersedia langsung** — gunakan filter di bawah untuk melihat daftar daerahnya.")
            pilih_indikator = st.selectbox(
                "Lihat daerah dengan indikator dominan:",
                options=["Semua"] + freq["Indikator"].tolist(),
                key="filter_indikator_dominan",
            )

    st.write("")

    # ================= TABEL LENGKAP =================
    with st.container(border=True):
        section_title("TABEL INDIKATOR DOMINAN PER DAERAH")

        tabel = df[[
            "Ranking", "Kabupaten/Kota", "Priority_Score", "Kategori_Prioritas",
            "Indikator_Dominan_1", "Indikator_Dominan_1_Skor",
            "Indikator_Dominan_2", "Indikator_Dominan_2_Skor",
        ]].copy()

        if pilih_indikator != "Semua":
            tabel = tabel[
                (tabel["Indikator_Dominan_1"] == pilih_indikator) |
                (tabel["Indikator_Dominan_2"] == pilih_indikator)
            ]

        tabel = tabel.sort_values("Ranking").rename(columns={
            "Priority_Score": "Skor Prioritas",
            "Kategori_Prioritas": "Kategori",
            "Indikator_Dominan_1": "Dominan #1",
            "Indikator_Dominan_1_Skor": "Kontribusi #1",
            "Indikator_Dominan_2": "Dominan #2",
            "Indikator_Dominan_2_Skor": "Kontribusi #2",
        })

        st.dataframe(
            tabel, use_container_width=True, hide_index=True, height=420,
            column_config={
                "Skor Prioritas": st.column_config.NumberColumn(format="%.4f"),
                "Kontribusi #1": st.column_config.NumberColumn(format="%.3f"),
                "Kontribusi #2": st.column_config.NumberColumn(format="%.3f"),
            },
        )
        st.caption(f"Menampilkan {len(tabel)} dari 38 Kabupaten/Kota.")