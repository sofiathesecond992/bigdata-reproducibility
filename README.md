# bigdata-reproducibility
# Sepsis Risk Prediction — Data Wrangling Pipeline
  
**Tugas:** Implementasi, Audit, dan Penalaran Klinis dalam Big Data Kesehatan  

---

## Deskripsi Proyek

Pipeline ini memproses data Rekam Medis Elektronik (EHR) mentah untuk menghasilkan dataset fitur yang siap digunakan dalam model prediksi risiko sepsis. Label outcome menggunakan pendekatan proxy Sepsis-3 (Singer et al., JAMA 2016).

---

## Struktur Repositori

```
sepsis_pipeline/
├── sepsis_dirty.py          # Commit 1: Kode wrangling awal (kualitas rendah)
├── sepsis_clean.py          # Commit 2: Kode hasil refactoring
├── README.md                # Dokumentasi ini
└── data/
    ├── ehr_data.csv         # Input: data EHR mentah (tidak disertakan — lihat akses)
    └── sepsis_features_clean.csv  # Output: fitur siap modeling
```

---

## Cara Menjalankan

```bash
# Install dependencies
pip install pandas numpy

# Jalankan pipeline
python sepsis_clean.py
```

---

## Versi Software

| Komponen  | Versi  |
|-----------|--------|
| Python    | 3.10+  |
| pandas    | 2.2.x  |
| numpy     | 1.26.x |

---

## Data Dictionary

### Input: `ehr_data.csv`

| Nama Kolom           | Tipe    | Satuan   | Rentang Normal Klinis | Deskripsi                                              |
|----------------------|---------|----------|-----------------------|--------------------------------------------------------|
| `patient_id`         | string  | —        | —                     | ID unik pasien (anonim, sudah di-mask)                 |
| `body_temp_celsius`  | float   | °C       | 36.1 – 37.2           | Suhu tubuh saat masuk; outlier < 34°C atau > 42°C dihapus |
| `heart_rate_bpm`     | integer | bpm      | 60 – 100              | Nadi; outlier < 20 atau > 300 bpm dihapus             |
| `resp_rate_rpm`      | integer | x/menit  | 12 – 20               | Laju pernapasan; outlier < 4 atau > 50 dihapus        |
| `wbc_count_per_ul`   | float   | sel/µL   | 4.000 – 11.000        | Hitung leukosit; missing diimputasi dengan median     |
| `antibiotics_given`  | integer | biner    | 0 = tidak, 1 = ya     | Pemberian antibiotik dalam 24 jam; missing diisi 0    |

### Output: `sepsis_features_clean.csv`

| Nama Kolom                    | Tipe  | Deskripsi                                                            |
|-------------------------------|-------|----------------------------------------------------------------------|
| `body_temp_celsius_zscore`    | float | Z-score suhu tubuh                                                   |
| `heart_rate_bpm_zscore`       | float | Z-score nadi                                                         |
| `resp_rate_rpm_zscore`        | float | Z-score laju napas                                                   |
| `wbc_count_per_ul_zscore`     | float | Z-score WBC                                                          |
| `antibiotics_given`           | int   | Fitur biner pemberian antibiotik (tidak dinormalisasi)               |
| `sepsis_label`                | int   | Label outcome: 1 = sepsis (≥2 kriteria SIRS + antibiotik), 0 = tidak|

---

## Keputusan Analitis Utama

| Keputusan                   | Pilihan          | Alternatif       | Alasan Klinis                                                          |
|-----------------------------|------------------|------------------|------------------------------------------------------------------------|
| Normalisasi                 | Z-score          | Min-max scaling  | Distribusi mendekati normal; min-max sensitif outlier residual         |
| Imputasi WBC missing        | Median           | Mean / drop      | Distribusi WBC skewed → median lebih robust                            |
| Imputasi antibiotik missing | Isi dengan 0     | Drop baris       | Asumsi konservatif: tidak ada catatan = tidak diberikan                |
| Definisi sepsis             | Proxy Sepsis-3   | ICD-10 coding    | ICD-10 memiliki bias coding; proxy berbasis tanda vital lebih konsisten|
| Threshold outlier suhu      | 34–42°C          | IQR-based        | Batas fisiologis absolut manusia dewasa                                |

---

## Akses Data

Data EHR bersifat **terproteksi** sesuai regulasi privasi data medis.  
Untuk akses dataset: hubungi (Marsa Ajrina-Institut Teknologi Sepuluh Nopember) melalui prosedur permintaan data resmi.  
Hash checksum file input: `ehr_data.csv` → `[SHA256: dicatat di sini sebelum analisis]`
