# test_skill_gap_resolver.py
from graph.nodes.skill_gap_resolver import skill_gap_resolver_node
import json

# Simulate state using your actual resume data + a gaps report
# (reuse the resume parsed_data from your earlier test output)
fake_state = {
    "resume_parsed_data": {
        "skills": ["Swift", "SwiftUI", "Python", "React", "Firebase"],
        "experience": [
            {
                "role": "iOS Developer Intern",
                "company": "Infosys Mysore",
                "bullets": ["Engineered a native iOS healthcare platform using Swift, SwiftUI, and Firebase."]
            }
        ],
        "projects": [
            {
                "title": "Curelt",
                "tech_stack": ["Swift (iOS)", "Figma"],
                "bullets": ["Built an iOS symptom checker app."]
            }
        ]
    },
    "ats_gaps": [
        {
            "type": "missing_required_skill",
            "items": ["ios", "objective-c", "problem solving"]
        }
    ]
}

result = skill_gap_resolver_node(fake_state)
print(json.dumps(result, indent=2))