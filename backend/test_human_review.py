# test_human_review.py
from graph.tailoring_graph import build_tailoring_graph
from langgraph.types import Command
import json

graph = build_tailoring_graph()

config = {"configurable": {"thread_id": "test-session-1"}}

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

result = graph.invoke(initial_state, config=config)

if "__interrupt__" in result:
    print("GRAPH PAUSED FOR HUMAN REVIEW")
    print(json.dumps(result["__interrupt__"][0].value, indent=2))

    human_decisions = {
        "decisions": {
            "Collaborated on a team of developers to engineer a comprehensive native iOS healthcare platform utilizing Swift, SwiftUI, and Firebase.": "approved"
        }
    }

    final_result = graph.invoke(Command(resume=human_decisions), config=config)

    print("\n=== FINAL STATE AFTER HUMAN REVIEW ===")
    print(json.dumps(final_result["bullet_rewrites"], indent=2))
else:
    print("No human review needed — graph completed fully.")
    print(json.dumps(result, indent=2))