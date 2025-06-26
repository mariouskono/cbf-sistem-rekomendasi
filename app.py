import streamlit as st
import pandas as pd
import joblib
import re
import string
from streamlit_card import card

# --- Fungsi Pembersih Teks ---
def clean_text(text):
    if pd.isna(text):
        return ""
    text = text.lower()
    text = re.sub(f"[{re.escape(string.punctuation)}]", " ", text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# --- Load Dataset dan Model ---
df = joblib.load('data_wisata_cleaned.pkl')
cosine_sim = joblib.load('cosine_similarity_matrix.pkl')
vectorizer = joblib.load('tfidf_vectorizer.pkl')

# --- Konfigurasi Streamlit ---
st.set_page_config(page_title="Rekomendasi Wisata Bali", layout="wide")
st.title("🎯 Rekomendasi Tempat Wisata di Bali")
st.markdown("Cari tempat wisata berdasarkan tempat yang Anda sukai di Bali.")

# --- Input User ---
pilihan_tempat = st.selectbox("Kamu sedang berada di mana / mau ke mana?", sorted(df['nama'].unique()))

# --- Rekomendasi Saat Tombol Diklik ---
if st.button("Temukan Tempat Rekomendasi"):
    nama_input = pilihan_tempat

    if nama_input not in df['nama'].values:
        st.error(f"Tempat '{pilihan_tempat}' tidak ditemukan dalam data.")
    else:
        idx_input = df[df['nama'] == nama_input].index[0]
        kabupaten_input = df.loc[idx_input, 'kabupaten_kota']

        sim_scores = list(enumerate(cosine_sim[idx_input]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Filter rekomendasi dari kabupaten yang sama, tidak termasuk dirinya
        rekomendasi = []
        for i, score in sim_scores[1:]:
            if df.loc[i, 'kabupaten_kota'] == kabupaten_input:
                rekomendasi.append((df.loc[i], score))
            if len(rekomendasi) >= 9:
                break

        if not rekomendasi:
            st.warning("Tidak ada tempat wisata yang mirip ditemukan di kabupaten yang sama.")
        else:
            st.subheader("🧭 Rekomendasi Tempat Wisata Lain:")
            cols = st.columns(3)
            for i, (tempat, skor) in enumerate(rekomendasi):
                col = cols[i % 3]
                with col:
                    if pd.notna(tempat['link_gambar']):
                        img = tempat['link_gambar']
                    else:
                        img = "https://placekitten.com/400/300"  # fallback image

                    card(
                        title=tempat['nama'].title(),
                        text=[
                            f"Kategori: {tempat['kategori'].title()}",
                            f"Rating: {tempat['rating']}",
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
                            "title": {"font-size": "20px"},
                            "text": {"font-size": "14px"},
                            "text_bottom": {"font-size": "16px"}
                        },
                        text_bottom=f"⭐ {tempat['rating']:.1f}"
                    )
