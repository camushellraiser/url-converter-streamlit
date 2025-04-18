
import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Language-to-path mapping
LANG_MAP = {
    "ja-JP": "/content/lifetech/japan/en-jp",
    "zh-CN": "/content/lifetech/greater-china/en-cn",
    "zh-TW": "/content/lifetech/greater-china/en-hk",
    "es-LATAM": "/content/lifetech/latin-america/en-mx",
    "es-ES": "/content/lifetech/europe/en-es",
    "fr-FR": "/content/lifetech/europe/en-fr",
    "de-DE": "/content/lifetech/europe/en-de",
    "pt-BR": "/content/lifetech/latin-america/en-br",
    "ko-KR": "/content/lifetech/ipac/en-kr"
}

def clean_url(url):
    if not isinstance(url, str) or "/home/" not in url:
        return None
    parts = url.split("/home/", 1)
    return "/home/" + parts[1].replace(".html", "") if len(parts) > 1 else None

def process_excel(file):
    df = pd.read_excel(file, sheet_name=0, header=3)
    results = []
    url_col = "URL in AEM"

    language_columns = [col for col in df.columns if any(code in str(col) for code in LANG_MAP.keys())]

    for _, row in df.iterrows():
        original_url = row.get(url_col)
        cleaned_path = clean_url(original_url)
        if not cleaned_path:
            continue
        for col in language_columns:
            for code in LANG_MAP:
                if code in str(col) and str(row[col]).strip().upper() == "X":
                    results.append({
                        "Original URL": original_url,
                        "Language": code,
                        "Localized Path": LANG_MAP[code] + cleaned_path
                    })

    return pd.DataFrame(results)

# Streamlit UI
st.set_page_config(page_title="🌐 URL Converter", layout="centered")
st.title("🌐 URL Converter")
st.write("Upload your Excel file and get localized AEM URLs based on language selection.")

uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        df_result = process_excel(uploaded_file)
        st.success("✅ Conversion completed!")

        st.dataframe(df_result)

        buffer = BytesIO()
        df_result.to_excel(buffer, index=False)
        buffer.seek(0)

        st.download_button(
            label="📥 Download Converted File",
            data=buffer,
            file_name="converted_urls.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"❌ Error: {e}")
