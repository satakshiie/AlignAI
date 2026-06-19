# test_layer2.py
from services.extraction_service import extract_text
from services.deterministic_extraction_service import extract_deterministic_fields
from services.llm_extraction_service import extract_resume_data, extract_jd_data
from services.ats_section_coverage import analyze_section_coverage
import json

# Load resume
with open("/Users/satakshi/Downloads/SatakshiS_resume.pdf", "rb") as f:
    resume_content = f.read()

# Load JD — use your actual JD PDF
with open("/Users/satakshi/Downloads/JD_test1.pdf", "rb") as f:
    jd_content = f.read()

# Extract resume
resume_extraction = extract_text(resume_content)
resume_deterministic = extract_deterministic_fields(
    resume_extraction["text"], "resume", resume_extraction["hyperlinks"]
)
resume_llm = extract_resume_data(
    resume_deterministic["sections"],
    resume_extraction["text"],
    resume_extraction["method"]
)

# Extract JD
jd_extraction = extract_text(jd_content)
jd_deterministic = extract_deterministic_fields(
    jd_extraction["text"], "jd", jd_extraction["hyperlinks"]
)
jd_llm = extract_jd_data(
    jd_deterministic["sections"],
    jd_extraction["text"],
    jd_extraction["method"]
)

# Run Layer 2
result = analyze_section_coverage(
    resume_parsed_data=resume_llm["data"],
    resume_deterministic=resume_deterministic,
    jd_parsed_data=jd_llm["data"],
    jd_raw_text=jd_extraction["text"]
)

print(json.dumps(result, indent=2))