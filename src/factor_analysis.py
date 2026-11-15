import pandas as pd
from machine_learning import get_snapshot_2025
from priority_score import topsis, categorize_priority, compute_criteria_contribution, TOPSIS_COLS

INDICATOR_LABELS = {
    "Kemiskinan": "Tingkat Kemiskinan",
    "IPM": "Indeks Pembangunan Manusia (IPM)",
    "TPT": "Tingkat Pengangguran Terbuka (TPT)",
    "Pertumbuhan Ekonomi": "Pertumbuhan Ekonomi",
}


def identify_dominant_indicators(df, top_n=2):
    """
    Mengidentifikasi top-N indikator dengan kontribusi TOPSIS tertinggi per daerah.
    Disebut 'Indikator Dominan' - bukan 'faktor penyebab' - karena ini murni
    dekomposisi kontribusi matematis dari Priority Score, bukan klaim kausalitas.
    """
    df = df.copy()
    contrib_cols = [f"Kontribusi_{c}" for c in TOPSIS_COLS]

    def get_top_indicators(row):
        values = row[contrib_cols].astype(float)
        top = values.sort_values(ascending=False).head(top_n)
        result = []
        for col, val in top.items():
            original_col = col.replace("Kontribusi_", "")
            result.append(f"{INDICATOR_LABELS[original_col]} (kontribusi={val:.3f})")
        return "; ".join(result)

    def get_top_indicator_parts(row):
        """
        Versi terpisah (bukan string gabungan) dari top-2 indikator dominan,
        dipakai oleh recommendation.py untuk menyusun rule tanpa perlu
        parsing string 'Indikator_Dominan'. Nilai yang disimpan adalah
        nama kolom asli (misal 'IPM', 'TPT'), bukan label panjangnya,
        supaya bisa langsung dicocokkan ke TINDAKAN_MAP.
        """
        values = row[contrib_cols].astype(float)
        top = values.sort_values(ascending=False).head(top_n)
        names = [col.replace("Kontribusi_", "") for col in top.index]
        scores = [round(float(v), 3) for v in top.values]
        return pd.Series({
            "Indikator_Dominan_1": names[0],
            "Indikator_Dominan_1_Skor": scores[0],
            "Indikator_Dominan_2": names[1] if len(names) > 1 else None,
            "Indikator_Dominan_2_Skor": scores[1] if len(scores) > 1 else None,
        })

    df["Indikator_Dominan"] = df.apply(get_top_indicators, axis=1)
    df = pd.concat([df, df.apply(get_top_indicator_parts, axis=1)], axis=1)
    return df


if __name__ == "__main__":
    df_2025 = get_snapshot_2025()
    result = topsis(df_2025)
    result = categorize_priority(result)
    result = compute_criteria_contribution(result)
    result = identify_dominant_indicators(result)

    print("=" * 100)
    print("INDIKATOR DOMINAN PER DAERAH (10 Prioritas Tertinggi)")
    print("=" * 100)
    top10 = result.head(10)
    for _, row in top10.iterrows():
        print(f"\n{row['Ranking']}. {row['Kabupaten/Kota']} (Kategori: {row['Kategori_Prioritas']}, Skor: {row['Priority_Score']:.4f})")
        print(f"   Indikator dominan: {row['Indikator_Dominan']}")

    result.to_csv("../data/factor_analysis_2025.csv", index=False)
    print("\n\nHasil disimpan ke data/factor_analysis_2025.csv")