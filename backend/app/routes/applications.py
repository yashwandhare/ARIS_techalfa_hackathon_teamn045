import json
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.application import Application
from app.schemas.application import (
    ApplicationResponse,
    ApplicationStatusUpdate,
)
from app.services.github_service import fetch_github_metrics
from app.services.scoring_service import compute_scores
from app.services.resume_service import parse_resume_pdf
from app.services.training_plan_service import generate_training_plan
from app.services.llm_service import (
    generate_profile_analysis,
    generate_training_plan_llm,
    generate_resume_ats,
    modify_plan_with_chat,
)

router = APIRouter()


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Application.id)).scalar() or 0
    pending = (
        db.query(func.count(Application.id))
        .filter(Application.status.in_(["pending", "in_review"]))
        .scalar()
        or 0
    )
    accepted = (
        db.query(func.count(Application.id))
        .filter(Application.status == "accepted")
        .scalar()
        or 0
    )
    rejected = (
        db.query(func.count(Application.id))
        .filter(Application.status == "rejected")
        .scalar()
        or 0
    )
    one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    new_this_week = (
        db.query(func.count(Application.id))
        .filter(Application.created_at >= one_week_ago)
        .scalar()
        or 0
    )
    return {
        "total_applications": total,
        "pending_review": pending,
        "accepted": accepted,
        "rejected": rejected,
        "new_this_week": new_this_week,
    }


@router.post("", response_model=ApplicationResponse)
async def create_application(
    full_name: str = Form(...),
    email: str = Form(...),
    github_url: str = Form(...),
    role_applied: str = Form(...),
    personal_json: str = Form("{}"),
    education_json: str = Form("{}"),
    experience_json: str = Form("{}"),
    professional_json: str = Form("{}"),
    motivation_json: str = Form("{}"),
    resume_file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    """Create application — accepts multipart/form-data with optional PDF resume."""

    # 1. Fetch GitHub metrics
    try:
        github_metrics = fetch_github_metrics(github_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="GitHub API error") from exc

    # 2. Parse resume PDF if provided
    resume_data = None
    resume_text = ""
    if resume_file and resume_file.filename:
        try:
            file_bytes = await resume_file.read()
            resume_data = parse_resume_pdf(file_bytes)
            resume_text = resume_data.get("raw_text", "")
        except Exception:
            resume_data = None

    # 3. LLM ATS analysis of resume (if we have text)
    llm_resume = None
    if resume_text:
        llm_resume = generate_resume_ats(resume_text, role_applied, full_name)
        # Merge LLM keywords into resume_data
        if llm_resume and resume_data:
            llm_kw = llm_resume.get("keywords_detected", [])
            existing_kw = set(resume_data.get("keywords_detected", []))
            for kw in llm_kw:
                existing_kw.add(str(kw).lower().strip())
            resume_data["keywords_detected"] = sorted(existing_kw)
            # Use better ATS score if LLM provides one
            llm_ats = llm_resume.get("ats_score", 0)
            if llm_ats > 0:
                resume_data["ats_score"] = max(
                    resume_data.get("ats_score", 0),
                    float(llm_ats),
                )

    # 4. Compute deterministic scores
    score_result = compute_scores(
        github_metrics,
        resume_data=resume_data,
        role_applied=role_applied,
    )

    score_breakdown = score_result.get("score_breakdown", {})
    learning_gaps = score_result.get("learning_gaps", [])

    # 5. Parse education / experience for LLM context
    education = None
    experience = None
    professional = None
    try:
        education = json.loads(education_json) if education_json else None
    except Exception:
        pass
    try:
        experience = json.loads(experience_json) if experience_json else None
    except Exception:
        pass
    try:
        professional = json.loads(professional_json) if professional_json else None
    except Exception:
        pass

    # 6. LLM profile analysis with full candidate context
    llm_profile = generate_profile_analysis(
        candidate_name=full_name,
        role_applied=role_applied,
        github_metrics=github_metrics,
        score_breakdown=score_breakdown,
        learning_gaps=learning_gaps,
        resume_data=resume_data,
        education=education,
        experience=experience,
        professional=professional,
    )

    # 7. Save to database
    db_obj = Application(
        full_name=full_name,
        email=email,
        github_url=github_url,
        role_applied=role_applied,
        status="pending",
        personal_json=personal_json,
        education_json=education_json,
        experience_json=experience_json,
        professional_json=professional_json,
        motivation_json=motivation_json,
    )

    db_obj.master_score = score_result.get("master_score")
    db_obj.confidence_band = score_result.get("confidence_band")
    db_obj.github_metrics_json = json.dumps(github_metrics)
    db_obj.score_breakdown_json = json.dumps(score_breakdown)
    db_obj.learning_gaps_json = json.dumps(learning_gaps)

    if resume_data:
        # Store resume analysis (without raw_text to save space)
        analysis_to_store = {k: v for k, v in resume_data.items() if k != "raw_text"}
        if llm_resume:
            analysis_to_store["missing_keywords"] = llm_resume.get("missing_keywords", [])
            analysis_to_store["suggestions"] = llm_resume.get("suggestions", [])
        db_obj.resume_analysis_json = json.dumps(analysis_to_store)

    if llm_profile:
        db_obj.background_report_json = json.dumps(llm_profile)
    else:
        master = db_obj.master_score or 0
        band = db_obj.confidence_band or "Unknown"
        db_obj.background_report_json = json.dumps({
            "summary": (
                f"{full_name} scored {master}/100 ({band} confidence) for the "
                f"{role_applied} role. Their GitHub profile shows {github_metrics.get('total_public_repos', 0)} "
                f"public repos with {github_metrics.get('commits_last_90_days', 0)} commits in the last 90 days."
            ),
            "strengths": [
                f"Active GitHub presence with {github_metrics.get('total_public_repos', 0)} repositories",
            ],
            "weaknesses": learning_gaps[:3] if learning_gaps else ["No major weaknesses identified"],
            "risks": [],
            "growth_direction": f"Focus on strengthening {role_applied} specific skills.",
        })

    # 8. Save initial database object
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    # 9. Auto-trigger agentic verification if LLM key is configured
    from app.services.llm_service import LLM_API_KEY
    if LLM_API_KEY:
        try:
            from app.agents.verification_crew import run_verification

            # Parse resume skills for claims cross-referencing
            resume_skills = []
            if resume_data:
                resume_skills = (
                    resume_data.get("keywords_detected")
                    or resume_data.get("skill_keywords")
                    or []
                )

            # Trigger CrewAI
            result = run_verification(
                github_url=db_obj.github_url,
                role_applied=db_obj.role_applied,
                candidate_name=db_obj.full_name,
                resume_skills=resume_skills,
            )

            db_obj.trust_score = result.get("trust_score", 0.0)
            db_obj.verification_report_json = json.dumps(
                result.get("verification_report", {})
            )

            crew_plan = result.get("training_plan")
            if crew_plan and isinstance(crew_plan, dict) and crew_plan.get("weekly_plan"):
                db_obj.training_plan_json = json.dumps(crew_plan)

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        except Exception as e:
            # If verification fails, log it but still return the created application
            print(f"Auto-verification failed: {e}")

    return db_obj


@router.get("", response_model=list[ApplicationResponse])
def list_applications(db: Session = Depends(get_db)):
    return db.query(Application).order_by(Application.created_at.desc()).all()


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(application_id: int, db: Session = Depends(get_db)):
    db_obj = db.query(Application).filter(Application.id == application_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    return db_obj


class GeneratePlanRequest(BaseModel):
    weeks: int | None = None
    daily_hours: float | None = None
    target_role: str | None = None


@router.post("/{application_id}/generate-plan", response_model=ApplicationResponse)
def generate_plan(application_id: int, payload: GeneratePlanRequest = GeneratePlanRequest(), db: Session = Depends(get_db)):
    db_obj = db.query(Application).filter(Application.id == application_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    if db_obj.master_score is None:
        raise HTTPException(status_code=400, detail="Scoring not completed")

    score_breakdown = json.loads(db_obj.score_breakdown_json or "{}")
    learning_gaps = json.loads(db_obj.learning_gaps_json or "[]")
    github_metrics = json.loads(db_obj.github_metrics_json or "{}")
    resume_data = None
    try:
        resume_data = json.loads(db_obj.resume_analysis_json or "null")
    except Exception:
        pass

    # Try LLM first for candidate-specific plan
    llm_plan = generate_training_plan_llm(
        candidate_name=db_obj.full_name,
        role_applied=db_obj.role_applied,
        confidence_band=db_obj.confidence_band or "Moderate",
        master_score=db_obj.master_score or 0,
        learning_gaps=learning_gaps,
        score_breakdown=score_breakdown,
        github_metrics=github_metrics,
        resume_data=resume_data,
        weeks=payload.weeks,
        daily_hours=payload.daily_hours,
        target_role=payload.target_role,
    )

    if llm_plan:
        final_plan = llm_plan
    else:
        # Deterministic fallback
        score_result = {
            "master_score": db_obj.master_score,
            "confidence_band": db_obj.confidence_band,
            "score_breakdown": score_breakdown,
            "learning_gaps": learning_gaps,
        }
        final_plan = generate_training_plan(
            score_result,
            role_applied=db_obj.role_applied,
            candidate_name=db_obj.full_name,
        )

    db_obj.training_plan_json = json.dumps(final_plan)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


class ModifyPlanRequest(BaseModel):
    message: str


@router.post("/{application_id}/modify-plan", response_model=ApplicationResponse)
def modify_plan(application_id: int, payload: ModifyPlanRequest, db: Session = Depends(get_db)):
    """Modify an existing training plan via a natural-language admin message."""
    db_obj = db.query(Application).filter(Application.id == application_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    existing_plan = json.loads(db_obj.training_plan_json or "null")
    if not existing_plan:
        raise HTTPException(status_code=400, detail="No training plan exists yet. Generate one first.")

    updated_plan = modify_plan_with_chat(
        existing_plan=existing_plan,
        admin_message=payload.message,
        candidate_name=db_obj.full_name,
        role_applied=db_obj.role_applied,
    )

    if not updated_plan:
        raise HTTPException(status_code=503, detail="LLM not available. Check LLM_API_KEY configuration.")

    db_obj.training_plan_json = json.dumps(updated_plan)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


@router.patch("/{application_id}/status", response_model=ApplicationResponse)
def update_status(
    application_id: int,
    payload: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
):
    db_obj = db.query(Application).filter(Application.id == application_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    allowed = {
        "pending": {"in_review", "accepted", "rejected"},
        "in_review": {"accepted", "rejected"},
        "accepted": {"intern"},
        "intern": set(),
        "rejected": set(),
    }

    current_status = db_obj.status
    next_status = payload.status

    if next_status not in allowed.get(current_status, set()):
        raise HTTPException(status_code=400, detail="Invalid status transition")

    db_obj.status = next_status
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


@router.post("/{application_id}/verify", response_model=ApplicationResponse)
def verify_candidate(application_id: int, db: Session = Depends(get_db)):
    """Trigger the full CrewAI agentic verification pipeline.

    Runs 4 agents sequentially:
      1. GitHub Analyst — audits real coding activity
      2. Fraud Detector — cross-references resume claims
      3. Compliance Manager — computes Trust Score
      4. Onboarding Planner — generates training plan

    Saves trust_score, verification_report_json, and training_plan_json.
    """
    db_obj = db.query(Application).filter(Application.id == application_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    # Parse resume skills for cross-referencing
    resume_skills = []
    try:
        resume_data = json.loads(db_obj.resume_analysis_json or "{}")
        resume_skills = (
            resume_data.get("keywords_detected")
            or resume_data.get("skill_keywords")
            or []
        )
    except (json.JSONDecodeError, TypeError):
        pass

    # If no resume skills, try to extract from professional_json
    if not resume_skills:
        try:
            professional = json.loads(db_obj.professional_json or "{}")
            resume_skills = professional.get("primaryTechStack", [])
        except (json.JSONDecodeError, TypeError):
            pass

    try:
        from app.agents.verification_crew import run_verification

        result = run_verification(
            github_url=db_obj.github_url,
            role_applied=db_obj.role_applied,
            candidate_name=db_obj.full_name,
            resume_skills=resume_skills,
        )

        # Save results
        db_obj.trust_score = result.get("trust_score", 0.0)
        db_obj.verification_report_json = json.dumps(
            result.get("verification_report", {})
        )

        # Only overwrite training plan if crew produced one
        crew_plan = result.get("training_plan")
        if crew_plan and isinstance(crew_plan, dict) and crew_plan.get("weekly_plan"):
            db_obj.training_plan_json = json.dumps(crew_plan)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="CrewAI not installed. Install crewai and crewai-tools.",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Verification pipeline error: {str(exc)}",
        )
