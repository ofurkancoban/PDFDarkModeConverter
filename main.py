import streamlit as st
import fitz  # PyMuPDF
from PIL import Image, ImageOps
import io
import time
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from streamlit_pdf_viewer import pdf_viewer
import cv2
import numpy as np

st.set_page_config(page_title="PDF Dark Mode Converter 🌗", page_icon="🌗")

def add_custom_font():
    custom_font_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Josefin+Sans:wght@100;200;300;400;500;600;700&display=swap');
        * {
            font-family: 'Josefin Sans', sans-serif !important;
        }
    </style>
    """
    st.markdown(custom_font_css, unsafe_allow_html=True)

# Inject the custom font into the app
add_custom_font()

# Helper function to format file sizes
def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} Bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:,.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):,.2f} MB"

# Processing function with DPI adjustment via OpenCV
# while keeping Pillow inversion & blending intact.
def process_pdf(input_pdf_bytes, filter_level, dpi):
    pdf_document = fitz.open(stream=input_pdf_bytes, filetype="pdf")
    output_buffer = io.BytesIO()
    c = canvas.Canvas(output_buffer)
    num_pages = len(pdf_document)

    for page_number in range(num_pages):
        page = pdf_document.load_page(page_number)
        page_width, page_height = page.rect.width, page.rect.height

        # Render the page with the specified DPI for high resolution
        pix = page.get_pixmap(dpi=dpi)

        # Convert the pixmap to a NumPy array using OpenCV
        arr = np.frombuffer(pix.samples, dtype=np.uint8)
        channels = 4 if pix.alpha else 3
        arr = arr.reshape((pix.height, pix.width, channels))
        if channels == 4:
            arr = cv2.cvtColor(arr, cv2.COLOR_BGRA2RGB)
        else:
            arr = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
        # Convert the NumPy array to a PIL Image
        image = Image.fromarray(arr)

        # Apply inversion and blending using Pillow
        inverted_image = ImageOps.invert(image)
        if filter_level == 50:
            filter_level = 60
        blend_factor = filter_level / 100
        final_image = Image.blend(image, inverted_image, blend_factor)

        image_bytes = io.BytesIO()
        final_image.save(image_bytes, format="PNG", quality=100)
        image_bytes.seek(0)

        c.setPageSize((page_width, page_height))
        img_reader = ImageReader(image_bytes)
        c.drawImage(img_reader, 0, 0, width=page_width, height=page_height)
        c.showPage()

    c.save()
    output_buffer.seek(0)
    return output_buffer

st.markdown(
    '<div style="text-align: center;font-size:300%;margin-bottom: 30px"><b>PDF Dark Mode Converter 🌗</b></div>',
    unsafe_allow_html=True
)

# Display social media icons using HTML
st.markdown(
    """
    <div style="display: flex; justify-content: space-around; padding: 0 0 10px 0px">
        <a href="https://github.com/ofurkancoban"><img src="https://raw.githubusercontent.com/ofurkancoban/xml2csv/master/img/github.png" width="30" style="pointer-events: none;"></a>
        <a href="https://www.linkedin.com/in/ofurkancoban"><img src="https://raw.githubusercontent.com/ofurkancoban/xml2csv/master/img/linkedin-in.png" width="30" style="pointer-events: none;"></a>
        <a href="https://www.kaggle.com/ofurkancoban"><img src="https://raw.githubusercontent.com/ofurkancoban/xml2csv/master/img/kaggle.png" width="30" style="pointer-events: none;"></a>
    </div>
    """, unsafe_allow_html=True
)

st.markdown("<hr>", unsafe_allow_html=True)

def start_processing():
    st.session_state.start_processing = True
    st.session_state.processed_files = []

# Check and initialize session state at the start
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = []
if 'start_processing' not in st.session_state:
    st.session_state.start_processing = False

uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    # Slider for inversion level (min: 0, max: 100, default: 100)
    filter_level = st.slider("Adjust Inversion Level", 0, 100, 100, step=1)
    # Slider for DPI (output quality)
    dpi = st.slider("Output Quality (DPI)", 100, 800, 150, step=50)

    st.info(
        "High quality levels increase file size and achieving original quality cannot be guaranteed.\n"
        "Additionally, due to Streamlit deployment limits, the app may crash at very high quality settings.\n"
        "Please choose an optimal DPI.", icon="⚠️"
    )
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align: center;font-size:170%;margin-bottom: 10px"><b>🛠 Process PDFs</b></div>',
        unsafe_allow_html=True
    )

    if st.button("🖨️ START 🖨️", use_container_width=True, key="start_button"):
        start_processing()
        total_files = len(uploaded_files)
        total_progress = st.progress(0)
        progress_text = st.empty()
        file_counter = st.empty()

        for i, uploaded_file in enumerate(uploaded_files):
            file_counter.markdown(
                f"<div style='text-align: center; font-size: 24px; margin-bottom: 20px;'>"
                f"<b>Processing file {i + 1} of {total_files}</b><br>"
                f"<span>{(i + 1) * 100 / total_files:.2f}% completed</span></div>",
                unsafe_allow_html=True
            )
            with st.spinner(f"Processing {uploaded_file.name}"):
                binary_pdf = uploaded_file.read()
                input_pdf_stream = io.BytesIO(binary_pdf)
                input_pdf_stream.seek(0)

                # Pass the DPI parameter along with the inversion level to the processing function
                output_pdf_stream = process_pdf(input_pdf_stream.getvalue(), filter_level, dpi)
                output_stream = output_pdf_stream.getvalue()
                st.session_state.processed_files.append(
                    (uploaded_file.name, output_stream, f"download_{i}_{time.time()}")
                )

            total_progress.progress((i + 1) / total_files)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            '<div style="text-align: center;font-size:170%;margin-bottom: 10px"><b>🔎 View Processed PDFs</b></div>',
            unsafe_allow_html=True
        )

    for j, (file_name, output_stream, unique_key) in enumerate(st.session_state.processed_files):
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            '<div style="text-align: center;font-size:170%;margin-bottom: 10px"><b>🔎 View PDF</b></div>',
            unsafe_allow_html=True
        )
        col1, col2 = st.columns([3, 1])
        with col1:
            size_str = format_size(len(output_stream))
            st.write(f"➔ {j + 1} - {file_name} ✅ | ({size_str})")
        with col2:
            st.download_button(
                label="Download",
                data=output_stream,
                file_name=f"{file_name}_DarkMode.pdf",
                mime="application/pdf",
                use_container_width=True,
                key=f"download_{j}_{time.time()}"
            )

        # Display the output PDF using streamlit_pdf_viewer
        pdf_viewer(
            output_stream,
            width=1200,
            height=600,
            pages_vertical_spacing=2,
            annotation_outline_size=2,
            pages_to_render=[]
        )