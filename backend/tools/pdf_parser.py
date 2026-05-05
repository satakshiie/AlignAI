# tools/pdf_parser.py

import re
import pdfplumber


# ── MOCK DATA ─────────────────────────────────────────────────────────────────

MOCK_PDF_BULLETS = [
    "Built and shipped 3 iOS apps using Swift and UIKit with 50k+ downloads.",
    "Integrated a real-time object detection feature using the Vision framework.",
    "Collaborated with designers and backend engineers to define API contracts.",
    "Mentored 2 junior developers and led weekly code review sessions.",
    "Managed feature branches and pull requests using Git and GitHub.",
]
# Strong action verbs that real bullet points start with
ACTION_VERBS = {
    "developed", "built", "designed", "created", "implemented", "led",
    "managed", "delivered", "improved", "increased", "decreased", "reduced",
    "collaborated", "contributed", "maintained", "integrated", "deployed",
    "launched", "shipped", "architected", "optimized", "automated", "migrated",
    "wrote", "tested", "reviewed", "mentored", "trained", "taught", "assisted",
    "supported", "coordinated", "conducted", "established", "streamlined",
    "negotiated", "presented", "analyzed", "researched", "generated", "drove",
    "spearheaded", "oversaw", "facilitated", "executed", "administered",
    "engineered", "refactored", "documented", "monitored", "configured",
    "troubleshot", "resolved", "diagnosed", "investigated", "evaluated",
    "identified", "proposed", "recommended", "achieved", "exceeded", "awarded",
    "gave", "held", "explained", "prepared", "tutored", "performed", "helped"
}


SKIP_PATTERNS = [
    r'^\d{3,}',
    r'^(education|experience|skills|activities|summary|objective|references|projects|awards|certifications)',
    r'@',
    r'\d{4}\s*[-–]\s*(\d{4}|present)',
    r'^(gpa|honors|dean)',
    r'^\+?\d[\d\s\-\(\)]{7,}',
    r'^[A-Z\s]{3,}$',
    r'^(programming languages|software|operating systems|professional):',  
    r'^(b\.s\.|b\.a\.|m\.s\.|ph\.d\.|minors|relevant courses)',          
 ]

# ── HELPERS ───────────────────────────────────────────────────────────────────

def should_skip(line: str) -> bool:
    """Returns True if this line should never be a bullet."""
    line_lower = line.lower().strip()
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, line_lower):
            return True
    return False


def starts_with_action_verb(line: str) -> bool:
    """Returns True if line starts with a known action verb."""
    first_word = line.strip().split()[0].lower().rstrip('.,;:')
    return first_word in ACTION_VERBS


def is_indented(line: str) -> bool:
    """Returns True if the line has leading whitespace (indented bullet)."""
    return line != line.lstrip() and len(line.strip()) > 0


def clean_bullet(line: str) -> str:
    """Strips bullet symbols and extra whitespace."""
    line = line.strip()
    line = re.sub(r'^[•\-\*–→▪◦‣]\s*', '', line)
    return line.strip()


def is_bullet(line: str) -> bool:
    """
    Multi-strategy bullet detection that works across resume styles.

    Strategy 1: Explicit bullet symbol (•, -, *, –)
    Strategy 2: Starts with a known action verb
    Strategy 3: Indented line that looks like a sentence
    """
    stripped = line.strip()

    if not stripped or len(stripped) < 15:
        return False

    if should_skip(stripped):
        return False

    # Strategy 1 — explicit bullet symbol
    if stripped.startswith(("•", "*", "–", "→", "▪", "◦", "‣", "\uf0a7", "\uf0b7")):
        return True

    # Strategy 2 — starts with action verb
    if starts_with_action_verb(stripped):
        return True

    # Strategy 3 — indented + long enough to be a sentence
    if is_indented(line) and len(stripped) > 30:
        return True

    return False


# ── MAIN FUNCTION ─────────────────────────────────────────────────────────────

def parse_resume_pdf(pdf_path: str, use_mock: bool = True) -> list[str]:
    """
    Takes a path to a 1-page PDF resume and returns
    a clean list of experience bullet points.
    Works across all resume formats — no API needed.
    """

    if use_mock:
        print("🟡 MOCK MODE: Returning hardcoded resume bullets (no PDF needed)")
        return MOCK_PDF_BULLETS

    print(f"📄 Parsing PDF: {pdf_path}...")

    try:
        with pdfplumber.open(pdf_path) as pdf:

            # ── page limit check ──
            if len(pdf.pages) > 1:
                raise ValueError(
                    f"Resume is {len(pdf.pages)} pages. "
                    "Please upload a 1-page resume."
                )

            raw_text = pdf.pages[0].extract_text()

            if not raw_text or raw_text.strip() == "":
                raise ValueError(
                    "Could not extract text from this PDF. "
                    "Make sure your PDF is not a scanned image."
                )

            print(f"📃 Raw text extracted ({len(raw_text)} characters)")

            lines = raw_text.split('\n')
            bullets = []

            for line in lines:
                if is_bullet(line):
                    cleaned = clean_bullet(line)
                    if cleaned and cleaned not in bullets:  # no duplicates
                        bullets.append(cleaned)

            if not bullets:
                raise ValueError(
                    "No bullet points found. "
                    "Make sure your resume includes experience descriptions."
                )

            print(f"✅ Extracted {len(bullets)} bullets from PDF")
            return bullets

    except FileNotFoundError:
        raise FileNotFoundError(f"PDF not found at path: {pdf_path}")
    except Exception as e:
        raise RuntimeError(f"PDF parsing failed: {str(e)}")


if __name__ == "__main__":
    import sys

    # Test 1: mock mode
    print("=" * 50)
    print("TEST 1: Mock mode")
    print("=" * 50)
    bullets = parse_resume_pdf("", use_mock=True)
    for i, b in enumerate(bullets, 1):
        print(f"  {i}. {b}")

    # Test 2: real PDF
    if len(sys.argv) > 1:
        print("\n" + "=" * 50)
        print("TEST 2: Real PDF mode")
        print("=" * 50)
        pdf_path = sys.argv[1]
        bullets = parse_resume_pdf(pdf_path, use_mock=False)
        print(f"\nBullets extracted: {len(bullets)}")
        for i, b in enumerate(bullets, 1):
            print(f"  {i}. {b}")