
# PDF Dark Mode Converter 🌗

Welcome to the **PDF Dark Mode Converter 🌗**! This Streamlit application allows users to upload PDF files and convert them to dark mode by inverting the colors. Users can adjust the inversion level to suit their preferences. The processed PDF files can be viewed within the app and downloaded for offline use.

**Check this out:https://pdfdarkmodeconverter.streamlit.app/**

## Features
- Upload multiple PDF files
- Adjust the inversion level for color conversion
- Process and convert PDF files to dark mode
- View the processed PDFs within the app
- Download the processed PDF files

## Installation
To run this project locally, you need to have Python installed. Follow these steps to set up the environment:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/pdf-dark-mode-converter.git
   cd pdf-dark-mode-converter
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv env
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```bash
     .\env\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     source env/bin/activate
     ```

4. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage
To run the Streamlit app, use the following command:
```bash
streamlit run app.py
```

This will start the Streamlit server and open the app in your default web browser.

## Dependencies
The project relies on the following key libraries:
- **Streamlit:** For building the web application
- **PyMuPDF (fitz):** For handling PDF files
- **Pillow (PIL):** For image processing
- **ReportLab:** For generating new PDF files
- **streamlit-pdf-viewer:** For viewing PDFs within the Streamlit app

Ensure all dependencies are listed in the `requirements.txt` file for easy installation.

## Code Explanation
Here is a brief explanation of the main components of the code:

### Processing Function
The `process_pdf` function takes an input PDF file and a filter level to adjust the inversion. It uses PyMuPDF to read the PDF, Pillow to invert the colors, and ReportLab to generate the new PDF.

### Main UI Layout
The Streamlit app layout includes sections for uploading files, adjusting the inversion level, and viewing or downloading the processed PDFs.

### Customization and Processing
When users upload PDFs and start the processing, the app shows progress bars and messages. Processed files are stored in the session state and can be downloaded or viewed using `streamlit-pdf-viewer`.

## Contributions
Contributions are welcome! If you find a bug or have a feature request, please open an issue on GitHub. Feel free to fork the repository and submit pull requests.

## License
This project is licensed under the MIT License.

## Contact
For any questions or feedback, please reach out to me on [GitHub](https://github.com/ofurkancoban), [LinkedIn](https://www.linkedin.com/in/ofurkancoban), or [Kaggle](https://www.kaggle.com/ofurkancoban).

---