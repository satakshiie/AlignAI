# test_extraction.py
from services.extraction_service import extract_text
from services.deterministic_extraction_service import extract_deterministic_fields, categorize_links

with open("/Users/satakshi/Downloads/SatakshiS_resume.pdf", "rb") as f:
    file_content = f.read()

extraction_result = extract_text(file_content)

print("METHOD:", extraction_result["method"])
print("CHAR COUNT:", extraction_result["char_count"])

links = categorize_links(extraction_result["hyperlinks"])
print("\nCATEGORIZED LINKS:")
print("LinkedIn:", links["linkedin"])
print("Portfolio:", links["portfolio"])
print("GitHub profile:", links["github_profile"])
print("Project links:", links["project_links"])

result = extract_deterministic_fields(
    extraction_result["text"],
    "resume",
    extraction_result["hyperlinks"]
)

print("\nDETERMINISTIC FIELDS:")
print("Name:", result["name"])
print("Email:", result["email"])
print("Phone:", result["phone"])
print("Dates:", result["dates"])

print("\nSECTIONS:")
for header, content in result["sections"].items():
    print(f"\n--- {header} ---")
    print(content[:200])