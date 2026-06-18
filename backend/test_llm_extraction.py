 # test_llm_extraction.py
from services.extraction_service import extract_text
from services.deterministic_extraction_service import extract_deterministic_fields
from services.llm_extraction_service import extract_resume_data

with open("/Users/satakshi/Downloads/resume_test.pdf", "rb") as f:
    file_content = f.read()

extraction_result = extract_text(file_content)
deterministic = extract_deterministic_fields(
    extraction_result["text"], "resume", extraction_result["hyperlinks"]
)

llm_result = extract_resume_data(
    deterministic["sections"],
    extraction_result["text"],
    extraction_result["method"]
)

if llm_result["success"]:
    import json
    print(json.dumps(llm_result["data"], indent=2))
else:
    print("ERROR:", llm_result["error"])