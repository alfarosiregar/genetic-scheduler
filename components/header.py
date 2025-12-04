"""Header dan styling aplikasi"""
import streamlit as st
from PIL import Image
import base64
from io import BytesIO
from config.settings import APP_IMAGE_PATH, INPUT_IMAGE_PATH, RUN_IMAGE_PATH, RESULT_IMAGE_PATH, SETTING_IMAGE_PATH

def apply_custom_css():
    """Terapkan custom CSS"""
    st.markdown("""
    <style>
        .big-title {
            font-size: 36px;
            font-weight: 700;
            margin-bottom: -10px;
        }
        .sub {
            font-size: 18px;
            color: #666;
            margin-bottom: 20px;
        }
        .box {
            padding: 20px;
            border-radius: 12px;
            background: #ffffff;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)


def display_header():
    """Tampilkan header aplikasi"""
    st.markdown("<div class='big-title'>🧬 Genetic Scheduler</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub'>Aplikasi Penjadwalan Kuliah berbasis Algoritma Genetika</div>", unsafe_allow_html=True)


def display_image_on_app():
    """Tampilkan gambar dengan styling"""
    try:
        image = Image.open(APP_IMAGE_PATH)
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        st.markdown(
            f"""
            <div style="text-align: center;">
                <img src="data:image/jpeg;base64,{img_str}"
                style="width: 100%; 
                            max-width: 500px; 
                            height: auto; 
                            border-radius: 20px;
                            margin-bottom: 20px; 
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        st.warning(f"⚠️ Tidak dapat memuat gambar: {e}")

def display_image_on_input():
    """Tampilkan gambar dengan styling"""
    try:
        image = Image.open(INPUT_IMAGE_PATH)
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        st.markdown(
            f"""
            <div style="text-align: center;">
                <img src="data:image/jpeg;base64,{img_str}"
                style="width: 100%; 
                            max-width: 500px; 
                            height: auto; 
                            border-radius: 20px;
                            margin-bottom: 20px; 
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        st.warning(f"⚠️ Tidak dapat memuat gambar: {e}")

def display_image_on_run():
    """Tampilkan gambar dengan styling"""
    try:
        image = Image.open(RUN_IMAGE_PATH)
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        st.markdown(
            f"""
            <div style="text-align: center;">
                <img src="data:image/jpeg;base64,{img_str}"
                style="width: 100%; 
                            max-width: 500px; 
                            height: auto; 
                            border-radius: 20px;
                            margin-bottom: 20px; 
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        st.warning(f"⚠️ Tidak dapat memuat gambar: {e}")

def display_image_on_results():
    """Tampilkan gambar dengan styling"""
    try:
        image = Image.open(RESULT_IMAGE_PATH)
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        st.markdown(
            f"""
            <div style="text-align: center;">
                <img src="data:image/jpeg;base64,{img_str}"
                style="width: 100%; 
                            max-width: 500px; 
                            height: auto; 
                            border-radius: 20px;
                            margin-bottom: 20px; 
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        st.warning(f"⚠️ Tidak dapat memuat gambar: {e}")


def display_image_on_settings():
    """Tampilkan gambar dengan styling"""
    try:
        image = Image.open(SETTING_IMAGE_PATH)
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        st.markdown(
            f"""
            <div style="text-align: center;">
                <img src="data:image/jpeg;base64,{img_str}"
                style="width: 100%; 
                            max-width: 500px; 
                            height: auto; 
                            border-radius: 20px;
                            margin-bottom: 20px; 
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        st.warning(f"⚠️ Tidak dapat memuat gambar: {e}")