import pandas as pd

def load_data(path="../data/dataset_bps.csv"):
    """Membaca dataset mentah dan membersihkan baris kosong sisa export Excel."""
    df = pd.read_csv(path)
    df = df.dropna(how="all")
    df["Tahun"] = df["Tahun"].astype(int)
    return df


def fix_population_unit(df):
    """
    Menstandardisasi satuan kolom 'Jumlah Penduduk'.

    Sumber data BPS mencatat kolom ini dalam satuan RIBUAN JIWA untuk
    tahun 2019-2024, tetapi dalam satuan JIWA PENUH untuk tahun 2025.
    Fungsi ini mengonversi data tahun 2025 ke satuan ribuan jiwa
    agar konsisten dengan tahun-tahun lainnya (dibagi 1000).
    """
    df = df.copy()
    mask_2025 = df["Tahun"] == 2025
    df.loc[mask_2025, "Jumlah Penduduk"] = df.loc[mask_2025, "Jumlah Penduduk"] / 1000
    return df


def check_data_quality(df):
    """Menampilkan ringkasan kualitas data untuk verifikasi."""
    print("Shape:", df.shape)
    print("\nMissing value per kolom:")
    print(df.isna().sum())
    print("\nDuplikat (Kabupaten/Kota + Tahun):", df.duplicated(subset=["Kabupaten/Kota", "Tahun"]).sum())
    print("\nJumlah Kabupaten/Kota unik:", df["Kabupaten/Kota"].nunique())
    print("Rentang tahun:", df["Tahun"].min(), "-", df["Tahun"].max())


def preprocess(path="../data/dataset_bps.csv"):
    """Pipeline preprocessing utama: load -> bersihkan -> standardisasi -> data siap pakai."""
    df = load_data(path)
    df = fix_population_unit(df)
    df = df.sort_values(by=["Kabupaten/Kota", "Tahun"]).reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = preprocess()
    check_data_quality(df)
    print("\nCek konsistensi Jumlah Penduduk per tahun (rata-rata):")
    print(df.groupby("Tahun")["Jumlah Penduduk"].mean())
    print("\n5 baris pertama data bersih:")
    print(df.head())

    df.to_csv("../data/dataset_bps_clean.csv", index=False)
    print("\nData bersih (panel 2019-2025) disimpan ke data/dataset_bps_clean.csv")