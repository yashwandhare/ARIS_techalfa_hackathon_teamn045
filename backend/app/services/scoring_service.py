"""Deterministic scoring engine — PRD §6.4.3 compliant.

Weights:
  Resume Skill Score   30%
  GitHub Activity      25%
  Project Depth        20%
  Role Alignment       15%
  Recency Score        10%
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


# ── helpers ──────────────────────────────────────────────────────────

def _log_curve(x: float, scale: float) -> float:
    """Gentle log curve so low values still get meaningful scores."""
    if x <= 0:
        return 0.0
    return min(1.0, math.log1p(x) / math.log1p(scale))


# ── per-role keyword sets ────────────────────────────────────────────

ROLE_KEYWORDS: dict[str, list[str]] = {
    "backend": [
        "python", "fastapi", "django", "flask", "api", "sql", "postgresql",
        "mongodb", "redis", "docker", "node.js", "express", "go", "java",
        "spring", "rest", "graphql", "microservices",
    ],
    "frontend": [
        "react", "javascript", "typescript", "html", "css", "vue", "angular",
        "next.js", "tailwind", "sass", "webpack", "vite", "ui", "ux",
        "responsive", "figma",
    ],
    "data": [
        "pandas", "numpy", "ml", "tensorflow", "sklearn", "pytorch", "r",
        "jupyter", "data", "analysis", "visualization", "statistics",
        "spark", "airflow", "sql", "tableau",
    ],
    "full stack": [
        "react", "javascript", "typescript", "python", "node.js", "api",
        "sql", "html", "css", "docker", "mongodb", "postgresql", "rest",
        "git", "ci/cd", "aws",
    ],
    "devops": [
        "docker", "kubernetes", "aws", "gcp", "azure", "terraform",
        "ci/cd", "jenkins", "github actions", "linux", "shell", "ansible",
        "monitoring", "nginx", "prometheus",
    ],
}

ALL_ROLE_LABELS = list(ROLE_KEYWORDS.keys())


def _normalize_role_key(role: str) -> str:
    key = role.strip().lower()
    for label in ALL_ROLE_LABELS:
        if label in key or key in label:
            return label
    # Fuzzy: "Backend Developer" → "backend"
    for label in ALL_ROLE_LABELS:
        if label.split()[0] in key:
            return label
    return key


# ── score components ─────────────────────────────────────────────────

def _resume_skill_score(resume_data: dict | None, languages: dict) -> float:
    """Resume Skill Score — 30% weight → 0-30 points.

    Uses tech keyword matches from parsed resume + GitHub languages.
    Generous: each matched keyword = ~3 pts, cap at 30.
    """
    if not resume_data:
        # If no resume, give a base score from GitHub languages alone
        lang_keys = {k.lower() for k in languages.keys()}
        base = min(len(lang_keys) * 3.0, 15.0)
        return _clamp(base, 0, 30)

    keywords = (
        resume_data.get("keywords_detected")
        or resume_data.get("keywords")
        or resume_data.get("skill_keywords")
        or []
    )
    keyword_set = {str(k).strip().lower() for k in keywords if str(k).strip()}

    # Also pull in GitHub languages as bonus
    lang_keys = {k.lower() for k in languages.keys()}
    combined = keyword_set.union(lang_keys)

    all_tech = {
        "python", "fastapi", "django", "flask", "api", "sql", "react",
        "javascript", "typescript", "html", "css", "pandas", "numpy",
        "ml", "tensorflow", "sklearn", "docker", "aws", "postgresql",
        "mongodb", "git", "node.js", "java", "go", "rust", "vue",
        "angular", "kubernetes", "redis", "graphql", "next.js", "express",
        "spring", "pytorch", "linux", "shell", "ci/cd",
    }
    matches = len(combined.intersection(all_tech))
    # Each match is worth ~3 points, generous curve
    score = min(matches * 3.0, 30.0)
    # ATS score bonus if present
    ats = float(resume_data.get("ats_score", 0) or 0)
    if ats > 0:
        score = max(score, ats * 0.3)  # ats_score is 0-100
    return _clamp(score, 0, 30)


def _github_activity_score(metrics: dict) -> float:
    """GitHub Activity — 25% weight → 0-25 points.

    Stars + commits + repo count with generous curves.
    """
    stars = float(metrics.get("total_stars", 0) or 0)
    commits_90 = float(metrics.get("commits_last_90_days", 0) or 0)
    repos = float(metrics.get("total_public_repos", metrics.get("total_repos", 0)) or 0)

    # Stars: log curve, 20 stars ≈ full credit
    star_pts = _log_curve(stars, 20) * 8.0

    # Commits 90d: 30 commits ≈ full credit
    commit_pts = _log_curve(commits_90, 30) * 10.0

    # Repos: 8 repos ≈ full credit
    repo_pts = _log_curve(repos, 8) * 7.0

    return _clamp(star_pts + commit_pts + repo_pts, 0, 25)


def _project_depth_score(metrics: dict) -> float:
    """Project Depth — 20% weight → 0-20 points.

    Considers: repo quality, language diversity, top repo stars, repo count.
    """
    top_repos = metrics.get("top_repositories") or []
    languages = metrics.get("languages") or {}
    repos = float(metrics.get("total_public_repos", metrics.get("total_repos", 0)) or 0)

    # Top repos aggregate stars (generous: 5 total stars ≈ good)
    top_stars = sum(float(r.get("stars", 0) or 0) for r in top_repos)
    star_pts = _log_curve(top_stars, 10) * 7.0

    # Language diversity: 3+ languages = full credit
    lang_count = len(languages)
    lang_pts = min(lang_count / 3.0, 1.0) * 6.0

    # Repo count bonus: 5+ meaningful repos
    repo_pts = _log_curve(repos, 5) * 4.0

    # Has description/README bonus (from top repos having names)
    detail_pts = min(len(top_repos), 3) * 1.0

    return _clamp(star_pts + lang_pts + repo_pts + detail_pts, 0, 20)


def _role_alignment_score(
    role_key: str,
    languages: dict,
    resume_data: dict | None,
) -> float:
    """Role Alignment — 15% weight → 0-15 points for the applied role."""
    required = ROLE_KEYWORDS.get(role_key, [])
    if not required:
        return 7.5  # neutral when role is unknown

    lang_keys = {k.lower() for k in languages.keys()}
    resume_kw: set[str] = set()
    if resume_data:
        for k in (
            resume_data.get("keywords_detected")
            or resume_data.get("keywords")
            or resume_data.get("skill_keywords")
            or []
        ):
            resume_kw.add(str(k).strip().lower())

    combined = lang_keys.union(resume_kw)
    matches = sum(1 for kw in required if kw in combined)
    ratio = matches / len(required)
    return _clamp(ratio * 15.0, 0, 15)


def _recency_score(metrics: dict) -> float:
    """Recency Score — 10% weight → 0-10 points.

    Based on last_activity date and recent commits.
    """
    commits_90 = float(metrics.get("commits_last_90_days", 0) or 0)
    last_activity = metrics.get("last_activity")

    # Commits recency component
    commit_pts = _log_curve(commits_90, 20) * 5.0

    # Last activity freshness
    freshness_pts = 0.0
    if last_activity:
        try:
            if isinstance(last_activity, str):
                last_dt = datetime.fromisoformat(last_activity.replace("Z", "+00:00"))
            else:
                last_dt = last_activity
            days_ago = (datetime.now(timezone.utc) - last_dt).days
            if days_ago <= 7:
                freshness_pts = 5.0
            elif days_ago <= 30:
                freshness_pts = 4.0
            elif days_ago <= 90:
                freshness_pts = 3.0
            elif days_ago <= 180:
                freshness_pts = 1.5
        except Exception:
            freshness_pts = 2.0

    return _clamp(commit_pts + freshness_pts, 0, 10)


def _compute_all_role_scores(
    languages: dict,
    resume_data: dict | None,
) -> dict[str, float]:
    """Compute match percentage for every role."""
    scores = {}
    for role_key, required in ROLE_KEYWORDS.items():
        lang_keys = {k.lower() for k in languages.keys()}
        resume_kw: set[str] = set()
        if resume_data:
            for k in (
                resume_data.get("keywords_detected")
                or resume_data.get("keywords")
                or resume_data.get("skill_keywords")
                or []
            ):
                resume_kw.add(str(k).strip().lower())

        combined = lang_keys.union(resume_kw)
        matches = sum(1 for kw in required if kw in combined)
        scores[role_key] = round(_clamp((matches / len(required)) * 100, 0, 100), 1)
    return scores


# ── main entry ───────────────────────────────────────────────────────

def compute_scores(
    github_metrics: dict,
    resume_data: dict | None = None,
    role_applied: str | None = None,
) -> dict[str, Any]:
    """Compute deterministic scores matching PRD §6.4.3 weights."""

    languages = github_metrics.get("languages") or {}
    role_key = _normalize_role_key(role_applied or "")

    resume_pts = _resume_skill_score(resume_data, languages)       # 0-30
    github_pts = _github_activity_score(github_metrics)            # 0-25
    project_pts = _project_depth_score(github_metrics)             # 0-20
    role_pts = _role_alignment_score(role_key, languages, resume_data)  # 0-15
    recency_pts = _recency_score(github_metrics)                   # 0-10

    master_score = resume_pts + github_pts + project_pts + role_pts + recency_pts
    master_score = _clamp(master_score, 0, 100)

    if master_score >= 75:
        confidence_band = "Strong"
    elif master_score >= 60:
        confidence_band = "Good"
    elif master_score >= 45:
        confidence_band = "Moderate"
    else:
        confidence_band = "Risk"

    # All role match scores for the chart
    all_role_scores = _compute_all_role_scores(languages, resume_data)

    # Learning gaps — specific to the candidate
    learning_gaps: list[str] = []
    lang_count = len(languages)
    commits_90 = float(github_metrics.get("commits_last_90_days", 0) or 0)
    stars = float(github_metrics.get("total_stars", 0) or 0)

    if lang_count < 2:
        learning_gaps.append("Expand language diversity — learn a second core language")
    if commits_90 < 10:
        learning_gaps.append("Increase coding consistency — aim for regular commits")
    if stars < 3:
        learning_gaps.append("Build projects with greater visibility and documentation")
    if role_pts < 8:
        learning_gaps.append(f"Strengthen skills aligned to {role_applied or 'target'} role")
    if resume_pts < 15 and resume_data:
        learning_gaps.append("Add more relevant tech keywords and project details to resume")

    return {
        "master_score": round(master_score, 1),
        "confidence_band": confidence_band,
        "score_breakdown": {
            "resume_skill_score": round(resume_pts, 1),
            "github_activity_score": round(github_pts, 1),
            "project_quality_score": round(project_pts, 1),
            "role_alignment_score": round(role_pts, 1),
            "recency_score": round(recency_pts, 1),
            "all_role_scores": all_role_scores,
        },
        "learning_gaps": learning_gaps,
    }
