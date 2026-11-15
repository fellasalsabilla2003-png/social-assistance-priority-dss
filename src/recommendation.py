import pandas as pd
from machine_learning import get_snapshot_2025
from priority_score import topsis, categorize_priority, compute_criteria_contribution, TOPSIS_COLS, IS_BENEFIT
from factor_analysis import identify_dominant_indicators, INDICATOR_LABELS

# ============================================================
# RULE-BASED RECOMMENDATION - DISEPAKATI, JANGAN DIUBAH TANPA PERSETUJUAN
#
# Rule dibangun murni dari hasil sistem yang sudah ada:
#   1. Kategori_Prioritas    -> menentukan URGENSI (framing)
#   2. Indikator_Dominan_1/2 -> menentukan TINDAKAN (domain program)
#   3. Outlier IQR pada 4 kriteria TOPSIS (snapshot 2025) -> ALERT
#
# Tidak ada nama Kabupaten/Kota yang di-hard-code di rule manapun.
# ============================================================

TINDAKAN_TUNGGAL = {
    "Kemiskinan": "intervensi sosial (bantuan langsung/subsidi)",
    "IPM": "program pendidikan & kesehatan dasar",
    "TPT": "program ketenagakerjaan/pelatihan kerja",
    "Pertumbuhan Ekonomi": "pemberdayaan ekonomi lokal/UMKM",
}

URGENSI_MAP = {
    "Sangat Tinggi": "Prioritaskan segera",
    "Tinggi": "Perlu perhatian dalam waktu dekat",
    "Sedang": "Pantau dan siapkan program pencegahan",
    "Rendah": "Pemantauan rutin, tidak mendesak",
}


def _tindakan_gabungan(indikator_1, indikator_2):
    """Menggabungkan domain tindakan dari top-2 indikator dominan, tanpa duplikat."""
    aksi_1 = TINDAKAN_TUNGGAL[indikator_1]
    if indikator_2 is None or pd.isna(indikator_2) or indikator_2 == indikator_1:
        return aksi_1.capitalize() + "."
    aksi_2 = TINDAKAN_TUNGGAL[indikator_2]
    return f"{aksi_1.capitalize()}, disertai {aksi_2}."


def generate_recommendation_row(row):
    """Menyusun REKOMENDASI dan DASAR REKOMENDASI untuk satu daerah."""
    kategori = row["Kategori_Prioritas"]
    ind1, skor1 = row["Indikator_Dominan_1"], row["Indikator_Dominan_1_Skor"]
    ind2, skor2 = row["Indikator_Dominan_2"], row["Indikator_Dominan_2_Skor"]

    urgensi = URGENSI_MAP[kategori]
    tindakan = _tindakan_gabungan(ind1, ind2)
    rekomendasi = f"{urgensi} — {tindakan}"

    if ind2 is not None and not pd.isna(ind2):
        dasar = (
            f"Kategori {kategori} (kuartil Priority Score TOPSIS) dengan indikator "
            f"dominan {ind1} dan {ind2} (kontribusi TOPSIS tertinggi: "
            f"{skor1:.3f} & {skor2:.3f})."
        )
    else:
        dasar = (
            f"Kategori {kategori} (kuartil Priority Score TOPSIS) dengan indikator "
            f"dominan {ind1} (kontribusi TOPSIS tertinggi: {skor1:.3f})."
        )

    return pd.Series({"Rekomendasi": rekomendasi, "Dasar_Rekomendasi": dasar})


def generate_recommendations(df):
    """Menambahkan kolom Rekomendasi & Dasar_Rekomendasi ke seluruh daerah."""
    df = df.copy()
    rec = df.apply(generate_recommendation_row, axis=1)
    return pd.concat([df, rec], axis=1)


def detect_extreme_outliers(df):
    """
    Deteksi outlier ekstrem pada 4 indikator TOPSIS, dihitung KHUSUS pada
    snapshot 2025 (38 daerah) - konsisten dengan unit analisis TOPSIS.
    Hanya sisi yang menandakan kondisi butuh perhatian yang dianggap alert
    (arah mengikuti definisi Benefit/Cost yang sudah disepakati).
    """
    df = df.copy()
    alert_flags = pd.DataFrame(index=df.index)

    for col in TOPSIS_COLS:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        if IS_BENEFIT[col]:
            alert_flags[col] = df[col] > upper
        else:
            alert_flags[col] = df[col] < lower

    df["Alert_Ekstrem"] = alert_flags.any(axis=1)
    df["Alert_Indikator"] = alert_flags.apply(
        lambda row: ", ".join([INDICATOR_LABELS[c] for c in TOPSIS_COLS if row[c]]),
        axis=1
    )
    return df


def generate_alert_summary(df):
    """Ringkasan alert berbasis hasil sistem, dipakai Notification/Action Center."""
    counts = df["Kategori_Prioritas"].value_counts()
    alerts = []
    for kategori in ["Sangat Tinggi", "Tinggi", "Sedang", "Rendah"]:
        jumlah = int(counts.get(kategori, 0))
        if jumlah > 0:
            alerts.append(f"{jumlah} Kabupaten/Kota berada pada kategori Prioritas {kategori}.")

    top1 = df.sort_values("Ranking").iloc[0]
    alerts.append(
        f"Prioritas tertinggi saat ini: {top1['Kabupaten/Kota']} "
        f"(Skor {top1['Priority_Score']:.4f}, Ranking #{int(top1['Ranking'])})."
    )

    ekstrem = df[df["Alert_Ekstrem"]]
    if len(ekstrem) > 0:
        nama_daerah = ", ".join(ekstrem["Kabupaten/Kota"].tolist())
        alerts.append(f"{len(ekstrem)} daerah terdeteksi kondisi ekstrem (outlier): {nama_daerah}.")

    return alerts


if __name__ == "__main__":
    df_2025 = get_snapshot_2025()
    result = topsis(df_2025)
    result = categorize_priority(result)
    result = compute_criteria_contribution(result)
    result = identify_dominant_indicators(result)
    result = generate_recommendations(result)
    result = detect_extreme_outliers(result)

    print("=" * 100)
    print("RULE-BASED RECOMMENDATION (10 Prioritas Tertinggi)")
    print("=" * 100)
    for _, row in result.head(10).iterrows():
        print(f"\n{row['Ranking']}. {row['Kabupaten/Kota']}")
        print(f"   STATUS            : {row['Kategori_Prioritas']}")
        print(f"   INDIKATOR DOMINAN : {row['Indikator_Dominan']}")
        print(f"   REKOMENDASI       : {row['Rekomendasi']}")
        print(f"   DASAR REKOMENDASI : {row['Dasar_Rekomendasi']}")
        if row["Alert_Ekstrem"]:
            print(f"   ALERT             : Kondisi ekstrem pada: {row['Alert_Indikator']}")

    print("\n" + "=" * 100)
    print("ALERT SUMMARY (untuk Notification/Action Center)")
    print("=" * 100)
    for alert in generate_alert_summary(result):
        print(f"- {alert}")

    result.to_csv("../data/recommendation_2025.csv", index=False)
    print("\n\nHasil disimpan ke data/recommendation_2025.csv")