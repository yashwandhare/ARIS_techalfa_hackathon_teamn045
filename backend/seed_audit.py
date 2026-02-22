"""
Seed all existing applications with mock audit (trust score + verification report).

Run from the backend directory:
    .venv/bin/python seed_audit.py

This uses the same deterministic seed as the DigiLocker service so data is consistent.
Any candidate that already has a trust_score is SKIPPED (no overwrite).
"""

import hashlib
import json
import random
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine, Base
from app.models.application import Application
from app.services.digilocker_service import run_government_verification


# ── Deterministic helpers ────────────────────────────────────────────────────

def _rng(candidate_id: int) -> random.Random:
    digest = hashlib.md5(f"{candidate_id}audit".encode()).hexdigest()
    return random.Random(int(digest[:8], 16))


RED_FLAGS_POOL = [
    "Resume claims 5+ years of experience but GitHub account is only 2 years old.",
    "Listed 'Kubernetes expert' but no container-related repositories found.",
    "High ATS score with low GitHub commit frequency — possible resume inflation.",
    "No public projects matching claimed internship tech stack.",
    "Profile photo and name mismatch with LinkedIn URL provided.",
    "Skill keywords copied verbatim from a popular template — no original phrasing.",
    "Claimed React expertise but primary language in GitHub is Java.",
]

FINDINGS_POOL = [
    "GitHub activity confirms strong Python usage across 80%+ of repositories.",
    "Commit history aligns with claimed project timelines.",
    "Open-source contributions to well-known libraries verified.",
    "Code quality analysis shows consistent documentation standards.",
    "No signs of copy-pasted code in primary repositories detected.",
    "Resume-listed skills corroborated by language statistics on GitHub.",
    "Active contributions in the last 90 days demonstrate current relevance.",
    "Portfolio projects match the complexity level described in resume.",
    "Peer review history in pull requests shows collaborative experience.",
    "Star count and fork activity on projects indicate genuine usage by others.",
]

SUMMARIES = [
    "Candidate profile appears authentic. GitHub activity strongly corroborates the claimed skill set. "
    "Minor inconsistencies in timeline but overall evidence is coherent.",

    "Strong evidence of genuine development experience. Code repositories reflect the level of expertise "
    "stated in the resume. No significant fraud indicators detected.",

    "Verification completed with high confidence. Claimed technologies align with measurable GitHub "
    "contributions. Recommend proceeding to technical interview.",

    "Candidate demonstrates consistent activity across multiple domains. Resume claims are substantiated "
    "by code evidence. Trust level: HIGH.",

    "Moderate confidence in profile authenticity. Some skill claims could not be independently verified "
    "through public repositories, but no explicit contradictions found.",
]


def generate_mock_report(app: Application) -> tuple[float, dict]:
    rng = _rng(app.id)

    # Trust score: skew toward good candidates for demo
    trust_score = round(rng.uniform(58, 95), 1)

    if trust_score >= 70:
        risk_level = "clear"
        recommendation = "proceed"
        num_flags = 0
        num_findings = rng.randint(4, 7)
    elif trust_score >= 50:
        risk_level = "review_required"
        recommendation = "review"
        num_flags = rng.randint(0, 1)
        num_findings = rng.randint(2, 5)
    else:
        risk_level = "high_risk"
        recommendation = "reject"
        num_flags = rng.randint(1, 2)
        num_findings = rng.randint(1, 3)

    red_flags = rng.sample(RED_FLAGS_POOL, num_flags)
    key_findings = rng.sample(FINDINGS_POOL, num_findings)
    summary = rng.choice(SUMMARIES)

    # Include government verification data
    gov_data = run_government_verification(app.id, app.full_name)

    report = {
        "trust_score": trust_score,
        "risk_level": risk_level,
        "recommendation": recommendation,
        "verification_summary": summary,
        "red_flags": red_flags,
        "key_findings": key_findings,
        "government_verification": gov_data,
    }

    return trust_score, report


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        apps = db.query(Application).all()
        print(f"Found {len(apps)} application(s)")

        seeded = 0
        skipped = 0
        for app in apps:
            if app.trust_score is not None:
                print(f"  SKIP  [{app.id}] {app.full_name} — already has trust_score={app.trust_score}")
                skipped += 1
                continue

            trust_score, report = generate_mock_report(app)
            app.trust_score = trust_score
            app.verification_report_json = json.dumps(report)
            db.add(app)
            print(f"  SEED  [{app.id}] {app.full_name} → trust_score={trust_score}, risk={report['risk_level']}")
            seeded += 1

        db.commit()
        print(f"\nDone. Seeded: {seeded}, Skipped: {skipped}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
