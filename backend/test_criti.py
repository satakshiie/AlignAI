# test_critic.py
from graph.tailoring_graph import build_tailoring_graph
import json

graph = build_tailoring_graph()

initial_state = {
    "resume_parsed_data": {
        "skills": ["Swift", "SwiftUI", "Python", "React", "Firebase"],
        "experience": [
            {
                "role": "iOS Developer Intern",
                "company": "Infosys Mysore",
                "bullets": [
                    "Collaborated on a team of developers to engineer a comprehensive native iOS healthcare platform utilizing Swift, SwiftUI, and Firebase."
                ]
            }
        ],
        "projects": [
            {
                "title": "Curelt",
                "tech_stack": ["Swift (iOS)", "Figma"],
                "bullets": ["Engineered an AI-powered Symptom Checker using the Groq API and LLAMA 3.3 70B."]
            }
        ]
    },
    "jd_parsed_data": {
        "responsibilities": ["Develop and maintain native iOS applications", "Collaborate with cross-functional teams"]
    },
    "ats_gaps": [
        {"type": "missing_required_skill", "items": ["ios", "objective-c", "unit testing"]}
    ],
    "gap_items": [],
    "bullet_rewrites": [],
    "learning_roadmap": [],
    "needs_human_review": False
}

final_state = graph.invoke(initial_state)

print("NEEDS HUMAN REVIEW (overall):", final_state["needs_human_review"])
print("\n=== GAP ITEMS WITH CRITIC SCORES ===")
print(json.dumps(final_state["gap_items"], indent=2))
print("\n=== BULLET REWRITES WITH CRITIC SCORES ===")
print(json.dumps(final_state["bullet_rewrites"], indent=2))