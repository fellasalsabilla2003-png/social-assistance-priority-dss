import pandas as pd

df = pd.read_csv("../data/dataset_bps.csv")

# Buang baris yang seluruh kolomnya kosong (sisa dari export Excel)
df = df.dropna(how="all")

# Pastikan kolom Tahun kembali ke tipe integer
df["Tahun"] = df["Tahun"].astype(int)

print("Jumlah baris dan kolom:", df.shape)
print("\nNama kolom:")
print(df.columns.tolist())
print("\n5 baris pertama:")
print(df.head())
print("\nJumlah Kabupaten/Kota unik:", df["Kabupaten/Kota"].nunique())
print("Rentang tahun:", df["Tahun"].min(), "-", df["Tahun"].max())

print("\n--- Cek apakah masih ada nilai kosong ---")
print(df.isna().sum())