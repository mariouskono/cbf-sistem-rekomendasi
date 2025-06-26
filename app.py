import streamlit as st
import pandas as pd
from streamlit_card import card

# --- Load Dataset ---
df = pd.read_csv("dataset_tempat_wisata_bali.csv")

# Format kolom rating
df['rating'] = df['rating'].astype(str).str.replace(',', '.').astype(float)

# Hapus baris yang tidak memiliki rating
df = df.dropna(subset=['rating'])

# --- Sidebar: Input User ---
st.sidebar.title("Temukan Tempat Wisata")

# Pilih lokasi tempat awal
selected_place = st.sidebar.selectbox("Kamu sedang berada di / ingin ke mana?", df['nama'].unique())

# Tombol pencarian
if st.sidebar.button("Temukan Rekomendasi"):
    # Ambil kabupaten dari tempat yang dipilih
    selected_row = df[df['nama'] == selected_place].iloc[0]
    kabupaten_terpilih = selected_row['kabupaten_kota']

    # Filter tempat wisata lain yang berada di kabupaten yang sama
    rekomendasi = df[
        (df['kabupaten_kota'] == kabupaten_terpilih) &
        (df['nama'] != selected_place)
    ].sort_values(by='rating', ascending=False)

    st.title("Rekomendasi Tempat Wisata")
    st.write(f"Karena kamu memilih **{selected_place}**, berikut rekomendasi di **{kabupaten_terpilih}**:")

    # --- Layout 3 kolom per baris ---
    col_count = 3
    cols = st.columns(col_count)
    for idx, (_, row) in enumerate(rekomendasi.iterrows()):
        with cols[idx % col_count]:
            # Render card
            clicked = card(
                title=row['nama'],
                text=row['kabupaten_kota'],
                image=row['link_gambar'] if pd.notna(row['link_gambar']) else None,
                url=row['link_lokasi'] if pd.notna(row['link_lokasi']) else None,
                styles={
                    "card": {
                        "height": "350px",
                        "border-radius": "15px",
                        "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.2)",
                        "padding": "10px"
                    },
                    "title": {
                        "font-size": "18px",
                        "font-weight": "bold",
                        "color": "#333"
                    },
                    "text": {
                        "font-size": "14px",
                        "color": "#555"
                    }
                },
                text_bottom=f"⭐ {row['rating']}"
            )

else:
    st.title("Sistem Rekomendasi Tempat Wisata di Bali")
    st.write("Silakan pilih tempat yang kamu tuju dari sidebar untuk mendapatkan rekomendasi lainnya di sekitarnya.")
