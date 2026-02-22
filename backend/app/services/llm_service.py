"""LLM service — deep candidate-specific analysis and training plan generation.

Uses rich prompts with full candidate context per PRD §6.4.5 and §7.
"""

from __future__ import annotations

import json
import os
from typing import Any

import httpx


LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3-70b-8192")


def _get_api_key():
    return os.getenv("LLM_API_KEY")


def _request_llm(messages: list[dict[str, str]], max_tokens: int = 2048) -> dict | None:
    """Send a chat completion request and parse JSON response."""
    api_key = _get_api_key()
    if not api_key:
        return None

    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "response_format": {"type": "json_object"},
        "temperature": 0.3,
        "max_tokens": max_tokens,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                f"{LLM_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)
    except Exception:
        return None


def generate_profile_analysis(
    candidate_name: str,
    role_applied: str,
    github_metrics: dict,
    score_breakdown: dict,
    learning_gaps: list[str],
    resume_data: dict | None = None,
    education: dict | None = None,
    experience: dict | None = None,
    professional: dict | None = None,
) -> dict | None:
    """Generate a thorough, candidate-specific profile analysis.

    Returns: { summary, strengths, weaknesses, risks, growth_direction }
    """
    # Build rich context about this specific candidate
    languages = github_metrics.get("languages", {})
    top_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
    lang_str = ", ".join(f"{l[0]} ({l[1]}%)" for l in top_langs) if top_langs else "None detected"

    repos = github_metrics.get("total_public_repos", github_metrics.get("total_repos", 0))
    stars = github_metrics.get("total_stars", 0)
    commits = github_metrics.get("commits_last_90_days", 0)

    # Resume context
    resume_ctx = ""
    if resume_data:
        kw = resume_data.get("keywords_detected", [])
        ats = resume_data.get("ats_score", 0)
        pq = resume_data.get("project_quality", 0)
        resume_ctx = (
            f"\nResume Analysis: ATS score {ats}/100, project quality {pq}/100. "
            f"Keywords: {', '.join(kw[:15])}."
        )

    # Education context
    edu_ctx = ""
    if education:
        edu_ctx = (
            f"\nEducation: {education.get('degree', 'N/A')} in "
            f"{education.get('fieldOfStudy', 'N/A')} from "
            f"{education.get('institution', 'N/A')}. "
            f"CGPA: {education.get('gpa', 'N/A')}."
        )

    # Experience context
    exp_ctx = ""
    if experience:
        has_intern = experience.get("hasPreviousInternship", False)
        company = experience.get("company", "")
        exp_ctx = f"\nExperience: {'Has' if has_intern else 'No'} previous internship"
        if company:
            exp_ctx += f" at {company}"
        exp_ctx += "."

    # Professional context
    prof_ctx = ""
    if professional:
        tech_stack = professional.get("primaryTechStack", [])
        yoe = professional.get("yearsOfExperience", 0)
        if tech_stack:
            prof_ctx = f"\nTech Stack: {', '.join(tech_stack[:8])}. Experience: {yoe} years."

    scores_str = json.dumps(score_breakdown, indent=2)
    gaps_str = ", ".join(learning_gaps) if learning_gaps else "No major gaps identified"

    system_prompt = (
        "You are TechAlpha's senior technical evaluator. You must provide a thorough, "
        "SPECIFIC analysis of this particular candidate — NOT a generic template. "
        "Reference their actual skills, repos, languages, and scores. "
        "Return ONLY valid JSON with keys: summary, strengths (array of 3-5 strings), "
        "weaknesses (array of 2-4 strings), risks (array of 1-3 strings), "
        "growth_direction (string). "
        "The 'summary' must be exactly 150-200 words and mention the candidate BY NAME. "
        "JSON only, no markdown."
    )

    user_prompt = (
        f"Analyze candidate: {candidate_name}\n"
        f"Applied for: {role_applied}\n"
        f"\nGitHub Profile:\n"
        f"- {repos} public repos, {stars} stars, {commits} commits in last 90 days\n"
        f"- Top languages: {lang_str}\n"
        f"- Top repos: {json.dumps(github_metrics.get('top_repositories', []))}\n"
        f"{resume_ctx}{edu_ctx}{exp_ctx}{prof_ctx}\n"
        f"\nScore Breakdown:\n{scores_str}\n"
        f"\nIdentified Learning Gaps: {gaps_str}\n"
        f"\nProvide a thorough, specific profile analysis for {candidate_name}. "
        f"Be concrete — mention specific technologies, repos, and scores."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    return _request_llm(messages, max_tokens=1500)


def generate_training_plan_llm(
    candidate_name: str,
    role_applied: str,
    confidence_band: str,
    master_score: float,
    learning_gaps: list[str],
    score_breakdown: dict,
    github_metrics: dict,
    resume_data: dict | None = None,
    weeks: int | None = None,
    daily_hours: float | None = None,
    target_role: str | None = None,
) -> dict | None:
    """Generate a candidate-specific, structured training plan using LLM.

    Returns: { summary, focus_areas, weekly_plan: [{ week, goal, objectives, topics, tasks, deliverables }] }
    """
    languages = github_metrics.get("languages", {})
    top_langs = list(languages.keys())[:5]
    repos = github_metrics.get("total_public_repos", 0)
    commits = github_metrics.get("commits_last_90_days", 0)

    # Use admin-supplied weeks or derive from confidence band
    plan_weeks = weeks if weeks and weeks > 0 else {"Strong": 4, "Good": 5, "Moderate": 6, "Risk": 8}.get(confidence_band, 6)
    plan_role = target_role or role_applied
    hours_note = f" The candidate will dedicate {daily_hours} hours/day." if daily_hours else ""

    kw_list = []
    if resume_data:
        kw_list = resume_data.get("keywords_detected", [])[:10]

    system_prompt = (
        "You are a technical training architect at TechAlpha. "
        "Generate a SPECIFIC, personalized training plan for this candidate. "
        "The plan must address their actual skill gaps and build on their existing strengths. "
        "Do NOT generate generic plans — reference specific technologies and skills."
        f"{hours_note} "
        f"Create exactly {plan_weeks} weeks. "
        "Return ONLY valid JSON with keys: "
        "summary (string, 50-100 words), "
        "focus_areas (array of 3-5 specific strings), "
        "weekly_plan (array of objects with keys: week (number), goal (string), "
        "objectives (array of 2-3 strings), topics (array of 2-4 strings), "
        "tasks (array of 1-2 strings), deliverables (array of 1-2 strings)). "
        "JSON only, no markdown."
    )

    gaps_str = "; ".join(learning_gaps) if learning_gaps else "No major gaps"
    all_roles = score_breakdown.get("all_role_scores", {})
    role_scores_str = ", ".join(f"{r}: {s}%" for r, s in all_roles.items()) if all_roles else "N/A"

    user_prompt = (
        f"Candidate: {candidate_name}\n"
        f"Role: {plan_role}\n"
        f"Score: {master_score}/100 ({confidence_band})\n"
        f"Languages: {', '.join(top_langs) if top_langs else 'None'}\n"
        f"Repos: {repos}, Commits (90d): {commits}\n"
        f"Resume Keywords: {', '.join(kw_list) if kw_list else 'No resume'}\n"
        f"Role Match Scores: {role_scores_str}\n"
        f"Learning Gaps: {gaps_str}\n"
        f"Score Breakdown: {json.dumps(score_breakdown)}\n\n"
        f"Create a {plan_weeks}-week training plan specifically for {candidate_name} "
        f"to prepare them for the {plan_role} role. "
        f"Address their gaps while building on their strengths in {', '.join(top_langs[:3]) if top_langs else 'general programming'}."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    return _request_llm(messages, max_tokens=2500)


def generate_resume_ats(
    resume_text: str,
    role: str,
    candidate_name: str = "",
) -> dict | None:
    """LLM-powered ATS evaluation of resume text."""
    system_prompt = (
        "You are an ATS evaluator for technical internship positions. "
        "Analyze this candidate's resume thoroughly for the specified role. "
        "Return ONLY valid JSON with keys: "
        "ats_score (number 0-100), "
        "keywords_detected (array of tech keywords found), "
        "missing_keywords (array of important missing keywords for this role), "
        "suggestions (array of 2-3 specific improvement suggestions). "
        "JSON only."
    )

    user_content = (
        f"Candidate: {candidate_name}\n"
        f"Applied Role: {role}\n\n"
        f"Resume Text:\n{resume_text[:3000]}"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]
    return _request_llm(messages, max_tokens=1000)


def modify_plan_with_chat(
    existing_plan: dict,
    admin_message: str,
    candidate_name: str,
    role_applied: str,
) -> dict | None:
    """Modify an existing training plan based on admin's natural-language instruction.

    Preserves plan structure while applying the requested changes.
    Returns the updated plan JSON.
    """
    system_prompt = (
        "You are an expert training plan editor for a tech internship program. "
        "You receive an existing training plan and an admin's modification request. "
        "Apply ONLY the specific changes requested while keeping everything else intact. "
        "Preserve the plan structure, candidate-specific content, and overall quality. "
        "Return ONLY valid JSON with the same structure as the input plan: "
        "summary (string), focus_areas (array of strings), "
        "weekly_plan (array of objects: week, goal, objectives, topics, tasks, deliverables). "
        "JSON only, no markdown, no explanation."
    )

    user_prompt = (
        f"Candidate: {candidate_name}\n"
        f"Role: {role_applied}\n\n"
        f"Current Training Plan:\n{json.dumps(existing_plan, indent=2)}\n\n"
        f"Admin's modification request: {admin_message}\n\n"
        f"Apply the admin's changes and return the updated training plan JSON."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    return _request_llm(messages, max_tokens=2500)

