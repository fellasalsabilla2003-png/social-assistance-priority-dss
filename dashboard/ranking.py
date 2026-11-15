import streamlit as st
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

    if "filter_kategori" not in st.session_state:
        st.session_state["filter_kategori"] = list(CATEGORY_ORDER)
    if "filter_search" not in st.session_state:
        st.session_state["filter_search"] = ""
    if "selected_region" not in st.session_state:
        st.session_state["selected_region"] = None

    # ================= HEADER =================
    st.markdown(
        "<div style='font-size:2rem;font-weight:800;color:#0B1E3D;line-height:1.1;'>"
        "RANKING</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='font-size:0.92rem;color:#5B6B82;margin-top:2px;margin-bottom:14px;'>"
        "Ranking prioritas bantuan sosial seluruh 38 Kabupaten/Kota Jawa Timur — Tahun 2025 (hasil TOPSIS)</div>",
        unsafe_allow_html=True,
    )

    # ================= FILTER BAR =================
    with st.container(border=True):
        f1, f2, f3, f4 = st.columns([1.6, 1.6, 1.2, 0.8])

        with f1:
            kategori_pilih = st.multiselect(
                "Kategori Prioritas", options=CATEGORY_ORDER,
                default=st.session_state["filter_kategori"], key="ranking_filter_kategori_widget",
            )
            st.session_state["filter_kategori"] = kategori_pilih if kategori_pilih else list(CATEGORY_ORDER)

        with f2:
            search = st.text_input(
                "Cari Kabupaten/Kota", value=st.session_state["filter_search"],
                placeholder="contoh: Bangkalan", key="ranking_search_widget",
            )
            st.session_state["filter_search"] = search

        with f3:
            urut_berdasarkan = st.selectbox(
                "Urutkan berdasarkan",
                options=["Ranking (Terbaik)", "Priority Score (Tertinggi)", "Nama A-Z"],
                key="ranking_sort_widget",
            )

        with f4:
            st.write("")
            if st.button("Reset Filter", use_container_width=True, key="ranking_reset_btn"):
                st.session_state["filter_kategori"] = list(CATEGORY_ORDER)
                st.session_state["filter_search"] = ""
                st.rerun()

    # ================= DATA TERFILTER + SORTING =================
    df_filtered = df[df["Kategori_Prioritas"].isin(st.session_state["filter_kategori"])]
    if st.session_state["filter_search"]:
        df_filtered = df_filtered[
            df_filtered["Kabupaten/Kota"].str.contains(st.session_state["filter_search"], case=False)
        ]

    if urut_berdasarkan == "Ranking (Terbaik)":
        df_filtered = df_filtered.sort_values("Ranking")
    elif urut_berdasarkan == "Priority Score (Tertinggi)":
        df_filtered = df_filtered.sort_values("Priority_Score", ascending=False)
    else:
        df_filtered = df_filtered.sort_values("Kabupaten/Kota")

    st.write("")
    st.caption(f"Menampilkan {len(df_filtered)} dari 38 Kabupaten/Kota.")

    # ================= TABEL RANKING (card per baris, agar bisa diklik) =================
    with st.container(border=True):
        section_title("DAFTAR PRIORITAS BANTUAN SOSIAL")

        if len(df_filtered) == 0:
            st.info("Tidak ada daerah yang cocok dengan filter/pencarian saat ini.")
        else:
            for _, row in df_filtered.iterrows():
                color = CATEGORY_COLORS[row["Kategori_Prioritas"]]
                col_info, col_rekom, col_btn = st.columns([1.6, 2.2, 0.7])

                with col_info:
                    st.markdown(f"""
                    <div style="border-left:5px solid {color}; padding-left:10px;">
                        <span style="font-size:0.95rem; font-weight:800; color:#0B1E3D;">
                            #{int(row['Ranking'])} &nbsp; {row['Kabupaten/Kota']}
                        </span><br>
                        <span style="font-size:0.78rem; color:#5B6B82;">
                            Skor: {row['Priority_Score']:.4f} &nbsp;·&nbsp;
                        </span>
                        {badge_html(row['Kategori_Prioritas'])}
                        <div style="font-size:0.75rem; color:#5B6B82; margin-top:4px;">
                            Indikator Dominan: {row['Indikator_Dominan']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col_rekom:
                    st.markdown(
                        f"<div style='font-size:0.78rem; color:#0B1E3D; padding-top:4px;'>{row['Rekomendasi']}</div>",
                        unsafe_allow_html=True,
                    )

                with col_btn:
                    if st.button("Detail", key=f"ranking_detail_{row['Kabupaten/Kota']}", use_container_width=True):
                        st.session_state["selected_region"] = row["Kabupaten/Kota"]
                        st.info(f"'{row['Kabupaten/Kota']}' terpilih. Buka menu 'Detail Daerah' di sidebar.")

                st.markdown("<hr style='margin:8px 0; border-color:#EEF3F8;'>", unsafe_allow_html=True)