"""ARIS Verification Crew — Multi-agent background verification pipeline.

Orchestrates 4 specialized CrewAI agents in sequence:
  1. GitHub Analyst     → Audits real coding activity
  2. Fraud Detector     → Cross-references resume claims vs evidence
  3. Compliance Manager → Computes Trust Score and writes HR report
  4. Onboarding Planner → Generates personalized training curriculum

Each agent's output feeds the next, producing a complete verification
package in under 2 minutes.
"""

from __future__ import annotations

import json
import os
from typing import Any

from crewai import Agent, Crew, Process, Task

from app.agents.tools import (
    compute_candidate_scores,
    cross_reference_claims,
    fetch_github_profile,
)


from langchain_groq import ChatGroq

_model_name = os.getenv("LLM_MODEL", "llama3-70b-8192")
if _model_name.startswith("groq/"):
    _model_name = _model_name[5:]

LLM_INSTANCE = ChatGroq(model=_model_name)


def _build_agents() -> dict[str, Agent]:
    """Create the 4 specialized verification agents."""

    github_analyst = Agent(
        role="Senior GitHub Activity Analyst",
        goal=(
            "Thoroughly audit a candidate's public GitHub profile to extract "
            "objective evidence of their real coding ability, including commit "
            "frequency, language proficiency, project complexity, and activity recency."
        ),
        backstory=(
            "You are a veteran code auditor at ARIS who has reviewed over "
            "10,000 developer profiles. You specialize in distinguishing genuine "
            "coding activity from superficial contributions. You believe that "
            "evidence speaks louder than claims."
        ),
        tools=[fetch_github_profile],
        llm=LLM_INSTANCE,
        verbose=True,
        allow_delegation=False,
    )

    fraud_detector = Agent(
        role="Background Verification Specialist",
        goal=(
            "Cross-reference every skill and experience claim on the candidate's "
            "resume against the GitHub evidence provided by the GitHub Analyst. "
            "Flag any mismatches, exaggerations, or contradictions with specific evidence."
        ),
        backstory=(
            "You are ARIS's fraud detection expert. You have uncovered hundreds "
            "of resume fabrications by methodically comparing claims to real data. "
            "You are fair but thorough — you always provide evidence for your findings."
        ),
        tools=[cross_reference_claims],
        llm=LLM_INSTANCE,
        verbose=True,
        allow_delegation=False,
    )

    compliance_manager = Agent(
        role="Hiring Compliance Officer",
        goal=(
            "Synthesize all verification findings into a final Trust Score (0-100) "
            "and produce a clear, actionable Verification Report for HR. Determine "
            "the overall risk level: Clear, Review Required, or High Risk."
        ),
        backstory=(
            "You are the head of hiring compliance at ARIS. You make the final "
            "determination on candidate trustworthiness. Your reports are used "
            "directly by HR directors to make hiring decisions. You are objective, "
            "precise, and always justify your scores with evidence."
        ),
        tools=[compute_candidate_scores],
        llm=LLM_INSTANCE,
        verbose=True,
        allow_delegation=False,
    )

    onboarding_planner = Agent(
        role="Technical Onboarding Specialist",
        goal=(
            "Based on the verified skill profile (not the claimed one), design "
            "a personalized week-by-week training plan that bridges the candidate's "
            "actual skill gaps for their target role."
        ),
        backstory=(
            "You are ARIS's onboarding architect. You create training plans that "
            "are specific to each candidate's verified abilities and weaknesses. "
            "Your plans have helped hundreds of new hires become productive in "
            "their first month."
        ),
        tools=[],
        llm=LLM_INSTANCE,
        verbose=True,
        allow_delegation=False,
    )

    return {
        "github_analyst": github_analyst,
        "fraud_detector": fraud_detector,
        "compliance_manager": compliance_manager,
        "onboarding_planner": onboarding_planner,
    }


def _build_tasks(
    agents: dict[str, Agent],
    github_url: str,
    role_applied: str,
    candidate_name: str,
    resume_skills: list[str] | None = None,
) -> list[Task]:
    """Create the sequential verification tasks."""

    skills_json = json.dumps(resume_skills or [])

    task_1_analyze_github = Task(
        description=(
            f"Analyze the GitHub profile for candidate '{candidate_name}' "
            f"at URL: {github_url}\n\n"
            f"Use the 'Fetch GitHub Profile' tool with the URL.\n"
            f"Then produce a structured report covering:\n"
            f"1. Total repositories and stars\n"
            f"2. Top programming languages with percentages\n"
            f"3. Commit frequency in the last 90 days\n"
            f"4. Top 3 repositories by stars\n"
            f"5. Activity recency assessment\n"
            f"6. Overall coding consistency evaluation"
        ),
        expected_output=(
            "A JSON object with keys: total_repos, total_stars, "
            "commits_90_days, top_languages (object), top_repositories (array), "
            "consistency_assessment (string), overall_quality (string)"
        ),
        agent=agents["github_analyst"],
    )

    task_2_detect_fraud = Task(
        description=(
            f"The candidate '{candidate_name}' claims these skills on their resume: "
            f"{skills_json}\n\n"
            f"Using the GitHub analysis from the previous task, cross-reference "
            f"each claimed skill against the real evidence.\n\n"
            f"Use the 'Cross Reference Claims' tool with the resume skills and "
            f"GitHub languages from the previous analysis.\n\n"
            f"For each skill, determine: verified, partial, contradicted, or unverifiable.\n"
            f"Flag any RED FLAGS where claims significantly contradict evidence."
        ),
        expected_output=(
            "A JSON object with keys: verification_results (array of "
            "{skill, status, evidence}), red_flags (array of strings), "
            "overall_integrity (string: 'high', 'medium', or 'low')"
        ),
        agent=agents["fraud_detector"],
        context=[task_1_analyze_github],
    )

    task_3_compliance = Task(
        description=(
            f"Based on the GitHub analysis and fraud detection results for "
            f"'{candidate_name}' (applied for: {role_applied}):\n\n"
            f"1. Use the 'Compute Candidate Scores' tool with the GitHub metrics, "
            f"role '{role_applied}', and resume keywords {skills_json}\n"
            f"2. Determine the final Trust Score (0-100)\n"
            f"3. Assign risk level: 'clear' (score >= 70), 'review_required' "
            f"(score 45-69), or 'high_risk' (score < 45)\n"
            f"4. Write a concise HR-ready verification summary\n"
            f"5. List key findings and any red flags from the fraud analysis"
        ),
        expected_output=(
            "A JSON object with keys: trust_score (number 0-100), "
            "risk_level (string), verification_summary (string, 100-200 words), "
            "key_findings (array of strings), red_flags (array of strings), "
            "recommendation (string: 'approve', 'manual_review', or 'reject')"
        ),
        agent=agents["compliance_manager"],
        context=[task_1_analyze_github, task_2_detect_fraud],
    )

    task_4_onboarding = Task(
        description=(
            f"Based on the VERIFIED skill profile (not the resume claims) for "
            f"'{candidate_name}' targeting the '{role_applied}' role:\n\n"
            f"1. Identify the candidate's proven strengths from GitHub evidence\n"
            f"2. Identify verified skill gaps between current abilities and role requirements\n"
            f"3. Generate a personalized week-by-week training plan (4-6 weeks)\n"
            f"4. Each week should have: goal, topics, tasks, and deliverables\n"
            f"5. Focus training on VERIFIED gaps, not assumed ones"
        ),
        expected_output=(
            "A JSON object with keys: summary (string), focus_areas (array of strings), "
            "weekly_plan (array of objects with: week, goal, objectives, topics, tasks, deliverables)"
        ),
        agent=agents["onboarding_planner"],
        context=[task_1_analyze_github, task_3_compliance],
    )

    return [task_1_analyze_github, task_2_detect_fraud, task_3_compliance, task_4_onboarding]


def run_verification(
    github_url: str,
    role_applied: str,
    candidate_name: str,
    resume_skills: list[str] | None = None,
) -> dict[str, Any]:
    """Execute the full 4-agent verification pipeline.

    Returns a dict with:
      - trust_score: float (0-100)
      - risk_level: str
      - verification_report: dict (full compliance report)
      - training_plan: dict (onboarding curriculum)
      - raw_output: str (full crew output for debugging)
    """
    agents = _build_agents()
    tasks = _build_tasks(
        agents=agents,
        github_url=github_url,
        role_applied=role_applied,
        candidate_name=candidate_name,
        resume_skills=resume_skills,
    )

    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()

    # Parse the final output — the last task's output is the training plan,
    # but we also need the compliance report from task 3
    raw_output = str(result)

    # Extract structured data from task outputs
    verification_report = {}
    training_plan = {}
    trust_score = 0.0
    risk_level = "review_required"

    # Try to parse compliance manager output (task 3)
    try:
        compliance_output = str(tasks[2].output)
        # Find JSON in the output
        json_start = compliance_output.find("{")
        json_end = compliance_output.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            compliance_data = json.loads(compliance_output[json_start:json_end])
            trust_score = float(compliance_data.get("trust_score", 0))
            risk_level = compliance_data.get("risk_level", "review_required")
            verification_report = compliance_data
    except (json.JSONDecodeError, ValueError, TypeError):
        # Fallback: extract what we can
        verification_report = {
            "verification_summary": raw_output[:500],
            "trust_score": 50.0,
            "risk_level": "review_required",
        }
        trust_score = 50.0

    # Try to parse onboarding planner output (task 4)
    try:
        planner_output = str(tasks[3].output)
        json_start = planner_output.find("{")
        json_end = planner_output.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            training_plan = json.loads(planner_output[json_start:json_end])
    except (json.JSONDecodeError, ValueError, TypeError):
        training_plan = {}

    return {
        "trust_score": trust_score,
        "risk_level": risk_level,
        "verification_report": verification_report,
        "training_plan": training_plan,
        "raw_output": raw_output,
    }
