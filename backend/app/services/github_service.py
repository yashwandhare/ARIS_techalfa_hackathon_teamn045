from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlparse

import httpx

from app.core.config import settings


def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def _extract_username(github_url: str) -> str:
    if not github_url:
        raise ValueError("GitHub URL is required")

    if "github.com" not in github_url:
        # Treat as raw username fallback
        return github_url.strip().strip("/")

    parsed = urlparse(github_url)
    path = parsed.path.strip("/")
    if not path:
        raise ValueError("GitHub username not found in URL")

    return path.split("/")[0]


def _safe_empty(username: str) -> dict[str, Any]:
    return {
        "username": username,
        "total_repos": 0,
        "total_public_repos": 0,
        "total_stars": 0,
        "top_repositories": [],
        "languages": {},
        "last_activity": None,
        "recent_activity_score_base": 0.0,
        "commits_last_90_days": 0,
    }


def fetch_github_metrics(github_url: str) -> dict[str, Any]:
    username = _extract_username(github_url)

    user_url = f"https://api.github.com/users/{username}"
    repos_url = f"https://api.github.com/users/{username}/repos?per_page=100"

    headers = {"Accept": "application/vnd.github+json"}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"

    try:
        with httpx.Client(timeout=10.0) as client:
            user_resp = client.get(user_url, headers=headers)
            if user_resp.status_code == 404:
                raise ValueError("GitHub user not found")
            user_resp.raise_for_status()

            repos_resp = client.get(repos_url, headers=headers)
            repos_resp.raise_for_status()

            repos = repos_resp.json()
    except ValueError:
        raise
    except Exception:
        return _safe_empty(username)

    non_fork_repos = [r for r in repos if not r.get("fork")]
    total_public_repos = len(non_fork_repos)
    total_stars = sum(r.get("stargazers_count", 0) for r in non_fork_repos)

    sorted_by_pushed = sorted(
        non_fork_repos,
        key=lambda r: r.get("pushed_at") or "",
        reverse=True,
    )
    analyzed_repos = sorted_by_pushed[:10]

    top_repositories = sorted(
        non_fork_repos,
        key=lambda r: r.get("stargazers_count", 0),
        reverse=True,
    )[:3]
    top_repositories = [
        {
            "name": r.get("name"),
            "stars": r.get("stargazers_count", 0),
            "language": r.get("language"),
        }
        for r in top_repositories
    ]

    cutoff = datetime.now(timezone.utc) - timedelta(days=90)
    commits_last_90_days = 0
    language_bytes: dict[str, int] = {}

    with httpx.Client(timeout=10.0) as client:
        for repo in analyzed_repos:
            owner = repo.get("owner", {}).get("login") or username
            repo_name = repo.get("name")
            if not repo_name:
                continue

            languages_url = f"https://api.github.com/repos/{owner}/{repo_name}/languages"
            commits_url = (
                f"https://api.github.com/repos/{owner}/{repo_name}/commits"
                f"?since={cutoff.isoformat()}&per_page=100"
            )

            try:
                lang_resp = client.get(languages_url, headers=headers)
                if lang_resp.status_code == 200:
                    repo_langs = lang_resp.json()
                    for lang, bytes_count in repo_langs.items():
                        language_bytes[lang] = language_bytes.get(lang, 0) + int(bytes_count)
            except Exception:
                pass

            try:
                commits_resp = client.get(commits_url, headers=headers)
                if commits_resp.status_code == 200:
                    commits = commits_resp.json()
                    commits_last_90_days += min(len(commits), 100)
            except Exception:
                pass

            if commits_last_90_days >= 500:
                commits_last_90_days = 500
                break

    total_lang_bytes = sum(language_bytes.values())
    if total_lang_bytes > 0:
        languages = {
            lang: round((bytes_count / total_lang_bytes) * 100, 2)
            for lang, bytes_count in language_bytes.items()
        }
    else:
        languages = {}

    last_activity = analyzed_repos[0].get("pushed_at") if analyzed_repos else None
    recent_activity_score_base = _clamp((commits_last_90_days / 50.0) * 100.0, 0, 100)

    return {
        "username": username,
        "total_repos": total_public_repos,
        "total_public_repos": total_public_repos,
        "total_stars": total_stars,
        "top_repositories": top_repositories,
        "languages": languages,
        "last_activity": last_activity,
        "recent_activity_score_base": round(recent_activity_score_base, 2),
        "commits_last_90_days": commits_last_90_days,
    }


if __name__ == "__main__":
    # Manual test only (requires network access)
    sample = fetch_github_metrics("https://github.com/octocat")
    print(sample)
