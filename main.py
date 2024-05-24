import streamlit as st
import fitz  # PyMuPDF
from PIL import Image, ImageOps
import io
import time
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from streamlit_pdf_viewer import pdf_viewer

# İşleme fonksiyonu
def process_pdf(input_pdf_bytes, filter_level):
    pdf_document = fitz.open(stream=input_pdf_bytes, filetype="pdf")

    output_buffer = io.BytesIO()
    c = canvas.Canvas(output_buffer)

    num_pages = len(pdf_document)

    for page_number in range(num_pages):
        page = pdf_document.load_page(page_number)
        page_width, page_height = page.rect.width, page.rect.height

        zoom = 2
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        inverted_image = ImageOps.invert(image)

        if filter_level == 50:
            filter_level = 60

        blend_factor = filter_level / 100
        final_image = Image.blend(image, inverted_image, blend_factor)

        image_bytes = io.BytesIO()
        final_image.save(image_bytes, format="PNG", optimize=True, quality=50)
        image_bytes.seek(0)

        c.setPageSize((page_width, page_height))
        img_reader = ImageReader(image_bytes)
        c.drawImage(img_reader, 0, 0, width=page_width, height=page_height)
        c.showPage()

    c.save()
    output_buffer.seek(0)

    return output_buffer
# Main UI layout
st.set_page_config(page_title="PDF Dark Mode Converter 🌗", page_icon="🌗")
st.markdown('<div style="text-align: center;font-size:300%;margin-bottom: 30px"><b>PDF Dark Mode Converter 🌗</b></div>',
            unsafe_allow_html=True)

# Display images using HTML
st.markdown(
    """
    <div style="display: flex; justify-content: space-around; padding: 0 0 10px 0px">
        <a href="https://github.com/ofurkancoban"><img href ="https://github.com/ofurkancoban" src="https://raw.githubusercontent.com/ofurkancoban/xml2csv/master/img/github.png" width="30" style="pointer-events: none;"></a>
        <a href="https://www.linkedin.com/in/ofurkancoban"><img src="https://raw.githubusercontent.com/ofurkancoban/xml2csv/master/img/linkedin-in.png" width="30" style="pointer-events: none;"></a>
        <a href="https://www.kaggle.com/ofurkancoban"><img src="https://raw.githubusercontent.com/ofurkancoban/xml2csv/master/img/kaggle.png" width="30" style="pointer-events: none;"></a>
    </div>
    """, unsafe_allow_html=True
)

# Customization Section
st.markdown("<hr>", unsafe_allow_html=True)
def start_processing():
    st.session_state.start_processing = True
    st.session_state.processed_files = []

# Başlangıçta session_state'i kontrol et ve başlat
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = []

if 'start_processing' not in st.session_state:
    st.session_state.start_processing = False


uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    filter_level = st.slider("Adjust Inversion Level", 0, 100, 100, step=1)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div style="text-align: center;font-size:170%;margin-bottom: 10px"><b>🛠 Process PDFs</b></div>', unsafe_allow_html=True)

    if st.button("🖨️ START 🖨️", use_container_width=True, key="start_button"):
        start_processing()
        total_files = len(uploaded_files)
        total_progress = st.progress(0)
        progress_text = st.empty()
        file_counter = st.empty()

        for i, uploaded_file in enumerate(uploaded_files):
            file_counter.markdown(
                f"<div style='text-align: center; font-size: 24px; margin-bottom: 20px;'>"
                f"<b>Processing file {i+1} of {total_files}</b><br>"
                f"<span>{(i+1) * 100 / total_files:.2f}% completed</span></div>",
                unsafe_allow_html=True
            )
            with st.spinner(f"Processing {uploaded_file.name}"):
                binary_pdf = uploaded_file.read()
                input_pdf_stream = io.BytesIO(binary_pdf)
                input_pdf_stream.seek(0)

                output_pdf_stream = process_pdf(input_pdf_stream.getvalue(), filter_level)

                output_stream = output_pdf_stream.getvalue()
                st.session_state.processed_files.append(
                    (uploaded_file.name, output_stream, f"download_{i}_{time.time()}")
                )

            total_progress.progress((i + 1) / total_files)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div style="text-align: center;font-size:170%;margin-bottom: 10px"><b>🔎 View Processed PDFs</b></div>', unsafe_allow_html=True)

    for j, (file_name, output_stream, unique_key) in enumerate(st.session_state.processed_files):
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: center;font-size:170%;margin-bottom: 10px"><b>🔎 View PDF</b></div>', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"➔ {j + 1} -  {file_name}   ✅")
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