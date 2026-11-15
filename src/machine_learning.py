import pandas as pd
import matplotlib
matplotlib.use("Agg")  # supaya bisa simpan grafik tanpa perlu tampilan interaktif
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from preprocessing import preprocess

FEATURE_COLS = ["Kemiskinan", "IPM", "TPT", "TPAK", "RLS", "HLS", "Pertumbuhan Ekonomi"]


def get_snapshot_2025():
    """Ambil data snapshot tahun 2025 (38 Kabupaten/Kota) sebagai unit analisis."""
    df = preprocess()
    df_2025 = df[df["Tahun"] == 2025].reset_index(drop=True)
    return df_2025


def explore_optimal_k(df, max_k=10):
    """Eksplorasi jumlah cluster optimal menggunakan Elbow Method dan Silhouette Score."""
    X = df[FEATURE_COLS]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    inertia_list = []
    silhouette_list = []
    k_range = range(2, max_k + 1)

    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        inertia_list.append(km.inertia_)
        sil = silhouette_score(X_scaled, labels)
        silhouette_list.append(sil)
        print(f"k={k} | inertia={km.inertia_:.2f} | silhouette_score={sil:.4f}")

    # Simpan grafik Elbow
    plt.figure(figsize=(6, 4))
    plt.plot(list(k_range), inertia_list, marker="o")
    plt.xlabel("Jumlah Cluster (k)")
    plt.ylabel("Inertia")
    plt.title("Elbow Method")
    plt.savefig("../models/elbow_plot.png")
    plt.close()

    # Simpan grafik Silhouette
    plt.figure(figsize=(6, 4))
    plt.plot(list(k_range), silhouette_list, marker="o", color="orange")
    plt.xlabel("Jumlah Cluster (k)")
    plt.ylabel("Silhouette Score")
    plt.title("Silhouette Score per k")
    plt.savefig("../models/silhouette_plot.png")
    plt.close()

    best_k = list(k_range)[silhouette_list.index(max(silhouette_list))]
    print(f"\nRekomendasi k dengan Silhouette Score tertinggi: k={best_k} (score={max(silhouette_list):.4f})")
    return best_k

import joblib

FINAL_K = 2


def run_final_clustering(df, k=FINAL_K):
    """Menjalankan K-Means final dan mengembalikan dataframe dengan label cluster."""
    X = df[FEATURE_COLS]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    df_result = df.copy()
    df_result["Cluster"] = labels

    # Simpan model dan scaler untuk dipakai di tahap/dashboard berikutnya
    joblib.dump(kmeans, "../models/kmeans_model.pkl")
    joblib.dump(scaler, "../models/scaler.pkl")

    return df_result


def cluster_profiling(df_result):
    """Menampilkan profil rata-rata tiap cluster berdasarkan 7 indikator."""
    print("=" * 70)
    print(f"PROFIL CLUSTER (k={FINAL_K})")
    print("=" * 70)

    print("\nJumlah anggota per cluster:")
    print(df_result["Cluster"].value_counts().sort_index())

    print("\nRata-rata 7 indikator per cluster:")
    profile = df_result.groupby("Cluster")[FEATURE_COLS].mean().round(2)
    print(profile)

    for c in sorted(df_result["Cluster"].unique()):
        anggota = df_result[df_result["Cluster"] == c]["Kabupaten/Kota"].tolist()
        print(f"\n--- Anggota Cluster {c} ({len(anggota)} daerah) ---")
        print(anggota)

    return profile


if __name__ == "__main__":
    df_2025 = get_snapshot_2025()
    print("Jumlah data (harus 38):", len(df_2025))

    df_result = run_final_clustering(df_2025)
    profile = cluster_profiling(df_result)

    # Simpan hasil untuk dipakai di tahap berikutnya
    df_result.to_csv("../data/clustering_result_2025.csv", index=False)
    print("\nHasil clustering disimpan ke data/clustering_result_2025.csv")