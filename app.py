import streamlit as st
import pandas as pd

st.set_page_config(page_title="YKS Tercih Robotu", layout="wide")

@st.cache_data
def load_data():
    try:
        df = pd.read_excel("yks_verileri.xlsx")
        df['Sıralama_Num'] = pd.to_numeric(df['Başarı Sırası'].astype(str).str.replace('.', ''), errors='coerce')
        return df
    except Exception:
        return pd.DataFrame()

df = load_data()

st.title("🎓 YKS Akıllı Tercih Robotu")

if 'secilen_bolum' not in st.session_state:
    st.session_state.secilen_bolum = None
if 'min_sira' not in st.session_state:
    st.session_state.min_sira = 0
if 'max_sira' not in st.session_state:
    st.session_state.max_sira = 3000000
if 'derece' not in st.session_state:
    st.session_state.derece = "Tümü"

def reset_filters():
    st.session_state.secilen_bolum = None
    st.session_state.min_sira = 0
    st.session_state.max_sira = 3000000
    st.session_state.derece = "Tümü"

bolum_listesi = sorted(df['Program Adı'].dropna().unique().tolist()) if not df.empty else []

col1, col2, col3, col4, col5 = st.columns([3, 1.5, 1.5, 1.5, 1])

with col1:
    st.selectbox(
        "Bölüm Ara (Otomatik Tamamlama)", 
        options=bolum_listesi, 
        index=None, 
        placeholder="Örn: Tıbbi Görüntüleme...", 
        key="secilen_bolum"
    )
with col2:
    st.number_input("Minimum Sıralama", min_value=0, value=0, step=10000, key="min_sira")
with col3:
    st.number_input("Maksimum Sıralama", min_value=0, value=3000000, step=10000, key="max_sira")
with col4:
    st.selectbox("Eğitim Düzeyi", ["Tümü", "Önlisans", "Lisans"], key="derece")
with col5:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    st.button("🧹 Temizle", on_click=reset_filters, use_container_width=True)

if not df.empty:
    filtered_df = df.copy()

    if st.session_state.secilen_bolum:
        filtered_df = filtered_df[filtered_df['Program Adı'] == st.session_state.secilen_bolum]

    if st.session_state.derece != "Tümü":
        filtered_df = filtered_df[filtered_df['Derece'] == st.session_state.derece]

    filtered_df = filtered_df[
        (filtered_df['Sıralama_Num'].isna()) | 
        ((filtered_df['Sıralama_Num'] >= st.session_state.min_sira) & (filtered_df['Sıralama_Num'] <= st.session_state.max_sira))
    ]

    display_df = filtered_df.drop(columns=['Sıralama_Num'])

    st.success(f"Arama kriterlerinize uygun {len(display_df)} sonuç bulundu.")
    st.dataframe(display_df, use_container_width=True)
else:
    st.error("yks_verileri.xlsx dosyası bulunamadı! Önce veri_cek.py kodunu çalıştırın.")