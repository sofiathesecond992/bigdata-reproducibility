# =============================================================================
# SEPSIS RISK PREDICTION - DATA WRANGLING PIPELINE
# Mata Kuliah: Big Data dalam Dunia Kesehatan
# Deskripsi: Script ini melakukan preprocessing data EHR untuk mempersiapkan
#            fitur prediksi risiko sepsis berdasarkan kriteria Sepsis-3.
# Input : ehr_data.csv (lihat Data Dictionary di README.md)
# Output: sepsis_features_clean.csv
# Versi Python: 3.10+ | pandas: 2.x | numpy: 1.26+
# =============================================================================

import pandas as pd
import numpy as np

# ── 1. MUAT DATA ──────────────────────────────────────────────────────────────
def load_ehr_data(filepath: str) -> pd.DataFrame:
    """Memuat dataset EHR dari file CSV."""
    return pd.read_csv(filepath)

# ── 2. PENANGANAN MISSING VALUES ──────────────────────────────────────────────
def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strategi imputasi per variabel:
    - Variabel vital (suhu, nadi, RR): drop baris jika kosong
      → Rasional: tidak bisa diimputasi karena krusial untuk definisi sepsis
    - WBC: imputasi dengan median populasi
      → Rasional: distribusi skewed, median lebih robust dari mean
    - Antibiotik (biner): isi dengan 0 (tidak ada catatan = tidak diberikan)
      → Rasional: asumsi konservatif sesuai konvensi klinis EHR
    """
    vital_signs = ["body_temp_celsius", "heart_rate_bpm", "resp_rate_rpm"]
    df = df.dropna(subset=vital_signs)

    df["wbc_count_per_ul"] = df["wbc_count_per_ul"].fillna(
        df["wbc_count_per_ul"].median()
    )
    df["antibiotics_given"] = df["antibiotics_given"].fillna(0)
    return df

# ── 3. FILTER OUTLIER KLINIS ──────────────────────────────────────────────────
def filter_clinical_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menghapus nilai di luar rentang fisiologis yang tidak mungkin valid.
    Threshold berdasarkan rentang fisiologis manusia dewasa:
    - Suhu tubuh: 34–42°C (di bawah/atas → kemungkinan error input alat)
    - Nadi: 20–300 bpm
    - Laju napas: 4–50 x/menit
    """
    df = df[df["body_temp_celsius"].between(34, 42)]
    df = df[df["heart_rate_bpm"].between(20, 300)]
    df = df[df["resp_rate_rpm"].between(4, 50)]
    return df

# ── 4. NORMALISASI (Z-SCORE) ──────────────────────────────────────────────────
def normalize_features(df: pd.DataFrame, feature_cols: list) -> pd.DataFrame:
    """
    Normalisasi z-score: (x - mean) / std
    Dipilih karena distribusi variabel klinis kontinu (suhu, nadi, RR, WBC)
    mendekati normal setelah outlier dihapus. Min-max scaling tidak digunakan
    karena sensitif terhadap sisa outlier.
    """
    for col in feature_cols:
        mean, std = df[col].mean(), df[col].std()
        df[f"{col}_zscore"] = (df[col] - mean) / std
    return df

# ── 5. BUAT LABEL OUTCOME (SEPSIS-3) ─────────────────────────────────────────
def create_sepsis_label(df: pd.DataFrame) -> pd.DataFrame:
    """
    Definisi label: Sepsis-3 (Singer et al., JAMA 2016)
    Pasien diklasifikasikan sepsis (label=1) jika memenuhi ≥2 kriteria SIRS
    yang disertai dugaan infeksi (antibiotik diberikan):
      - Suhu > 38.3°C (demam)
      - Nadi > 90 bpm (takikardia)
      - Laju napas > 20 x/menit (takipnea)
      - WBC > 12.000/µL (leukositosis)
    CATATAN: Ini adalah proxy Sepsis-3; idealnya menggunakan SOFA score penuh.
    """
    sirs_criteria = (
        (df["body_temp_celsius"] > 38.3).astype(int) +
        (df["heart_rate_bpm"] > 90).astype(int) +
        (df["resp_rate_rpm"] > 20).astype(int) +
        (df["wbc_count_per_ul"] > 12000).astype(int)
    )
    df["sepsis_label"] = ((sirs_criteria >= 2) & (df["antibiotics_given"] == 1)).astype(int)
    return df

# ── 6. PIPELINE UTAMA ─────────────────────────────────────────────────────────
def run_pipeline(input_path: str, output_path: str) -> None:
    feature_cols = [
        "body_temp_celsius", "heart_rate_bpm",
        "resp_rate_rpm", "wbc_count_per_ul"
    ]

    df = load_ehr_data(input_path)
    df = handle_missing_values(df)
    df = filter_clinical_outliers(df)
    df = normalize_features(df, feature_cols)
    df = create_sepsis_label(df)

    # Pilih kolom final untuk modeling
    zscore_cols = [f"{c}_zscore" for c in feature_cols]
    output_cols = zscore_cols + ["antibiotics_given", "sepsis_label"]
    df[output_cols].to_csv(output_path, index=False)

    print(f"✔ Dataset tersimpan: {output_path}")
    print(f"  Jumlah pasien: {len(df)}")
    print(f"  Distribusi label:\n{df['sepsis_label'].value_counts()}")

if __name__ == "__main__":
    run_pipeline(
        input_path="ehr_data.csv",
        output_path="sepsis_features_clean.csv"
    )
