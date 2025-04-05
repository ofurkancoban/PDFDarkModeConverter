import streamlit as st
import fitz  # PyMuPDF
from PIL import Image, ImageOps
import io
import time
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from streamlit_pdf_viewer import pdf_viewer
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

# Processing function
def process_pdf(input_pdf_bytes, filter_level, zoom_level):
    pdf_document = fitz.open(stream=input_pdf_bytes, filetype="pdf")

    output_buffer = io.BytesIO()
    c = canvas.Canvas(output_buffer)

    num_pages = len(pdf_document)

    for page_number in range(num_pages):
        page = pdf_document.load_page(page_number)
        page_width, page_height = page.rect.width, page.rect.height

        # Use the zoom level selected by the user
        mat = fitz.Matrix(zoom_level, zoom_level)
        pix = page.get_pixmap(matrix=mat)
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        inverted_image = ImageOps.invert(image)

        # If filter level is 50, change it to 60 for inversion purposes
        if filter_level == 50:
            filter_level = 60

        blend_factor = filter_level / 100
        final_image = Image.blend(image, inverted_image, blend_factor)

        image_bytes = io.BytesIO()
        final_image.save(image_bytes, format="PNG", optimize=True, quality=100)
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

# Customization Section
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
    # Slider for zoom level (between 1 and 10, default value is 5)
    zoom_level = st.slider("Quality Level", min_value=1, max_value=10, value=5, step=1)

    st.info(
        "High quality levels increase file size and achieving original quality cannot be guaranteed.\n"
        "Additionally, due to Streamlit deployment limits, the app may crash at very high quality settings.\n"
        "Please choose an optimal zoom level.",icon="⚠️"
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

                # Pass the zoom level parameter to the processing function
                output_pdf_stream = process_pdf(input_pdf_stream.getvalue(), filter_level, zoom_level)

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