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

# --- SESSION STATE İLK DEĞERLERİ ---
if "f_bolum" not in st.session_state: st.session_state.f_bolum = None
if "f_sehir" not in st.session_state: st.session_state.f_sehir = []
if "f_uni_turu" not in st.session_state: st.session_state.f_uni_turu = "Tümü"
if "f_min_sira" not in st.session_state: st.session_state.f_min_sira = 0
if "f_max_sira" not in st.session_state: st.session_state.f_max_sira = 3000000
if "f_derece" not in st.session_state: st.session_state.f_derece = "Tümü"
if "f_burs" not in st.session_state: st.session_state.f_burs = "Tümü"

# Filtre Sıfırlama Fonksiyonu (Tıklama anında çalışır)
def reset_filters():
    st.session_state.f_bolum = None
    st.session_state.f_sehir = []
    st.session_state.f_uni_turu = "Tümü"
    st.session_state.f_min_sira = 0
    st.session_state.f_max_sira = 3000000
    st.session_state.f_derece = "Tümü"
    st.session_state.f_burs = "Tümü"

st.title("🎓 YKS Akıllı Tercih Robotu")

if not df.empty:
    bolum_listesi = sorted(df['Program Adı'].dropna().unique().tolist())
    sehir_listesi = sorted(df['Şehir'].dropna().unique().tolist())
    uni_turleri = ["Tümü"] + sorted(df['Üniversite Türü'].dropna().unique().tolist()) if 'Üniversite Türü' in df.columns else ["Tümü"]
    burs_turleri = ["Tümü"] + sorted(df['Burs / Ücret'].dropna().unique().tolist()) if 'Burs / Ücret' in df.columns else ["Tümü"]

    # --- KOMPAKT & ŞIK FİLTRELEME ALANI ---
    with st.form(key="search_form"):
        # 1. Satır: Odak Noktası (Bölüm & Şehir)
        r1_col1, r1_col2 = st.columns([3, 2])
        with r1_col1:
            st.selectbox("Bölüm Ara", options=bolum_listesi, index=None, placeholder="Örn: Tıbbi Görüntüleme, Ekonomi...", key="f_bolum")
        with r1_col2:
            st.multiselect("Şehir Seçimi", options=sehir_listesi, placeholder="Tüm şehirler...", key="f_sehir")

        # 2. Satır: Kriter Filtreleri
        r2_c1, r2_c2, r2_c3, r2_c4, r2_c5 = st.columns(5)
        with r2_c1:
            st.number_input("Min Sıralama", min_value=0, step=10000, key="f_min_sira")
        with r2_c2:
            st.number_input("Maks Sıralama", min_value=0, step=10000, key="f_max_sira")
        with r2_c3:
            st.selectbox("Eğitim Düzeyi", ["Tümü", "Önlisans", "Lisans"], key="f_derece")
        with r2_c4:
            st.selectbox("Üniversite Türü", options=uni_turleri, key="f_uni_turu")
        with r2_c5:
            st.selectbox("Burs / Ücret", options=burs_turleri, key="f_burs")

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        
        # Butonlar
        btn_col1, btn_col2 = st.columns([4, 1])
        with btn_col1:
            st.form_submit_button(label="🔍 Sonuçları Getir", use_container_width=True, type="primary")
        with btn_col2:
            # on_click kullanarak hatayı tamamen engelliyoruz
            st.form_submit_button(label="🧹 Filtreleri Temizle", on_click=reset_filters, use_container_width=True)

    # --- FİLTRELEME MANTIĞI ---
    filtered_df = df.copy()

    if st.session_state.f_bolum:
        filtered_df = filtered_df[filtered_df['Program Adı'].astype(str).str.contains(st.session_state.f_bolum, case=False, na=False, regex=False)]

    if st.session_state.f_sehir:
        filtered_df = filtered_df[filtered_df['Şehir'].isin(st.session_state.f_sehir)]

    if st.session_state.f_uni_turu != "Tümü" and 'Üniversite Türü' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Üniversite Türü'] == st.session_state.f_uni_turu]

    if st.session_state.f_derece != "Tümü":
        filtered_df = filtered_df[filtered_df['Derece'] == st.session_state.f_derece]

    if st.session_state.f_burs != "Tümü" and 'Burs / Ücret' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Burs / Ücret'] == st.session_state.f_burs]

    filtered_df = filtered_df[
        (filtered_df['Sıralama_Num'].isna()) | 
        ((filtered_df['Sıralama_Num'] >= st.session_state.f_min_sira) & (filtered_df['Sıralama_Num'] <= st.session_state.f_max_sira))
    ]

    # Ekrandaki tablodan gereksiz kolonları kaldır
    drop_cols = ['Sıralama_Num', 'Öğretim Türü']
    display_df = filtered_df.drop(columns=[col for col in drop_cols if col in filtered_df.columns])

    st.markdown("---")
    st.success(f"Arama kriterlerinize uygun **{len(display_df)}** sonuç bulundu.")
    st.dataframe(display_df, use_container_width=True)

else:
    st.error("yks_verileri.xlsx dosyası bulunamadı!")
