# app.py

import streamlit as st
import pandas as pd
import joblib

# Load data dan model
df = joblib.load('data_wisata_cleaned.pkl')
cosine_sim = joblib.load('cosine_similarity_matrix.pkl')
vectorizer = joblib.load('tfidf_vectorizer.pkl')

# Fungsi pembersih teks
import re
import string
def clean_text(text):
    if pd.isna(text):
        return ""
    text = text.lower()
    text = re.sub(f"[{re.escape(string.punctuation)}]", " ", text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# Judul Aplikasi
st.title("🎯 Rekomendasi Tempat Wisata di Bali")
st.markdown("Cari tempat wisata berdasarkan tempat yang Anda sukai di Bali.")

# Input: Pilih nama tempat wisata
pilihan_tempat = st.selectbox("Kamu sedang berada dimana / mau kemana?", sorted(df['nama'].unique()))

# Tombol Temukan
if st.button("Temukan Tempat Rekomendasi"):
    nama_input = clean_text(pilihan_tempat)

    if nama_input not in df['nama'].values:
        st.error(f"Tempat '{pilihan_tempat}' tidak ditemukan dalam data.")
    else:
        idx_input = df[df['nama'] == nama_input].index[0]
        kabupaten_input = df.loc[idx_input, 'kabupaten_kota']

        # Hitung skor similarity
        sim_scores = list(enumerate(cosine_sim[idx_input]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Ambil tempat dari kabupaten sama (kecuali diri sendiri)
        rekomendasi = []
        for i, score in sim_scores[1:]:
            if df.loc[i, 'kabupaten_kota'] == kabupaten_input:
                rekomendasi.append((df.loc[i], score))
            if len(rekomendasi) >= 5:
                break

        if not rekomendasi:
            st.warning("Tidak ada tempat wisata yang mirip ditemukan di kabupaten yang sama.")
        else:
            st.subheader("🧭 Rekomendasi Tempat Wisata Lain:")
            for tempat, skor in rekomendasi:
                with st.container():
                    if pd.notna(tempat['link_gambar']):
                        st.image(tempat['link_gambar'], caption=tempat['nama'], use_container_width=True)

                    st.markdown(f"**{tempat['nama'].title()}**")
                    st.markdown(f"- Kategori: {tempat['kategori'].title()}")
                    st.markdown(f"- Preferensi: {tempat['preferensi'].title()}")
                    st.markdown(f"- Kabupaten/Kota: {tempat['kabupaten_kota'].title()}")
                    st.markdown(f"- Rating: {tempat['rating']}")
                    
                    if pd.notna(tempat['link_lokasi']):
                        st.link_button("📍 Lihat di Google Maps", tempat['link_lokasi'])

                    st.markdown("---")
