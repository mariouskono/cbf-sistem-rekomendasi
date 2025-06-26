# app.py

import streamlit as st
import pandas as pd
import joblib
import re
import string
from streamlit_product_card import product_card

# --- Fungsi pembersih teks ---
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
st.markdown("Pilih tempat favoritmu, dan kami rekomendasikan yang serupa!")

# --- Input pengguna ---
pilihan_tempat = st.selectbox("Kamu sedang berada di mana / mau ke mana?", sorted(df['nama'].unique()))

# --- Tombol ---
if st.button("Temukan Tempat Rekomendasi"):
    nama_input = clean_text(pilihan_tempat)

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
                rekomendasi.append(df.loc[i])
            if len(rekomendasi) >= 10:
                break

        if not rekomendasi:
            st.warning("Tidak ditemukan tempat wisata yang mirip di kabupaten yang sama.")
        else:
            st.subheader("📍 Rekomendasi Tempat Wisata Mirip:")
            for idx, tempat in enumerate(rekomendasi):
                clicked = product_card(
                    product_name=tempat['nama'].title(),
                    description=[
                        f"Kategori: {tempat['kategori'].title()}",
                        f"Preferensi: {tempat['preferensi'].title()}",
                        f"Lokasi: {tempat['kabupaten_kota'].title()}",
                    ],
                    price=f"⭐ {tempat['rating']:.1f}",
                    product_image=tempat['link_gambar'] if pd.notna(tempat['link_gambar']) else "https://placekitten.com/400/300",
                    button_text="Lihat di Google Maps" if pd.notna(tempat['link_lokasi']) else None,
                    picture_position="left",
                    image_width_percent=40,
                    image_aspect_ratio="4/3",
                    image_object_fit="cover",
                    enable_animation=True,
                    mobile_breakpoint_behavior="stack top",
                    font_url="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap",
                    styles={
                        "card": {
                            "border-radius": "12px",
                            "box-shadow": "0 4px 8px rgba(0,0,0,0.1)",
                            "background-color": "#ffffff",
                            "margin-bottom": "16px",
                        },
                        "title": {
                            "font-family": "'Montserrat', sans-serif",
                            "font-size": "1.3em",
                            "font-weight": "600",
                        },
                        "text": {
                            "font-family": "'Montserrat', sans-serif",
                            "font-size": "0.95em",
                        },
                        "price": {
                            "font-family": "'Montserrat', sans-serif",
                            "font-size": "1em",
                            "color": "#e67700",
                            "font-weight": "bold"
                        },
                    },
                    key=f"rekomendasi_{idx}"
                )

                if clicked and pd.notna(tempat['link_lokasi']):
                    st.success(f"Membuka {tempat['nama']} di Google Maps...")
                    st.markdown(f"[Klik di sini untuk membuka Google Maps]({tempat['link_lokasi']})")
