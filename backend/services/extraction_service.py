import fitz  # PyMuPDF — imported as 'fitz' for historical reasons
import pytesseract
from PIL import Image
import io

# If a PDF returns less text than this, we don't trust it —
# could be a scanned PDF with a near-empty text layer
MINIMUM_TEXT_LENGTH = 100

# DPI for rendering PDF pages to images before OCR
# Higher = more accurate OCR but slower. 300 is a good balance.
OCR_RENDER_DPI = 300


def extract_with_pymupdf(file_content: bytes) -> str:
    """
    Primary extraction path.
    PyMuPDF reads the embedded text layer directly — fast,
    and preserves natural reading order (important for resumes).
    """

    # Open the PDF from bytes in memory — no need to save to disk first
    doc = fitz.open(stream=file_content, filetype="pdf")

    full_text = ""

    for page in doc:
        # get_text() with no args returns plain text in reading order
        full_text += page.get_text()
        full_text += "\n"  # separate pages clearly

    doc.close()  # always close — avoids memory leaks on large batches

    return full_text.strip()


def extract_with_tesseract(file_content: bytes) -> str:
    """
    Fallback extraction path for scanned PDFs.
    Since there's no text layer, we render each page as an image
    and run OCR on the image instead.
    """

    doc = fitz.open(stream=file_content, filetype="pdf")

    full_text = ""

    for page in doc:
        # Render the PDF page to a pixel image (like a screenshot)
        # PyMuPDF does the rendering — Tesseract just reads images
        pix = page.get_pixmap(dpi=OCR_RENDER_DPI)

        # Convert PyMuPDF's pixmap into a PIL Image — Tesseract needs PIL format
        img = Image.open(io.BytesIO(pix.tobytes("png")))

        # Run OCR on this page's image
        page_text = pytesseract.image_to_string(img)

        full_text += page_text
        full_text += "\n"

    doc.close()

    return full_text.strip()


def extract_text(file_content: bytes) -> dict:
    """
    Main entry point. Tries PyMuPDF first, falls back to Tesseract
    only if PyMuPDF's output is too short to be trustworthy.
    """

    text = extract_with_pymupdf(file_content)
    method_used = "pymupdf"

    # If PyMuPDF didn't get enough text, this is likely a scanned PDF
    # with no real text layer — fall back to OCR
    if len(text) < MINIMUM_TEXT_LENGTH:
        text = extract_with_tesseract(file_content)
        method_used = "tesseract_ocr"

        # If OCR also fails to produce meaningful text, the PDF
        # is genuinely unreadable — flag it rather than silently
        # passing empty text downstream to the LLM
        if len(text) < MINIMUM_TEXT_LENGTH:
            return {
                "success": False,
                "text": "",
                "method": method_used,
                "error": "Could not extract readable text from this PDF."
            }

    return {
        "success": True,
        "text": text,
        "method": method_used,
        "char_count": len(text)
    }