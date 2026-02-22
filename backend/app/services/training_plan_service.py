"""Deterministic training plan fallback — used when LLM is unavailable.

Generates structured plans based on role, confidence band, and learning gaps.
"""

from __future__ import annotations

from app.services.scoring_service import ROLE_KEYWORDS, _normalize_role_key


# Role-specific training topics
ROLE_TRAINING_TOPICS: dict[str, dict[str, list[str]]] = {
    "backend": {
        "foundation": [
            "Python fundamentals & best practices",
            "HTTP & REST API design patterns",
            "SQL & database design principles",
        ],
        "intermediate": [
            "FastAPI / Django development",
            "Authentication & authorization patterns",
            "Database optimization & indexing",
        ],
        "advanced": [
            "Microservices architecture",
            "Caching strategies (Redis)",
            "API security & rate limiting",
        ],
    },
    "frontend": {
        "foundation": [
            "HTML5 & CSS3 fundamentals",
            "JavaScript ES6+ core concepts",
            "Responsive design principles",
        ],
        "intermediate": [
            "React component architecture",
            "State management (Context, Redux)",
            "TypeScript for React applications",
        ],
        "advanced": [
            "Performance optimization & code splitting",
            "Testing (Jest, React Testing Library)",
            "Next.js & server-side rendering",
        ],
    },
    "data": {
        "foundation": [
            "Python for data analysis",
            "Pandas & NumPy fundamentals",
            "SQL for data querying",
        ],
        "intermediate": [
            "Data visualization (Matplotlib, Seaborn)",
            "Statistical analysis & hypothesis testing",
            "Machine learning basics (scikit-learn)",
        ],
        "advanced": [
            "Deep learning (TensorFlow/PyTorch)",
            "Feature engineering & model optimization",
            "Data pipeline design (Airflow, dbt)",
        ],
    },
    "full stack": {
        "foundation": [
            "HTML/CSS/JS web fundamentals",
            "React component basics",
            "Node.js / Python backend basics",
        ],
        "intermediate": [
            "Full stack CRUD application",
            "REST API + React integration",
            "Database design & ORM usage",
        ],
        "advanced": [
            "Docker & deployment workflows",
            "CI/CD pipeline setup",
            "System design & architecture",
        ],
    },
    "devops": {
        "foundation": [
            "Linux command line & shell scripting",
            "Git workflows & branching strategies",
            "Basic networking concepts",
        ],
        "intermediate": [
            "Docker containerization",
            "CI/CD with GitHub Actions",
            "Cloud services (AWS/GCP basics)",
        ],
        "advanced": [
            "Kubernetes orchestration",
            "Infrastructure as Code (Terraform)",
            "Monitoring & observability",
        ],
    },
}


def generate_training_plan(
    score_result: dict,
    role_applied: str = "",
    candidate_name: str = "",
) -> dict:
    """Generate a deterministic training plan as LLM fallback."""
    master_score = score_result.get("master_score", 50)
    confidence_band = score_result.get("confidence_band", "Moderate")
    learning_gaps = score_result.get("learning_gaps") or []
    score_breakdown = score_result.get("score_breakdown", {})

    role_key = _normalize_role_key(role_applied)
    role_topics = ROLE_TRAINING_TOPICS.get(role_key, ROLE_TRAINING_TOPICS["full stack"])

    # Determine plan parameters
    if confidence_band == "Risk":
        weeks = 8
        track = "Foundational"
        start_level = "foundation"
    elif confidence_band == "Moderate":
        weeks = 6
        track = "Strengthening"
        start_level = "foundation"
    elif confidence_band == "Good":
        weeks = 5
        track = "Accelerated"
        start_level = "intermediate"
    else:  # Strong
        weeks = 4
        track = "Advanced"
        start_level = "advanced"

    # Build focus areas from learning gaps
    focus_areas = []
    for gap in learning_gaps[:4]:
        gap_lower = str(gap).lower()
        if "language" in gap_lower or "diversity" in gap_lower:
            focus_areas.append(f"Technology stack expansion for {role_applied}")
        elif "consistency" in gap_lower or "commit" in gap_lower:
            focus_areas.append("Regular coding practice & contribution discipline")
        elif "visibility" in gap_lower or "documentation" in gap_lower:
            focus_areas.append("Project documentation & portfolio building")
        elif "role" in gap_lower or "align" in gap_lower:
            focus_areas.append(f"Core {role_applied} skill development")
        elif "resume" in gap_lower:
            focus_areas.append("Resume & professional profile enhancement")
        else:
            focus_areas.append("Technical skill development")

    if not focus_areas:
        focus_areas = [
            f"Deep {role_applied} specialization",
            "Building production-ready projects",
            "Industry best practices & patterns",
        ]

    # Build weekly plan
    weekly_plan = []
    level_order = ["foundation", "intermediate", "advanced"]
    start_idx = level_order.index(start_level) if start_level in level_order else 0

    for week_num in range(1, weeks + 1):
        # Progress through levels
        progress = (week_num - 1) / max(weeks - 1, 1)
        level_idx = min(start_idx + int(progress * (2 - start_idx)), 2)
        level = level_order[level_idx]
        topics = role_topics[level]

        # Pick topic for this week
        topic_idx = (week_num - 1) % len(topics)
        main_topic = topics[topic_idx]

        goal = f"{main_topic}"
        objectives = [
            f"Understand core concepts of {main_topic.lower()}",
            f"Complete hands-on exercises for {main_topic.split('&')[0].strip().lower()}",
        ]
        tasks = [
            f"Build a mini-project demonstrating {main_topic.split('(')[0].strip().lower()}",
        ]
        deliverables = [
            f"Working code pushed to GitHub with documentation",
            f"Progress report with learning reflections",
        ]

        weekly_plan.append({
            "week": week_num,
            "goal": goal,
            "objectives": objectives,
            "topics": [main_topic] + [t for i, t in enumerate(topics) if i != topic_idx][:1],
            "tasks": tasks,
            "deliverables": deliverables,
        })

    name_ref = f" for {candidate_name}" if candidate_name else ""
    summary = (
        f"{track} {weeks}-week training plan{name_ref} targeting the {role_applied} role. "
        f"Based on evaluation score of {master_score}/100 ({confidence_band} confidence). "
        f"Focuses on {', '.join(focus_areas[:2]).lower()} to address identified skill gaps."
    )

    return {
        "summary": summary,
        "focus_areas": focus_areas,
        "weekly_plan": weekly_plan,
    }
