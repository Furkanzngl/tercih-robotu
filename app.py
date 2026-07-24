import streamlit as st
import pandas as pd

st.set_page_config(page_title="YKS Tercih Robotu", layout="wide")

@st.cache_data
def load_data():
    try:
        df = pd.read_excel("yks_verileri.xlsx")
        df['Sıralama_Num'] = pd.to_numeric(df['Başarı Sırası'].astype(str).str.replace('.', ''), errors='coerce')
        return df
    except Exception as e:
        st.error(f"Veri yüklenirken hata oluştu: {e}")
        return pd.DataFrame()

df = load_data()

st.title("🎓 YKS Tercih Robotu")

if not df.empty:
    # Sütun kontrolü (Eski Excel dosyası yüklüyse çökmesini engeller)
    required_cols = ['Üniversite Türü', 'Öğretim Türü', 'Burs / Ücret']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        st.warning("⚠️ Excel dosyanız henüz güncellenmedi! Lütfen yeni veri_cek.py ile oluşturduğunuz yks_verileri.xlsx dosyasını GitHub'a yükleyin.")
    else:
        bolum_listesi = sorted(df['Program Adı'].dropna().unique().tolist())
        sehir_listesi = sorted(df['Şehir'].dropna().unique().tolist())
        uni_turleri = ["Tümü"] + sorted(df['Üniversite Türü'].dropna().unique().tolist())
        burs_turleri = ["Tümü"] + sorted(df['Burs / Ücret'].dropna().unique().tolist())
        ogretim_turleri = ["Tümü"] + sorted(df['Öğretim Türü'].dropna().unique().tolist())

        # --- ŞIK FİLTRELEME ALANI (FORM) ---
        with st.form(key="search_form"):
            st.markdown("### 🔍 Arama Kriterleri")
            
            # 1. Satır: Bölüm Arama, Şehir ve Üniversite Türü
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                secilen_bolum = st.selectbox("Bölüm Ara (Otomatik Tamamlama)", options=bolum_listesi, index=None, placeholder="Bölüm adı yazın veya seçin...")
            with col2:
                secilen_sehirler = st.multiselect("Şehir Seçimi (İsteğe Bağlı)", options=sehir_listesi)
            with col3:
                secilen_uni_turu = st.selectbox("Üniversite Türü", options=uni_turleri)

            # 2. Satır: Sıralama, Eğitim Düzeyi, Burs Durumu, Öğretim Türü
            col4, col5, col6, col7, col8 = st.columns([1.5, 1.5, 1.5, 2, 2])
            with col4:
                min_sira = st.number_input("Min Sıralama", min_value=0, value=0, step=10000)
            with col5:
                max_sira = st.number_input("Maks Sıralama", min_value=0, value=3000000, step=10000)
            with col6:
                secilen_derece = st.selectbox("Eğitim Düzeyi", ["Tümü", "Önlisans", "Lisans"])
            with col7:
                secilen_burs = st.selectbox("Burs / Ücret Durumu", options=burs_turleri)
            with col8:
                secilen_ogretim = st.selectbox("Öğretim Türü", options=ogretim_turleri)

            st.markdown("<br>", unsafe_allow_html=True)
            btn_col1, btn_col2 = st.columns([4, 1])
            with btn_col1:
                submit_button = st.form_submit_button(label="🔍 Sonuçları Getir / Filtrele", use_container_width=True, type="primary")
            with btn_col2:
                st.form_submit_button(label="🧹 Filtreleri Sıfırla", use_container_width=True)

        # --- FİLTRELEME MANTIĞI ---
        filtered_df = df.copy()

        if secilen_bolum:
            filtered_df = filtered_df[filtered_df['Program Adı'].astype(str).str.contains(secilen_bolum, case=False, na=False, regex=False)]

        if secilen_sehirler:
            filtered_df = filtered_df[filtered_df['Şehir'].isin(secilen_sehirler)]

        if secilen_uni_turu != "Tümü":
            filtered_df = filtered_df[filtered_df['Üniversite Türü'] == secilen_uni_turu]

        if secilen_derece != "Tümü":
            filtered_df = filtered_df[filtered_df['Derece'] == secilen_derece]

        if secilen_burs != "Tümü":
            filtered_df = filtered_df[filtered_df['Burs / Ücret'] == secilen_burs]

        if secilen_ogretim != "Tümü":
            filtered_df = filtered_df[filtered_df['Öğretim Türü'] == secilen_ogretim]

        filtered_df = filtered_df[
            (filtered_df['Sıralama_Num'].isna()) | 
            ((filtered_df['Sıralama_Num'] >= min_sira) & (filtered_df['Sıralama_Num'] <= max_sira))
        ]

        display_df = filtered_df.drop(columns=['Sıralama_Num'])

        st.markdown("---")
        st.success(f"Arama kriterlerinize uygun **{len(display_df)}** sonuç bulundu.")
        st.dataframe(display_df, use_container_width=True)

else:
    st.error("yks_verileri.xlsx dosyası bulunamadı!")
