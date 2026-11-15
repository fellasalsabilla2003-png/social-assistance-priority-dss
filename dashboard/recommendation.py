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

    if "selected_region" not in st.session_state:
        st.session_state["selected_region"] = None

    # ================= HEADER =================
    st.markdown(
        "<div style='font-size:2rem;font-weight:800;color:#0B1E3D;line-height:1.1;'>"
        "REKOMENDASI</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='font-size:0.92rem;color:#5B6B82;margin-top:2px;margin-bottom:14px;'>"
        "Rule-Based Recommendation — dihasilkan otomatis dari Kategori Prioritas + Indikator Dominan tiap daerah</div>",
        unsafe_allow_html=True,
    )

    # ================= RINGKASAN ALERT (Action Center) =================
    counts = df["Kategori_Prioritas"].value_counts()
    with st.container(border=True):
        section_title("RINGKASAN ALERT")
        cols = st.columns(4)
        for col, kategori in zip(cols, CATEGORY_ORDER):
            jumlah = int(counts.get(kategori, 0))
            color = CATEGORY_COLORS[kategori]
            with col:
                st.markdown(f"""
                <div style="border-left:4px solid {color}; padding-left:10px;">
                    <div style="font-size:0.78rem; color:#5B6B82; text-transform:uppercase;">{kategori}</div>
                    <div style="font-size:1.4rem; font-weight:800; color:#0B1E3D;">{jumlah} daerah</div>
                </div>
                """, unsafe_allow_html=True)

        top1 = df.sort_values("Ranking").iloc[0]
        st.write("")
        st.warning(
            f"🚨 Prioritas tertinggi saat ini: **{top1['Kabupaten/Kota']}** "
            f"(Skor {top1['Priority_Score']:.4f}, Ranking #{int(top1['Ranking'])}) — {top1['Rekomendasi']}"
        )

    st.write("")

    # ================= FILTER =================
    with st.container(border=True):
        f1, f2 = st.columns([2, 2])
        with f1:
            filter_kategori = st.multiselect(
                "Filter Kategori Prioritas", options=CATEGORY_ORDER,
                default=list(CATEGORY_ORDER), key="rekom_filter_kategori",
            )
        with f2:
            search = st.text_input(
                "Cari Kabupaten/Kota", placeholder="contoh: Bangkalan", key="rekom_search",
            )

    df_filtered = df[df["Kategori_Prioritas"].isin(filter_kategori if filter_kategori else CATEGORY_ORDER)]
    if search:
        df_filtered = df_filtered[df_filtered["Kabupaten/Kota"].str.contains(search, case=False)]
    df_filtered = df_filtered.sort_values("Ranking")

    st.write("")

    # ================= DAFTAR REKOMENDASI (card per daerah) =================
    with st.container(border=True):
        section_title(f"DAFTAR REKOMENDASI ({len(df_filtered)} DAERAH)")

        if len(df_filtered) == 0:
            st.info("Tidak ada daerah yang cocok dengan filter/pencarian saat ini.")
        else:
            for _, row in df_filtered.iterrows():
                color = CATEGORY_COLORS[row["Kategori_Prioritas"]]
                with st.container(border=True):
                    col_a, col_b = st.columns([1, 3])
                    with col_a:
                        st.markdown(f"""
                        <div style="font-size:1rem; font-weight:800; color:#0B1E3D;">
                            #{int(row['Ranking'])} &nbsp; {row['Kabupaten/Kota']}
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(badge_html(row["Kategori_Prioritas"]), unsafe_allow_html=True)
                        st.caption(f"Skor: {row['Priority_Score']:.4f}")
                    with col_b:
                        st.markdown(f"**Indikator Dominan:** {row['Indikator_Dominan']}")
                        st.markdown(f"**Rekomendasi:** {row['Rekomendasi']}")
                        st.caption(f"Dasar: {row['Dasar_Rekomendasi']}")

                    if st.button("Lihat Detail Daerah", key=f"rekom_detail_{row['Kabupaten/Kota']}"):
                        st.session_state["selected_region"] = row["Kabupaten/Kota"]
                        st.info(f"'{row['Kabupaten/Kota']}' terpilih. Buka menu 'Detail Daerah' di sidebar.")