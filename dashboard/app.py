import streamlit as st

st.set_page_config(
    page_title="SPK Prioritas Bansos Jawa Timur",
    page_icon="🗺️",
    layout="wide",
)

st.markdown("""
<style>
/* ===== Background halaman utama: PUTIH dominan ===== */
.stApp {
    background-color: #FFFFFF;
}

/* ===== Sidebar container: navy blue ===== */
section[data-testid="stSidebar"] {
    background-color: #0B1E3D;
    border-right: 1px solid #142A52;
}

section[data-testid="stSidebar"] h1 {
    font-size: 1.15rem;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: 0.02em;
}
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: #93A5C9;
}

/* Sembunyikan lingkaran radio bawaan */
section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
    display: none;
}

/* Card/button menu */
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    display: flex;
    align-items: center;
    width: 100%;
    padding: 14px 16px;
    margin-bottom: 8px;
    border-radius: 10px;
    background-color: #102A52;
    border: 1px solid #1C3A66;
    transition: all 0.15s ease;
    cursor: pointer;
}

/* Teks menu -> putih bold besar */
section[data-testid="stSidebar"] div[role="radiogroup"] label p {
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.02em;
    margin: 0;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background-color: #14356B;
    border-color: #2E5C9E;
}

/* Menu aktif: background biru muda, teks HITAM */
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background-color: #7EC1F5;
    border: 1px solid #5EA0F5;
    box-shadow: 0 0 10px rgba(94, 160, 245, 0.35);
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
    color: #0B1E3D !important;
    font-weight: 800 !important;
}
</style>
""", unsafe_allow_html=True)

if "selected_region" not in st.session_state:
    st.session_state["selected_region"] = None

st.sidebar.title("SPK PRIORITAS BANSOS")
st.sidebar.caption("38 Kabupaten/Kota Jawa Timur · Snapshot 2025")
st.sidebar.divider()

PAGES = {
    "OVERVIEW": "overview",
    "PETA PRIORITAS": "peta",
    "RANKING": "ranking",
    "DETAIL DAERAH": "detail",
    "ANALISIS ML (K-MEANS)": "machine_learning",
    "INDIKATOR DOMINAN": "indikator_dominan",
    "REKOMENDASI": "recommendation",
    "DATASET": "dataset",
}

pilihan = st.sidebar.radio("Navigasi", list(PAGES.keys()), label_visibility="collapsed")
modul = PAGES[pilihan]

if modul == "overview":
    import overview
    overview.render()
elif modul == "peta":
    import peta
    peta.render()
elif modul == "ranking":
    import ranking
    ranking.render()
elif modul == "detail":
    import detail
    detail.render()
elif modul == "machine_learning":
    import machine_learning
    machine_learning.render()
elif modul == "indikator_dominan":
    import indikator_dominan
    indikator_dominan.render()
elif modul == "recommendation":
    import recommendation
    recommendation.render()
elif modul == "dataset":
    import dataset
    dataset.render()