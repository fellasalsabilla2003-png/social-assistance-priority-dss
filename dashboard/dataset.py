import streamlit as st
from utils import load_historical_data


def section_title(text):
    st.markdown(
        f"<div style='display:inline-block; background:#EAF4FC; color:#0B1E3D; "
        f"font-weight:800; font-size:0.95rem; padding:6px 14px; border-radius:6px; "
        f"margin-bottom:10px;'>{text}</div>",
        unsafe_allow_html=True,
    )


def render():
    df = load_historical_data()

    # ================= HEADER =================
    st.markdown(
        "<div style='font-size:2rem;font-weight:800;color:#0B1E3D;line-height:1.1;'>"
        "DATASET</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='font-size:0.92rem;color:#5B6B82;margin-top:2px;margin-bottom:14px;'>"
        "Data sosial ekonomi BPS 38 Kabupaten/Kota Jawa Timur, periode 2019-2025 (data mentah, tidak diubah)</div>",
        unsafe_allow_html=True,
    )

    # ================= INFO JUMLAH DATA =================
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.metric("Jumlah Baris", len(df))
    with c2:
        with st.container(border=True):
            st.metric("Jumlah Kolom", len(df.columns))
    with c3:
        with st.container(border=True):
            st.metric("Rentang Tahun", f"{df['Tahun'].min()}-{df['Tahun'].max()}")

    st.write("")

    # ================= FILTER =================
    with st.container(border=True):
        f1, f2, f3 = st.columns([1, 2, 0.8])

        with f1:
            tahun_pilih = st.multiselect(
                "Filter Tahun",
                options=sorted(df["Tahun"].unique()),
                default=sorted(df["Tahun"].unique()),
                key="dataset_filter_tahun",
            )

        with f2:
            search = st.text_input(
                "Cari Kabupaten/Kota", placeholder="contoh: Bangkalan", key="dataset_search",
            )

        with f3:
            st.write("")
            if st.button("Reset Filter", use_container_width=True, key="dataset_reset"):
                st.rerun()

    df_filtered = df[df["Tahun"].isin(tahun_pilih if tahun_pilih else df["Tahun"].unique())]
    if search:
        df_filtered = df_filtered[df_filtered["Kabupaten/Kota"].str.contains(search, case=False)]

    st.write("")

    # ================= TABEL DATASET =================
    with st.container(border=True):
        section_title(f"TABEL DATASET ({len(df_filtered)} baris)")

        df_display = df_filtered.sort_values(["Tahun", "Kabupaten/Kota"])
        st.dataframe(
            df_display, use_container_width=True, hide_index=True, height=450,
            column_config={
                "Kemiskinan": st.column_config.NumberColumn(format="%.2f"),
                "IPM": st.column_config.NumberColumn(format="%.2f"),
                "TPT": st.column_config.NumberColumn(format="%.2f"),
                "TPAK": st.column_config.NumberColumn(format="%.2f"),
                "RLS": st.column_config.NumberColumn(format="%.2f"),
                "HLS": st.column_config.NumberColumn(format="%.2f"),
                "Jumlah Penduduk": st.column_config.NumberColumn(format="%.1f"),
                "Pertumbuhan Ekonomi": st.column_config.NumberColumn(format="%.2f"),
            },
        )

        csv = df_display.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV (data terfilter)", data=csv,
            file_name="dataset_bps_filtered.csv", mime="text/csv",
        )