import magic
import aiofiles
import os
from fastapi import UploadFile, HTTPException

ALLOWED_MIME = "application/pdf"
MAX_SIZE_MB = 10
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024
UPLOAD_DIR = "uploaded_files"

os.makedirs(UPLOAD_DIR, exist_ok=True)


async def validate_and_save(file: UploadFile, doc_type: str) -> dict:

    # STEP 1 — Read full file content once
    # We need the full content for size check and corruption check anyway
    await file.seek(0)
    content = await file.read()

    # STEP 2 — Explicit empty file check
    # Don't rely on python-magic behaviour for this — check it ourselves
    if len(content) == 0:
        raise HTTPException(
            status_code=400,
            detail="File is empty. Please upload a valid PDF."
        )

    # STEP 3 — MIME check on the actual bytes
    mime_type = magic.from_buffer(content[:2048], mime=True)

    if mime_type != ALLOWED_MIME:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type detected: '{mime_type}'. Only PDFs are accepted."
        )

    # STEP 4 — Size check
    size_bytes = len(content)
    size_mb = round(size_bytes / (1024 * 1024), 2)

    if size_bytes > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File too large: {size_mb} MB. Limit is {MAX_SIZE_MB} MB."
        )

    # STEP 5 — Corruption check using pdfplumber
    # A corrupted PDF passes MIME check but fails to open
    # We attempt to open it here and catch the failure early
    import pdfplumber
    import io

    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:

            # STEP 6 — Password-protected check
            # pdfplumber raises PDFPasswordIncorrect if the file is encrypted
            # An encrypted PDF with no password still triggers this
            page_count = len(pdf.pages)

            if page_count == 0:
                raise HTTPException(
                    status_code=400,
                    detail="PDF has no pages. The file may be corrupted."
                )

    except HTTPException:
        # Re-raise our own HTTPExceptions — don't swallow them
        raise

    except pdfplumber.pdfminer.pdfparser.PDFSyntaxError:
        raise HTTPException(
            status_code=400,
            detail="PDF appears to be corrupted and cannot be read."
        )

    except Exception as e:
        error_msg = str(e).lower()

        # pdfplumber surfaces password protection as an exception message
        if "password" in error_msg or "encrypted" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="PDF is password-protected. Please upload an unlocked version."
            )

        # Any other parsing failure = treat as corrupted
        raise HTTPException(
            status_code=400,
            detail=f"Could not read PDF: {str(e)}"
        )

    # STEP 7 — All checks passed, save to disk
    safe_name = f"{doc_type}_{file.filename}"
    save_path = os.path.join(UPLOAD_DIR, safe_name)

    async with aiofiles.open(save_path, "wb") as f:
        await f.write(content)

    return {
        "filename": file.filename,
        "size_mb": size_mb,
        "mime_type": mime_type,
        "saved_path": save_path,
        "page_count": page_count,
        "content": content 
    }