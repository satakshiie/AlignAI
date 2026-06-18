# test_layer1.py
from services.ats_skill_matching import match_skills

# Use your actual extracted resume + JD data
resume_skills = [
    "HTML", "CSS", "JavaScript", "Python", "Swift", "C++",
    "React.js", "Bootstrap", "Flask", "Figma", "Git",
    "VS Code", "Xcode", "SQL", "LLAMA", "Mistral",
    "prompt engineering", "responsive design", "UI/UX",
    "API integration", "SwiftUI", "Firebase",
    "Machine Learning", "Blender"
]

# Simulate a JD's required/preferred skills
required_skills = [
    "Python", "React", "Node.js", "REST APIs",
    "SQL", "Machine Learning", "Docker"
]

preferred_skills = [
    "FastAPI", "PostgreSQL", "AWS", "UI/UX design"
]

result = match_skills(resume_skills, required_skills, preferred_skills)

import json
print(json.dumps(result, indent=2))