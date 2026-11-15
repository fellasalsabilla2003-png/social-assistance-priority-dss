import pandas as pd
from preprocessing import preprocess

INDICATOR_COLS = ["Kemiskinan", "IPM", "TPT", "TPAK", "RLS", "HLS",
                   "Jumlah Penduduk", "Pertumbuhan Ekonomi"]


def distribution_summary(df):
    """1. Distribusi tiap indikator (statistik deskriptif)."""
    print("=" * 60)
    print("1. DISTRIBUSI INDIKATOR")
    print("=" * 60)
    print(df[INDICATOR_COLS].describe().T)


def compare_regions(df, tahun=2025):
    """2. Perbandingan antardaerah pada tahun tertentu."""
    print("\n" + "=" * 60)
    print(f"2. PERBANDINGAN ANTARDAERAH (Tahun {tahun})")
    print("=" * 60)
    df_tahun = df[df["Tahun"] == tahun]
    print("\n5 daerah dengan Kemiskinan tertinggi:")
    print(df_tahun.nlargest(5, "Kemiskinan")[["Kabupaten/Kota", "Kemiskinan"]])
    print("\n5 daerah dengan IPM terendah:")
    print(df_tahun.nsmallest(5, "IPM")[["Kabupaten/Kota", "IPM"]])


def trend_over_years(df):
    """3. Tren rata-rata tiap indikator dari 2019-2025."""
    print("\n" + "=" * 60)
    print("3. TREN RATA-RATA PER TAHUN (seluruh Jatim)")
    print("=" * 60)
    trend = df.groupby("Tahun")[INDICATOR_COLS].mean()
    print(trend)


def correlation_matrix(df):
    """4. Korelasi antarindikator."""
    print("\n" + "=" * 60)
    print("4. MATRIKS KORELASI ANTARINDIKATOR")
    print("=" * 60)
    print(df[INDICATOR_COLS].corr().round(2))


def detect_outliers(df):
    """5. Deteksi outlier per indikator menggunakan metode IQR."""
    print("\n" + "=" * 60)
    print("5. DETEKSI OUTLIER (metode IQR)")
    print("=" * 60)
    for col in INDICATOR_COLS:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        outliers = df[(df[col] < lower) | (df[col] > upper)]
        if len(outliers) > 0:
            print(f"\n{col}: {len(outliers)} outlier ditemukan")
            print(outliers[["Tahun", "Kabupaten/Kota", col]].to_string(index=False))
        else:
            print(f"\n{col}: tidak ada outlier")


if __name__ == "__main__":
    df = preprocess()
    distribution_summary(df)
    compare_regions(df)
    trend_over_years(df)
    correlation_matrix(df)
    detect_outliers(df)