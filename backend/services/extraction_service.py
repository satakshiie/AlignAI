import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import os

if os.path.exists("/opt/homebrew/bin/tesseract"):
    pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

MINIMUM_TEXT_LENGTH = 100
OCR_RENDER_DPI = 300


def extract_with_pymupdf(file_content: bytes) -> str:
    doc = fitz.open(stream=file_content, filetype="pdf")
    full_text = ""

    for page in doc:
        full_text += page.get_text()
        full_text += "\n"

    doc.close()
    return full_text.strip()


def extract_hyperlinks(file_content: bytes) -> list[str]:
    """
    Extracts actual hyperlink URLs embedded in the PDF.
    Needed because resumes often show 'LinkedIn' as a clickable word
    rather than the raw URL appearing anywhere in the visible text —
    PyMuPDF's get_text() only sees the displayed label, never the
    underlying link target, so this has to be pulled separately.
    """
    doc = fitz.open(stream=file_content, filetype="pdf")
    links = []

    for page in doc:
        for link in page.get_links():
      
            if "uri" in link:
                links.append(link["uri"])

    doc.close()
    return links


def extract_with_tesseract(file_content: bytes) -> str:
    doc = fitz.open(stream=file_content, filetype="pdf")
    full_text = ""

    for page in doc:
        pix = page.get_pixmap(dpi=OCR_RENDER_DPI)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        page_text = pytesseract.image_to_string(img)
        full_text += page_text
        full_text += "\n"

    doc.close()
    return full_text.strip()


def extract_text(file_content: bytes) -> dict:
    text = extract_with_pymupdf(file_content)
    method_used = "pymupdf"


    hyperlinks = extract_hyperlinks(file_content)

    if len(text) < MINIMUM_TEXT_LENGTH:
        text = extract_with_tesseract(file_content)
        method_used = "tesseract_ocr"

        if len(text) < MINIMUM_TEXT_LENGTH:
            return {
                "success": False,
                "text": "",
                "method": method_used,
                "error": "Could not extract readable text from this PDF.",
                "hyperlinks": hyperlinks
            }

    return {
        "success": True,
        "text": text,
        "method": method_used,
        "char_count": len(text),
        "hyperlinks": hyperlinks
    }