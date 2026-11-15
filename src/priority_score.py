import pandas as pd
import numpy as np
from machine_learning import get_snapshot_2025

# ============================================================
# DESAIN FINAL TOPSIS - DISEPAKATI, JANGAN DIUBAH TANPA PERSETUJUAN
# ============================================================
TOPSIS_COLS = ["Kemiskinan", "IPM", "TPT", "Pertumbuhan Ekonomi"]

WEIGHTS = {
    "Kemiskinan": 0.25,
    "IPM": 0.25,
    "TPT": 0.25,
    "Pertumbuhan Ekonomi": 0.25,
}

# True = Benefit (searah prioritas), False = Cost (berlawanan arah prioritas)
IS_BENEFIT = {
    "Kemiskinan": True,
    "IPM": False,
    "TPT": True,
    "Pertumbuhan Ekonomi": False,
}
# ============================================================


def topsis(df):
    """
    Menghitung Priority Score dengan metode TOPSIS.
    Dataset input TIDAK diubah (df.copy() dipakai) - fungsi ini murni
    menambahkan kolom baru, tidak memodifikasi data mentah.
    """
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "Total bobot harus 100%"

    df = df.copy()
    X = df[TOPSIS_COLS].values.astype(float)

    # 1. Normalisasi
    norm = np.sqrt((X ** 2).sum(axis=0))
    X_norm = X / norm

    # 2. Pembobotan
    weights = np.array([WEIGHTS[c] for c in TOPSIS_COLS])
    X_weighted = X_norm * weights

    # 3. Solusi ideal positif (A+) dan ideal negatif (A-)
    ideal_positive, ideal_negative = [], []
    for i, col in enumerate(TOPSIS_COLS):
        if IS_BENEFIT[col]:
            ideal_positive.append(X_weighted[:, i].max())
            ideal_negative.append(X_weighted[:, i].min())
        else:
            ideal_positive.append(X_weighted[:, i].min())
            ideal_negative.append(X_weighted[:, i].max())
    ideal_positive = np.array(ideal_positive)
    ideal_negative = np.array(ideal_negative)

    # 4. Jarak Euclidean ke solusi ideal
    dist_positive = np.sqrt(((X_weighted - ideal_positive) ** 2).sum(axis=1))
    dist_negative = np.sqrt(((X_weighted - ideal_negative) ** 2).sum(axis=1))

    # 5. Priority Score (closeness coefficient)
    denom = dist_positive + dist_negative
    priority_score = np.where(denom == 0, 0, dist_negative / denom)

    df["Priority_Score"] = priority_score
    df = df.sort_values(by="Priority_Score", ascending=False).reset_index(drop=True)
    df["Ranking"] = df.index + 1

    return df


def categorize_priority(df):
    """
    Mengelompokkan daerah ke kategori prioritas berdasarkan kuartil Priority Score.
    Q4 (skor tertinggi) = Sangat Tinggi, ..., Q1 (skor terendah) = Rendah.
    """
    df = df.copy()
    df["Kategori_Prioritas"] = pd.qcut(
        df["Priority_Score"],
        q=4,
        labels=["Rendah", "Sedang", "Tinggi", "Sangat Tinggi"]
    )
    return df


def validate_result(df_result):
    """Pengecekan validitas dasar hasil TOPSIS."""
    print("\n--- VALIDASI HASIL ---")
    print("Range Priority Score:", df_result["Priority_Score"].min(), "-", df_result["Priority_Score"].max())
    print("Jumlah daerah:", len(df_result))
    print("Ranking unik (harus 38):", df_result["Ranking"].nunique())
    print("Tidak ada nilai kosong:", df_result["Priority_Score"].isna().sum() == 0)


def show_category_summary(df):
    print("\n--- RINGKASAN KATEGORI PRIORITAS ---")
    summary = df.groupby("Kategori_Prioritas", observed=True).agg(
        Jumlah_Daerah=("Kabupaten/Kota", "count"),
        Skor_Min=("Priority_Score", "min"),
        Skor_Max=("Priority_Score", "max")
    )
    print(summary)


def compute_criteria_contribution(df):
    """
    Menghitung kontribusi tiap kriteria (indikator) TOPSIS terhadap Priority Score
    tiap daerah, menggunakan komponen (nilai terbobot & solusi ideal) yang SAMA
    PERSIS dengan yang dipakai dalam fungsi topsis(). Ini memastikan hasil
    analisis "Indikator Dominan" dapat ditelusuri langsung dari perhitungan
    Priority Score, bukan ukuran terpisah seperti z-score terhadap rata-rata.

    contribution_ij = |v_ij - A-_j| / (|v_ij - A+_j| + |v_ij - A-_j|)

    Nilai mendekati 1 berarti kriteria j menempatkan daerah i dekat dengan
    solusi ideal positif (kondisi kebutuhan prioritas tertinggi untuk kriteria itu).
    """
    df = df.copy()
    X = df[TOPSIS_COLS].values.astype(float)

    norm = np.sqrt((X ** 2).sum(axis=0))
    X_norm = X / norm
    weights = np.array([WEIGHTS[c] for c in TOPSIS_COLS])
    X_weighted = X_norm * weights

    ideal_positive, ideal_negative = [], []
    for i, col in enumerate(TOPSIS_COLS):
        if IS_BENEFIT[col]:
            ideal_positive.append(X_weighted[:, i].max())
            ideal_negative.append(X_weighted[:, i].min())
        else:
            ideal_positive.append(X_weighted[:, i].min())
            ideal_negative.append(X_weighted[:, i].max())
    ideal_positive = np.array(ideal_positive)
    ideal_negative = np.array(ideal_negative)

    for j, col in enumerate(TOPSIS_COLS):
        dist_pos = np.abs(X_weighted[:, j] - ideal_positive[j])
        dist_neg = np.abs(X_weighted[:, j] - ideal_negative[j])
        denom = dist_pos + dist_neg
        contribution = np.where(denom == 0, 0, dist_neg / denom)
        df[f"Kontribusi_{col}"] = contribution

    return df


if __name__ == "__main__":
    df_2025 = get_snapshot_2025()
    result = topsis(df_2025)
    result = categorize_priority(result)

    print("=" * 90)
    print("HASIL TOPSIS - PRIORITY SCORE, RANKING & KATEGORI (38 Kabupaten/Kota, 2025)")
    print("=" * 90)
    cols_show = ["Ranking", "Kabupaten/Kota", "Priority_Score", "Kategori_Prioritas"] + TOPSIS_COLS
    print(result[cols_show].to_string(index=False))

    validate_result(result)
    show_category_summary(result)

    result.to_csv("../data/priority_score_2025.csv", index=False)
    print("\nHasil disimpan ke data/priority_score_2025.csv")