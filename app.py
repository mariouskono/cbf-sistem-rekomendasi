# app.py

import streamlit as st
import pandas as pd
import joblib
import re
import string
import base64
from streamlit_card import card

# --- Fungsi untuk membersihkan teks ---
def clean_text(text):
    if pd.isna(text):
        return ""
    text = text.lower()
    text = re.sub(f"[{re.escape(string.punctuation)}]", " ", text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# --- Load data dan model ---
df = joblib.load('data_wisata_cleaned.pkl')
cosine_sim = joblib.load('cosine_similarity_matrix.pkl')
vectorizer = joblib.load('tfidf_vectorizer.pkl')

# --- Judul Aplikasi ---
st.set_page_config(page_title="Rekomendasi Wisata Bali", layout="wide")
st.title("🎯 Rekomendasi Tempat Wisata di Bali")
st.markdown("Cari tempat wisata berdasarkan tempat favorit Anda di Bali.")

# --- Input pengguna ---
pilihan_tempat = st.selectbox("Kamu sedang berada di mana / mau ke mana?", sorted(df['nama'].unique()))

# --- Tombol ---
if st.button("Temukan Tempat Rekomendasi"):
    nama_input = clean_text(pilihan_tempat)

    # Verifikasi apakah input ada dalam data
    if nama_input not in df['nama'].str.lower().values:
        st.error(f"Tempat '{pilihan_tempat}' tidak ditemukan.")
    else:
        idx_input = df[df['nama'].str.lower() == nama_input].index[0]
        kabupaten_input = df.loc[idx_input, 'kabupaten_kota']

        # Hitung similarity
        sim_scores = list(enumerate(cosine_sim[idx_input]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Filter rekomendasi dari kabupaten yang sama
        rekomendasi = []
        for i, score in sim_scores[1:]:
            if df.loc[i, 'kabupaten_kota'] == kabupaten_input:
                rekomendasi.append((df.loc[i], score))
            if len(rekomendasi) >= 12:
                break

        if not rekomendasi:
            st.warning("Tidak ditemukan tempat wisata yang mirip di kabupaten yang sama.")
        else:
            st.subheader("🧭 Rekomendasi Tempat Wisata Mirip di Kabupaten yang Sama:")

            # Tampilkan dalam bentuk card (3 kolom per baris)
            for i in range(0, len(rekomendasi), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(rekomendasi):
                        tempat, skor = rekomendasi[i + j]
                        with cols[j]:
                            # Cek gambar valid
                            img = tempat['link_gambar'] if pd.notna(tempat['link_gambar']) else "https://placekitten.com/400/300"
                            
                            # Tampilkan card
                            card(
                                title=tempat['nama'].title(),
                                text=[
                                    f"Kategori: {tempat['kategori'].title()}",
                                    f"Rating: {tempat['rating']:.1f}",
                                    f"Lokasi: {tempat['kabupaten_kota'].title()}",
                                ],
                                image=img,
                                url=tempat['link_lokasi'] if pd.notna(tempat['link_lokasi']) else None,
                                styles={
                                    "card": {
                                        "width": "100%",
                                        "height": "340px",
                                        "box-shadow": "0 0 10px rgba(0,0,0,0.1)",
                                        "border-radius": "12px",
                                        "margin": "10px"
                                    },
                                    "title": {"font-size": "18px"},
                                    "text": {"font-size": "14px"}
                                }
                            )
