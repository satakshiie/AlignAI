# test_ats_engine.py
from services.extraction_service import extract_text
from services.deterministic_extraction_service import extract_deterministic_fields
from services.llm_extraction_service import extract_resume_data, extract_jd_data
from services.ats_engine import compute_ats_score
import json

with open("/Users/satakshi/Downloads/SatakshiS_resume.pdf", "rb") as f:
    resume_content = f.read()

with open("/Users/satakshi/Downloads/JD_test1.pdf", "rb") as f:
    jd_content = f.read()

resume_extraction = extract_text(resume_content)
resume_deterministic = extract_deterministic_fields(
    resume_extraction["text"], "resume", resume_extraction["hyperlinks"]
)
resume_llm = extract_resume_data(
    resume_deterministic["sections"], resume_extraction["text"], resume_extraction["method"]
)

jd_extraction = extract_text(jd_content)
jd_deterministic = extract_deterministic_fields(
    jd_extraction["text"], "jd", jd_extraction["hyperlinks"]
)
jd_llm = extract_jd_data(
    jd_deterministic["sections"], jd_extraction["text"], jd_extraction["method"]
)

result = compute_ats_score(
    resume_parsed_data=resume_llm["data"],
    resume_deterministic=resume_deterministic,
    resume_raw_text=resume_extraction["text"],
    jd_parsed_data=jd_llm["data"],
    jd_deterministic=jd_deterministic,
    jd_raw_text=jd_extraction["text"]
)

print(json.dumps(result, indent=2))