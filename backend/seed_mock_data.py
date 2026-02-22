"""Seed the database with 15 realistic Indian mock profiles.

Usage:
    cd backend && .venv/bin/python seed_mock_data.py
"""

import json, sys, os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from app.database import SessionLocal, engine, Base
from app.models.application import Application

Base.metadata.create_all(bind=engine)


def _p(full_name, email, github_url, role_applied, status, master_score,
       confidence_band, personal, education, experience, professional,
       github_metrics, resume_analysis, score_breakdown, learning_gaps,
       background_report, motivation=None):
    """Build a profile dict with all JSON fields."""
    return {
        "full_name": full_name, "email": email, "github_url": github_url,
        "role_applied": role_applied, "status": status,
        "master_score": master_score, "confidence_band": confidence_band,
        "personal_json": json.dumps(personal),
        "education_json": json.dumps(education),
        "experience_json": json.dumps(experience),
        "professional_json": json.dumps(professional),
        "motivation_json": json.dumps(motivation or {}),
        "github_metrics_json": json.dumps(github_metrics),
        "resume_analysis_json": json.dumps(resume_analysis),
        "score_breakdown_json": json.dumps(score_breakdown),
        "learning_gaps_json": json.dumps(learning_gaps),
        "background_report_json": json.dumps(background_report),
    }


PROFILES = [
    # ═══════════════════════════════════════════════════════════════
    # 1. Arjun Sharma — Strong Backend — IIT Bombay
    # ═══════════════════════════════════════════════════════════════
    _p("Arjun Sharma", "arjun.sharma@iitb.ac.in", "https://github.com/arjunsharma",
       "Backend Developer", "pending", 78.2, "Strong",
       personal={"fullName":"Arjun Sharma","email":"arjun.sharma@iitb.ac.in","phone":"+91 9876543210","age":22,"location":"Bangalore, Karnataka"},
       education={"degree":"Bachelor's Degree","fieldOfStudy":"Computer Science","institution":"IIT Bombay","graduationYear":2025,"gpa":"8.7"},
       experience={"hasPreviousInternship":True,"company":"Infosys","duration":"3 months",
                   "projectLinks":[{"url":"https://github.com/arjunsharma/fastapi-blog","description":"Blog API with FastAPI, PostgreSQL, JWT auth"},
                                   {"url":"https://github.com/arjunsharma/task-manager","description":"Task management REST API with RBAC"}]},
       professional={"githubUrl":"https://github.com/arjunsharma","primaryTechStack":["Python","FastAPI","PostgreSQL","Docker","Redis"],"yearsOfExperience":1,"currentStatus":"Student"},
       github_metrics={"username":"arjunsharma","total_repos":18,"total_public_repos":18,"total_stars":23,
                       "top_repositories":[{"name":"fastapi-blog","stars":12,"language":"Python"},{"name":"task-manager","stars":8,"language":"Python"}],
                       "languages":{"Python":52.4,"JavaScript":18.1,"TypeScript":14.3,"Shell":8.7,"Dockerfile":6.5},
                       "last_activity":"2026-02-19T10:30:00Z","recent_activity_score_base":82,"commits_last_90_days":78},
       resume_analysis={"keywords_detected":["python","fastapi","django","postgresql","docker","redis","api","sql","git","rest"],"ats_score":82,"project_quality":75},
       score_breakdown={"resume_skill_score":24,"github_activity_score":21.5,"project_quality_score":15.8,"role_alignment_score":11.2,"recency_score":5.7,
                        "all_role_scores":{"backend":72,"frontend":28,"data":18,"full stack":52,"devops":35}},
       learning_gaps=["Strengthen frontend skills","Learn microservices & container orchestration"],
       background_report={"summary":"Arjun is a strong backend developer with solid Python/FastAPI foundation. 78 commits in 90 days across 18 repos. Previous Infosys internship adds real-world context. Strong with PostgreSQL, Docker, Redis. 8.7 CGPA from IIT Bombay.",
                          "strengths":["Strong Python/FastAPI expertise","78 commits in 90 days across 18 repos","Previous Infosys internship","Solid database & caching knowledge"],
                          "weaknesses":["Limited frontend experience","No microservices/K8s exposure"],
                          "risks":["May need system design guidance"],"growth_direction":"Microservices architecture, container orchestration, API security patterns."}),

    # ═══════════════════════════════════════════════════════════════
    # 2. Priya Patel — Good Frontend — VJTI Mumbai
    # ═══════════════════════════════════════════════════════════════
    _p("Priya Patel", "priya.patel@vjti.ac.in", "https://github.com/priyapatel",
       "Frontend Developer", "in_review", 72.5, "Good",
       personal={"fullName":"Priya Patel","email":"priya.patel@vjti.ac.in","phone":"+91 8765432109","age":21,"location":"Mumbai, Maharashtra"},
       education={"degree":"Bachelor's Degree","fieldOfStudy":"Information Technology","institution":"VJTI Mumbai","graduationYear":2026,"gpa":"8.2"},
       experience={"hasPreviousInternship":False,"projectLinks":[{"url":"https://github.com/priyapatel/portfolio-site","description":"Portfolio with React & Tailwind"},
                                                                  {"url":"https://github.com/priyapatel/expense-tracker","description":"Expense tracker with Next.js & charts"}]},
       professional={"githubUrl":"https://github.com/priyapatel","primaryTechStack":["React","TypeScript","Next.js","Tailwind","Figma"],"yearsOfExperience":0,"currentStatus":"Student"},
       github_metrics={"username":"priyapatel","total_repos":12,"total_public_repos":12,"total_stars":15,
                       "top_repositories":[{"name":"portfolio-site","stars":8,"language":"TypeScript"},{"name":"expense-tracker","stars":5,"language":"TypeScript"}],
                       "languages":{"TypeScript":38.5,"JavaScript":24.3,"CSS":19.8,"HTML":17.4},
                       "last_activity":"2026-02-20T08:15:00Z","recent_activity_score_base":68,"commits_last_90_days":52},
       resume_analysis={"keywords_detected":["react","typescript","javascript","html","css","next.js","tailwind","figma","git"],"ats_score":75,"project_quality":68},
       score_breakdown={"resume_skill_score":21,"github_activity_score":18.8,"project_quality_score":14.2,"role_alignment_score":12.5,"recency_score":6,
                        "all_role_scores":{"backend":15,"frontend":78,"data":8,"full stack":45,"devops":12}},
       learning_gaps=["Add backend skills","Learn state management (Redux, Zustand)"],
       background_report={"summary":"Priya is a promising frontend dev with strong React/TypeScript. Portfolio & expense tracker show practical UI ability. 52 commits in 90 days. Figma skills add UI/UX value. 8.2 CGPA from VJTI.",
                          "strengths":["Strong React/TypeScript","Good UI/UX with Figma","Active GitHub contributor"],
                          "weaknesses":["No internship experience","Limited backend knowledge","Needs state management depth"],
                          "risks":[],"growth_direction":"Frontend architecture, testing frameworks, basic backend exposure."}),

    # ═══════════════════════════════════════════════════════════════
    # 3. Rahul Verma — Strong Data Science — IIT Delhi
    # ═══════════════════════════════════════════════════════════════
    _p("Rahul Verma", "rahul.verma@iitd.ac.in", "https://github.com/rahulverma",
       "Data Science", "accepted", 85.1, "Strong",
       personal={"fullName":"Rahul Verma","email":"rahul.verma@iitd.ac.in","phone":"+91 7654321098","age":23,"location":"New Delhi"},
       education={"degree":"Master's Degree","fieldOfStudy":"Data Science","institution":"IIT Delhi","graduationYear":2025,"gpa":"9.1"},
       experience={"hasPreviousInternship":True,"company":"Microsoft Research India","duration":"6 months",
                   "projectLinks":[{"url":"https://github.com/rahulverma/sentiment-analyzer","description":"NLP sentiment analysis with transformers"},
                                   {"url":"https://github.com/rahulverma/stock-predictor","description":"LSTM stock price predictor"}]},
       professional={"githubUrl":"https://github.com/rahulverma","primaryTechStack":["Python","TensorFlow","PyTorch","Pandas","SQL"],"yearsOfExperience":2,"currentStatus":"Recent Graduate"},
       github_metrics={"username":"rahulverma","total_repos":25,"total_public_repos":25,"total_stars":42,
                       "top_repositories":[{"name":"sentiment-analyzer","stars":18,"language":"Python"},{"name":"stock-predictor","stars":14,"language":"Python"}],
                       "languages":{"Python":65.2,"Jupyter Notebook":20.8,"R":8.5,"SQL":5.5},
                       "last_activity":"2026-02-21T06:00:00Z","recent_activity_score_base":92,"commits_last_90_days":120},
       resume_analysis={"keywords_detected":["python","tensorflow","pytorch","pandas","numpy","sklearn","sql","jupyter","ml","data"],"ats_score":90,"project_quality":88},
       score_breakdown={"resume_skill_score":28.5,"github_activity_score":23.2,"project_quality_score":17.5,"role_alignment_score":13.8,"recency_score":2.1,
                        "all_role_scores":{"backend":35,"frontend":5,"data":88,"full stack":28,"devops":15}},
       learning_gaps=["Learn MLOps and model deployment at scale"],
       background_report={"summary":"Rahul is exceptional — MS from IIT Delhi (9.1 CGPA), 6-month Microsoft Research India internship. 42 stars, 120 commits in 90 days. Deep TensorFlow/PyTorch expertise with published-quality projects.",
                          "strengths":["Deep TensorFlow/PyTorch expertise","Microsoft Research India experience","120 commits in 90 days","9.1 CGPA from IIT Delhi"],
                          "weaknesses":["Limited MLOps/deployment experience"],"risks":[],"growth_direction":"MLOps, model serving, production data pipelines."}),

    # ═══════════════════════════════════════════════════════════════
    # 4. Sneha Kulkarni — Moderate Full Stack — COEP Pune
    # ═══════════════════════════════════════════════════════════════
    _p("Sneha Kulkarni", "sneha.k@coep.ac.in", "https://github.com/snehakulkarni",
       "Full Stack Developer", "pending", 64.8, "Good",
       personal={"fullName":"Sneha Kulkarni","email":"sneha.k@coep.ac.in","phone":"+91 6543210987","age":20,"location":"Pune, Maharashtra"},
       education={"degree":"Bachelor's Degree","fieldOfStudy":"Computer Engineering","institution":"COEP Pune","graduationYear":2027,"gpa":"7.8"},
       experience={"hasPreviousInternship":False,"projectLinks":[{"url":"https://github.com/snehakulkarni/todo-app","description":"Full stack todo with React + Express"},
                                                                  {"url":"https://github.com/snehakulkarni/weather-dashboard","description":"Weather dashboard with OpenWeather API"}]},
       professional={"githubUrl":"https://github.com/snehakulkarni","primaryTechStack":["JavaScript","React","Node.js","MongoDB"],"yearsOfExperience":0,"currentStatus":"Student"},
       github_metrics={"username":"snehakulkarni","total_repos":8,"total_public_repos":8,"total_stars":6,
                       "top_repositories":[{"name":"todo-app","stars":3,"language":"JavaScript"},{"name":"weather-dashboard","stars":2,"language":"JavaScript"}],
                       "languages":{"JavaScript":45.2,"HTML":22.0,"CSS":18.8,"Python":14.0},
                       "last_activity":"2026-02-15T12:00:00Z","recent_activity_score_base":55,"commits_last_90_days":35},
       resume_analysis={"keywords_detected":["javascript","react","node.js","mongodb","html","css","git","api"],"ats_score":62,"project_quality":55},
       score_breakdown={"resume_skill_score":18,"github_activity_score":15.5,"project_quality_score":12.8,"role_alignment_score":10.5,"recency_score":8,
                        "all_role_scores":{"backend":25,"frontend":55,"data":5,"full stack":48,"devops":8}},
       learning_gaps=["Improve project documentation","Strengthen backend & DB skills","Learn TypeScript"],
       background_report={"summary":"Sneha is an early-career full stack dev from COEP Pune. 8 repos with working todo app and weather dashboard. 35 commits in 90 days — moderate but growing. Good candidate for structured training.",
                          "strengths":["Working full-stack projects","Solid JavaScript/React foundation","Growing GitHub pattern"],
                          "weaknesses":["No professional experience","Limited backend depth","Projects lack docs/tests"],
                          "risks":["May need extra initial mentoring"],"growth_direction":"TypeScript adoption, Express/FastAPI depth, database design."}),

    # ═══════════════════════════════════════════════════════════════
    # 5. Vikram Joshi — Risk DevOps — MNIT Jaipur
    # ═══════════════════════════════════════════════════════════════
    _p("Vikram Joshi", "vikram.joshi@mnit.ac.in", "https://github.com/vikramjoshi",
       "DevOps Engineer", "rejected", 42.3, "Risk",
       personal={"fullName":"Vikram Joshi","email":"vikram.joshi@mnit.ac.in","phone":"+91 5432109876","age":24,"location":"Jaipur, Rajasthan"},
       education={"degree":"Bachelor's Degree","fieldOfStudy":"Mechanical Engineering","institution":"MNIT Jaipur","graduationYear":2024,"gpa":"6.5"},
       experience={"hasPreviousInternship":False,"projectLinks":[{"url":"https://github.com/vikramjoshi/hello-docker","description":"Docker containerization tutorial"},
                                                                  {"url":"https://github.com/vikramjoshi/linux-scripts","description":"Bash utility scripts"}]},
       professional={"githubUrl":"https://github.com/vikramjoshi","primaryTechStack":["Linux","Docker","Shell"],"yearsOfExperience":0,"currentStatus":"Recent Graduate"},
       github_metrics={"username":"vikramjoshi","total_repos":4,"total_public_repos":4,"total_stars":1,
                       "top_repositories":[{"name":"hello-docker","stars":1,"language":"Dockerfile"}],
                       "languages":{"Shell":42.0,"Dockerfile":28.0,"Python":30.0},
                       "last_activity":"2026-01-10T09:00:00Z","recent_activity_score_base":18,"commits_last_90_days":8},
       resume_analysis={"keywords_detected":["linux","docker","shell","git"],"ats_score":35,"project_quality":25},
       score_breakdown={"resume_skill_score":9,"github_activity_score":8.5,"project_quality_score":7.8,"role_alignment_score":6,"recency_score":11,
                        "all_role_scores":{"backend":12,"frontend":3,"data":5,"full stack":10,"devops":28}},
       learning_gaps=["Learn a programming language properly","Increase coding consistency","Build visible projects","Strengthen DevOps skills"],
       background_report={"summary":"Vikram is a mechanical engineering grad from MNIT Jaipur switching to DevOps. Only 4 repos, 1 star, 8 commits in 90 days. Basic Docker/Linux but very early stage. Steep learning curve ahead.",
                          "strengths":["Interest in DevOps","Basic Docker/Linux exposure"],
                          "weaknesses":["Very limited coding experience","Non-CS background","Minimal GitHub activity","No CI/CD or cloud experience"],
                          "risks":["Career switcher with steep learning curve","May struggle with programming fundamentals"],
                          "growth_direction":"Python basics → Docker → CI/CD → cloud fundamentals."}),

    # ═══════════════════════════════════════════════════════════════
    # 6. Ananya Krishnan — Good Backend — Anna University
    # ═══════════════════════════════════════════════════════════════
    _p("Ananya Krishnan", "ananya.k@annauniv.edu", "https://github.com/ananyak",
       "Backend Developer", "in_review", 68.9, "Good",
       personal={"fullName":"Ananya Krishnan","email":"ananya.k@annauniv.edu","phone":"+91 4321098765","age":22,"location":"Chennai, Tamil Nadu"},
       education={"degree":"Bachelor's Degree","fieldOfStudy":"Computer Science","institution":"Anna University, Chennai","graduationYear":2026,"gpa":"8.0"},
       experience={"hasPreviousInternship":True,"company":"Zoho Corporation","duration":"2 months",
                   "projectLinks":[{"url":"https://github.com/ananyak/ecommerce-api","description":"E-commerce REST API with Django"},
                                   {"url":"https://github.com/ananyak/chat-app","description":"Real-time chat with WebSockets"}]},
       professional={"githubUrl":"https://github.com/ananyak","primaryTechStack":["Python","Django","PostgreSQL","JavaScript","Docker"],"yearsOfExperience":1,"currentStatus":"Student"},
       github_metrics={"username":"ananyak","total_repos":14,"total_public_repos":14,"total_stars":18,
                       "top_repositories":[{"name":"ecommerce-api","stars":9,"language":"Python"},{"name":"chat-app","stars":6,"language":"JavaScript"}],
                       "languages":{"Python":44.5,"JavaScript":25.0,"HTML":14.5,"CSS":9.0,"Shell":7.0},
                       "last_activity":"2026-02-18T14:30:00Z","recent_activity_score_base":72,"commits_last_90_days":62},
       resume_analysis={"keywords_detected":["python","django","postgresql","javascript","docker","api","sql","rest","git"],"ats_score":78,"project_quality":72},
       score_breakdown={"resume_skill_score":22,"github_activity_score":19.2,"project_quality_score":13.5,"role_alignment_score":9.8,"recency_score":4.4,
                        "all_role_scores":{"backend":65,"frontend":35,"data":12,"full stack":55,"devops":22}},
       learning_gaps=["Explore FastAPI","Learn caching & message queues"],
       background_report={"summary":"Ananya is a well-rounded backend dev with Django experience from Zoho. 14 repos, e-commerce API and chat app showcase real-world skills. 8.0 CGPA, 62 commits in 90 days. Good cross-functional potential.",
                          "strengths":["Practical Django/PostgreSQL from Zoho internship","Real-world projects","Cross-functional Python/JS skills","62 commits in 90 days"],
                          "weaknesses":["Limited to Django only","No caching/queue experience"],
                          "risks":[],"growth_direction":"FastAPI, Redis caching, message queues for scalable systems."}),

    # ═══════════════════════════════════════════════════════════════
    # 7. Deepak Reddy — Strong DevOps — IIIT Hyderabad
    # ═══════════════════════════════════════════════════════════════
    _p("Deepak Reddy", "deepak.r@iiith.ac.in", "https://github.com/deepakreddy",
       "DevOps Engineer", "pending", 76.4, "Strong",
       personal={"fullName":"Deepak Reddy","email":"deepak.r@iiith.ac.in","phone":"+91 9988776655","age":23,"location":"Hyderabad, Telangana"},
       education={"degree":"Bachelor's Degree","fieldOfStudy":"Computer Science","institution":"IIIT Hyderabad","graduationYear":2025,"gpa":"8.4"},
       experience={"hasPreviousInternship":True,"company":"Razorpay","duration":"4 months",
                   "projectLinks":[{"url":"https://github.com/deepakreddy/k8s-deploy","description":"Kubernetes deployment automation with Helm charts"},
                                   {"url":"https://github.com/deepakreddy/ci-pipeline","description":"GitHub Actions CI/CD pipeline for microservices"}]},
       professional={"githubUrl":"https://github.com/deepakreddy","primaryTechStack":["Docker","Kubernetes","Terraform","AWS","Python"],"yearsOfExperience":1,"currentStatus":"Student"},
       github_metrics={"username":"deepakreddy","total_repos":16,"total_public_repos":16,"total_stars":28,
                       "top_repositories":[{"name":"k8s-deploy","stars":15,"language":"Python"},{"name":"ci-pipeline","stars":8,"language":"Shell"}],
                       "languages":{"Python":35.0,"Shell":28.0,"YAML":18.0,"Dockerfile":12.0,"Go":7.0},
                       "last_activity":"2026-02-20T16:00:00Z","recent_activity_score_base":85,"commits_last_90_days":90},
       resume_analysis={"keywords_detected":["docker","kubernetes","terraform","aws","python","ci/cd","github actions","helm","linux","shell"],"ats_score":85,"project_quality":80},
       score_breakdown={"resume_skill_score":25,"github_activity_score":20.5,"project_quality_score":15,"role_alignment_score":11,"recency_score":4.9,
                        "all_role_scores":{"backend":40,"frontend":5,"data":10,"full stack":30,"devops":82}},
       learning_gaps=["Learn monitoring & observability tools (Prometheus, Grafana)"],
       background_report={"summary":"Deepak is a strong DevOps candidate from IIIT Hyderabad with Razorpay internship experience. K8s deployment automation and CI/CD pipeline projects show real infrastructure skills. 90 commits in 90 days, 28 stars. 8.4 CGPA.",
                          "strengths":["Kubernetes & Terraform expertise","Razorpay internship experience","Strong CI/CD pipeline knowledge","90 commits in 90 days"],
                          "weaknesses":["Limited monitoring/observability experience"],
                          "risks":[],"growth_direction":"Monitoring (Prometheus/Grafana), service mesh, cloud cost optimization."}),

    # ═══════════════════════════════════════════════════════════════
    # 8. Kavya Nair — Good Data Science — IISc Bangalore
    # ═══════════════════════════════════════════════════════════════
    _p("Kavya Nair", "kavya.nair@iisc.ac.in", "https://github.com/kavyanair",
       "Data Science", "pending", 74.3, "Good",
       personal={"fullName":"Kavya Nair","email":"kavya.nair@iisc.ac.in","phone":"+91 8877665544","age":22,"location":"Bangalore, Karnataka"},
       education={"degree":"Bachelor's Degree","fieldOfStudy":"Mathematics & Computing","institution":"IISc Bangalore","graduationYear":2026,"gpa":"8.8"},
       experience={"hasPreviousInternship":False,"projectLinks":[{"url":"https://github.com/kavyanair/image-classifier","description":"CNN image classifier with 95% accuracy on CIFAR-10"},
                                                                  {"url":"https://github.com/kavyanair/recommendation-engine","description":"Collaborative filtering recommendation system"}]},
       professional={"githubUrl":"https://github.com/kavyanair","primaryTechStack":["Python","PyTorch","scikit-learn","Pandas","NumPy"],"yearsOfExperience":0,"currentStatus":"Student"},
       github_metrics={"username":"kavyanair","total_repos":11,"total_public_repos":11,"total_stars":16,
                       "top_repositories":[{"name":"image-classifier","stars":9,"language":"Python"},{"name":"recommendation-engine","stars":5,"language":"Python"}],
                       "languages":{"Python":60.0,"Jupyter Notebook":25.0,"Shell":10.0,"Markdown":5.0},
                       "last_activity":"2026-02-19T11:00:00Z","recent_activity_score_base":70,"commits_last_90_days":55},
       resume_analysis={"keywords_detected":["python","pytorch","scikit-learn","pandas","numpy","cnn","ml","data","statistics"],"ats_score":76,"project_quality":70},
       score_breakdown={"resume_skill_score":22,"github_activity_score":18,"project_quality_score":14,"role_alignment_score":12,"recency_score":8.3,
                        "all_role_scores":{"backend":20,"frontend":5,"data":75,"full stack":18,"devops":8}},
       learning_gaps=["Learn NLP & transformer architectures","Build end-to-end ML pipelines"],
       background_report={"summary":"Kavya from IISc Bangalore (8.8 CGPA) shows strong ML fundamentals. Image classifier with 95% accuracy and recommendation engine demonstrate practical skills. 55 commits, 16 stars. Strong math background is an asset.",
                          "strengths":["Strong mathematical foundation from IISc","Practical ML projects with good accuracy","PyTorch proficiency","Good academic record"],
                          "weaknesses":["No internship experience","Hasn't explored NLP/transformers","Limited deployment knowledge"],
                          "risks":[],"growth_direction":"NLP/transformers, end-to-end ML pipelines, model deployment."}),

    # ═══════════════════════════════════════════════════════════════
    # 9. Amit Gupta — Moderate Frontend — NIT Trichy
    # ═══════════════════════════════════════════════════════════════
    _p("Amit Gupta", "amit.g@nitt.edu", "https://github.com/amitgupta",
       "Frontend Developer", "pending", 58.5, "Moderate",
       personal={"fullName":"Amit Gupta","email":"amit.g@nitt.edu","phone":"+91 7766554433","age":21,"location":"Trichy, Tamil Nadu"},
       education={"degree":"Bachelor's Degree","fieldOfStudy":"Electronics & Communication","institution":"NIT Trichy","graduationYear":2026,"gpa":"7.5"},
       experience={"hasPreviousInternship":False,"projectLinks":[{"url":"https://github.com/amitgupta/landing-pages","description":"Collection of responsive landing pages"},
                                                                  {"url":"https://github.com/amitgupta/quiz-app","description":"Interactive quiz app with vanilla JS"}]},
       professional={"githubUrl":"https://github.com/amitgupta","primaryTechStack":["HTML","CSS","JavaScript","React"],"yearsOfExperience":0,"currentStatus":"Student"},
       github_metrics={"username":"amitgupta","total_repos":7,"total_public_repos":7,"total_stars":4,
                       "top_repositories":[{"name":"landing-pages","stars":2,"language":"HTML"},{"name":"quiz-app","stars":2,"language":"JavaScript"}],
                       "languages":{"JavaScript":35.0,"HTML":30.0,"CSS":25.0,"Python":10.0},
                       "last_activity":"2026-02-12T09:00:00Z","recent_activity_score_base":45,"commits_last_90_days":25},
       resume_analysis={"keywords_detected":["html","css","javascript","react","responsive","git"],"ats_score":55,"project_quality":45},
       score_breakdown={"resume_skill_score":15,"github_activity_score":13,"project_quality_score":11,"role_alignment_score":10,"recency_score":9.5,
                        "all_role_scores":{"backend":10,"frontend":52,"data":3,"full stack":28,"devops":5}},
       learning_gaps=["Learn TypeScript","Deepen React knowledge","Build more complex projects","Learn testing"],
       background_report={"summary":"Amit from NIT Trichy is transitioning from ECE to frontend development. 7 repos with basic landing pages and a quiz app. 25 commits in 90 days — needs more consistency. Shows potential but needs structured guidance.",
                          "strengths":["Good HTML/CSS fundamentals","Interest in frontend development","Clean responsive designs"],
                          "weaknesses":["Non-CS background","Limited project complexity","Low GitHub activity","No TypeScript experience"],
                          "risks":["ECE background may slow initial progress"],"growth_direction":"TypeScript, React component patterns, testing, CSS frameworks."}),

    # ═══════════════════════════════════════════════════════════════
    # 10. Meera Iyer — Strong Full Stack — BITS Pilani
    # ═══════════════════════════════════════════════════════════════
    _p("Meera Iyer", "meera.iyer@bits-pilani.ac.in", "https://github.com/meeraiyer",
       "Full Stack Developer", "accepted", 81.6, "Strong",
       personal={"fullName":"Meera Iyer","email":"meera.iyer@bits-pilani.ac.in","phone":"+91 6655443322","age":22,"location":"Goa"},
       education={"degree":"Bachelor's Degree","fieldOfStudy":"Computer Science","institution":"BITS Pilani, Goa","graduationYear":2025,"gpa":"9.0"},
       experience={"hasPreviousInternship":True,"company":"Flipkart","duration":"6 months",
                   "projectLinks":[{"url":"https://github.com/meeraiyer/social-app","description":"Social media app with React, Node.js, MongoDB, real-time notifications"},
                                   {"url":"https://github.com/meeraiyer/dev-dashboard","description":"Developer productivity dashboard with GitHub API integration"}]},
       professional={"githubUrl":"https://github.com/meeraiyer","primaryTechStack":["TypeScript","React","Node.js","PostgreSQL","Docker"],"yearsOfExperience":1,"currentStatus":"Student"},
       github_metrics={"username":"meeraiyer","total_repos":22,"total_public_repos":22,"total_stars":35,
                       "top_repositories":[{"name":"social-app","stars":18,"language":"TypeScript"},{"name":"dev-dashboard","stars":12,"language":"TypeScript"}],
                       "languages":{"TypeScript":42.0,"JavaScript":22.0,"Python":15.0,"CSS":12.0,"HTML":9.0},
                       "last_activity":"2026-02-21T08:00:00Z","recent_activity_score_base":88,"commits_last_90_days":105},
       resume_analysis={"keywords_detected":["typescript","react","node.js","postgresql","docker","api","mongodb","html","css","git","rest","graphql"],"ats_score":88,"project_quality":85},
       score_breakdown={"resume_skill_score":26,"github_activity_score":22,"project_quality_score":16.5,"role_alignment_score":12,"recency_score":5.1,
                        "all_role_scores":{"backend":62,"frontend":72,"data":12,"full stack":85,"devops":25}},
       learning_gaps=["Learn system design for distributed systems"],
       background_report={"summary":"Meera from BITS Pilani (9.0 CGPA) with Flipkart internship is a standout full-stack candidate. Social app and dev dashboard show strong end-to-end skills. 105 commits in 90 days, 35 stars across 22 repos. TypeScript-first approach.",
                          "strengths":["Flipkart internship with production exposure","Strong TypeScript/React/Node.js stack","105 commits in 90 days","Full-stack projects with real complexity"],
                          "weaknesses":["Limited system design for distributed systems"],
                          "risks":[],"growth_direction":"System design, distributed systems, microservices architecture."}),

    # ═══════════════════════════════════════════════════════════════
    # 11. Rohan Das — Moderate Backend — Jadavpur University
    # ═══════════════════════════════════════════════════════════════
    _p("Rohan Das", "rohan.das@jadavpur.edu", "https://github.com/rohandas",
       "Backend Developer", "pending", 61.2, "Good",
       personal={"fullName":"Rohan Das","email":"rohan.das@jadavpur.edu","phone":"+91 5544332211","age":21,"location":"Kolkata, West Bengal"},
       education={"degree":"Bachelor's Degree","fieldOfStudy":"Computer Science","institution":"Jadavpur University","graduationYear":2026,"gpa":"7.6"},
       experience={"hasPreviousInternship":False,"projectLinks":[{"url":"https://github.com/rohandas/flask-notes","description":"Note-taking API with Flask and SQLite"},
                                                                  {"url":"https://github.com/rohandas/url-shortener","description":"URL shortener service with Python"}]},
       professional={"githubUrl":"https://github.com/rohandas","primaryTechStack":["Python","Flask","SQLite","Git"],"yearsOfExperience":0,"currentStatus":"Student"},
       github_metrics={"username":"rohandas","total_repos":9,"total_public_repos":9,"total_stars":7,
                       "top_repositories":[{"name":"flask-notes","stars":4,"language":"Python"},{"name":"url-shortener","stars":3,"language":"Python"}],
                       "languages":{"Python":55.0,"HTML":20.0,"JavaScript":15.0,"CSS":10.0},
                       "last_activity":"2026-02-16T13:00:00Z","recent_activity_score_base":58,"commits_last_90_days":38},
       resume_analysis={"keywords_detected":["python","flask","sqlite","sql","api","git","html"],"ats_score":60,"project_quality":52},
       score_breakdown={"resume_skill_score":17,"github_activity_score":14.5,"project_quality_score":12,"role_alignment_score":9.5,"recency_score":8.2,
                        "all_role_scores":{"backend":55,"frontend":18,"data":15,"full stack":35,"devops":12}},
       learning_gaps=["Move from Flask to FastAPI/Django","Learn PostgreSQL","Add authentication to projects","Write tests"],
       background_report={"summary":"Rohan from Jadavpur University builds basic Python APIs. Flask notes app and URL shortener show foundational backend skills. 38 commits, 7 stars. Needs to level up to production-grade tools.",
                          "strengths":["Solid Python fundamentals","Working API projects","Growing contribution pattern"],
                          "weaknesses":["Only uses Flask/SQLite (no production DBs)","No authentication/security knowledge","Projects lack tests"],
                          "risks":["May need time to transition to production tools"],"growth_direction":"FastAPI/Django, PostgreSQL, authentication patterns, testing."}),

    # ═══════════════════════════════════════════════════════════════
    # 12. Nisha Agarwal — Risk Frontend — DTU Delhi
    # ═══════════════════════════════════════════════════════════════
    _p("Nisha Agarwal", "nisha.a@dtu.ac.in", "https://github.com/nishaagarwal",
       "Frontend Developer", "rejected", 38.5, "Risk",
       personal={"fullName":"Nisha Agarwal","email":"nisha.a@dtu.ac.in","phone":"+91 4433221100","age":20,"location":"Delhi"},
       education={"degree":"Bachelor's Degree","fieldOfStudy":"Software Engineering","institution":"DTU Delhi","graduationYear":2027,"gpa":"6.8"},
       experience={"hasPreviousInternship":False,"projectLinks":[{"url":"https://github.com/nishaagarwal/my-portfolio","description":"Simple HTML/CSS portfolio page"}]},
       professional={"githubUrl":"https://github.com/nishaagarwal","primaryTechStack":["HTML","CSS"],"yearsOfExperience":0,"currentStatus":"Student"},
       github_metrics={"username":"nishaagarwal","total_repos":3,"total_public_repos":3,"total_stars":0,
                       "top_repositories":[{"name":"my-portfolio","stars":0,"language":"HTML"}],
                       "languages":{"HTML":50.0,"CSS":40.0,"JavaScript":10.0},
                       "last_activity":"2026-01-05T10:00:00Z","recent_activity_score_base":12,"commits_last_90_days":5},
       resume_analysis={"keywords_detected":["html","css","git"],"ats_score":28,"project_quality":18},
       score_breakdown={"resume_skill_score":7,"github_activity_score":6.5,"project_quality_score":6,"role_alignment_score":8,"recency_score":11,
                        "all_role_scores":{"backend":3,"frontend":22,"data":2,"full stack":12,"devops":2}},
       learning_gaps=["Learn JavaScript properly","Build interactive projects","Increase GitHub activity significantly","Learn a frontend framework (React)"],
       background_report={"summary":"Nisha from DTU Delhi is very early in her frontend journey. Only 3 repos, 0 stars, 5 commits in 90 days. Only HTML/CSS with no JavaScript framework knowledge. Needs foundational work before an internship would be productive.",
                          "strengths":["Interest in web development","Clean HTML/CSS structure"],
                          "weaknesses":["No JavaScript frameworks","Extremely low GitHub activity","No interactive project experience","Very limited portfolio"],
                          "risks":["Not ready for internship-level work","Would need extensive foundational training"],
                          "growth_direction":"JavaScript fundamentals → React basics → Build 3-4 interactive projects → TypeScript."}),

    # ═══════════════════════════════════════════════════════════════
    # 13. Siddharth Menon — Good Backend — IIIT Bangalore
    # ═══════════════════════════════════════════════════════════════
    _p("Siddharth Menon", "sid.menon@iiitb.ac.in", "https://github.com/sidmenon",
       "Backend Developer", "in_review", 70.3, "Good",
       personal={"fullName":"Siddharth Menon","email":"sid.menon@iiitb.ac.in","phone":"+91 9911223344","age":22,"location":"Bangalore, Karnataka"},
       education={"degree":"Bachelor's Degree","fieldOfStudy":"Computer Science","institution":"IIIT Bangalore","graduationYear":2025,"gpa":"8.3"},
       experience={"hasPreviousInternship":True,"company":"ThoughtWorks","duration":"3 months",
                   "projectLinks":[{"url":"https://github.com/sidmenon/microservice-auth","description":"JWT auth microservice with Go"},
                                   {"url":"https://github.com/sidmenon/event-driven-api","description":"Event-driven API with RabbitMQ"}]},
       professional={"githubUrl":"https://github.com/sidmenon","primaryTechStack":["Go","Python","PostgreSQL","RabbitMQ","Docker"],"yearsOfExperience":1,"currentStatus":"Student"},
       github_metrics={"username":"sidmenon","total_repos":15,"total_public_repos":15,"total_stars":20,
                       "top_repositories":[{"name":"microservice-auth","stars":10,"language":"Go"},{"name":"event-driven-api","stars":7,"language":"Python"}],
                       "languages":{"Go":38.0,"Python":30.0,"Shell":15.0,"Dockerfile":10.0,"SQL":7.0},
                       "last_activity":"2026-02-20T18:00:00Z","recent_activity_score_base":78,"commits_last_90_days":72},
       resume_analysis={"keywords_detected":["go","golang","python","postgresql","rabbitmq","docker","microservices","jwt","api","git"],"ats_score":80,"project_quality":75},
       score_breakdown={"resume_skill_score":23,"github_activity_score":19,"project_quality_score":14,"role_alignment_score":10,"recency_score":4.3,
                        "all_role_scores":{"backend":70,"frontend":8,"data":12,"full stack":42,"devops":45}},
       learning_gaps=["Learn Kubernetes for container orchestration","Explore gRPC for inter-service communication"],
       background_report={"summary":"Siddharth from IIIT Bangalore with ThoughtWorks internship brings microservices experience. Auth service in Go and event-driven API show advanced backend thinking. 72 commits, 20 stars, 8.3 CGPA.",
                          "strengths":["Go + Python dual-language proficiency","Microservices and event-driven architecture experience","ThoughtWorks internship","Message queue (RabbitMQ) knowledge"],
                          "weaknesses":["No Kubernetes experience","Limited frontend skills"],
                          "risks":[],"growth_direction":"Kubernetes, gRPC, distributed tracing, system design."}),

    # ═══════════════════════════════════════════════════════════════
    # 14. Tanvi Deshmukh — Good Full Stack — PICT Pune
    # ═══════════════════════════════════════════════════════════════
    _p("Tanvi Deshmukh", "tanvi.d@pict.edu", "https://github.com/tanvideshmukh",
       "Full Stack Developer", "in_review", 66.7, "Good",
       personal={"fullName":"Tanvi Deshmukh","email":"tanvi.d@pict.edu","phone":"+91 8899001122","age":21,"location":"Pune, Maharashtra"},
       education={"degree":"Bachelor's Degree","fieldOfStudy":"Information Technology","institution":"PICT Pune","graduationYear":2026,"gpa":"8.1"},
       experience={"hasPreviousInternship":True,"company":"Persistent Systems","duration":"2 months",
                   "projectLinks":[{"url":"https://github.com/tanvideshmukh/food-delivery","description":"Food delivery app with React Native and Node.js backend"},
                                   {"url":"https://github.com/tanvideshmukh/blog-cms","description":"Blog CMS with Next.js and Prisma ORM"}]},
       professional={"githubUrl":"https://github.com/tanvideshmukh","primaryTechStack":["TypeScript","React","Next.js","Node.js","Prisma"],"yearsOfExperience":1,"currentStatus":"Student"},
       github_metrics={"username":"tanvideshmukh","total_repos":13,"total_public_repos":13,"total_stars":14,
                       "top_repositories":[{"name":"food-delivery","stars":7,"language":"TypeScript"},{"name":"blog-cms","stars":5,"language":"TypeScript"}],
                       "languages":{"TypeScript":40.0,"JavaScript":25.0,"CSS":18.0,"HTML":10.0,"Python":7.0},
                       "last_activity":"2026-02-17T15:00:00Z","recent_activity_score_base":65,"commits_last_90_days":48},
       resume_analysis={"keywords_detected":["typescript","react","next.js","node.js","prisma","postgresql","html","css","git","react native"],"ats_score":72,"project_quality":65},
       score_breakdown={"resume_skill_score":20,"github_activity_score":17,"project_quality_score":13,"role_alignment_score":11,"recency_score":5.7,
                        "all_role_scores":{"backend":38,"frontend":60,"data":8,"full stack":68,"devops":10}},
       learning_gaps=["Learn Docker and deployment","Strengthen database design skills","Add testing to projects"],
       background_report={"summary":"Tanvi from PICT Pune with Persistent Systems internship builds cross-platform apps. Food delivery app (React Native + Node.js) and blog CMS (Next.js + Prisma) show full-stack capability. 48 commits, 14 stars, 8.1 CGPA.",
                          "strengths":["Full-stack TypeScript projects","React Native mobile experience","Persistent Systems internship","Prisma/Next.js modern stack knowledge"],
                          "weaknesses":["No Docker/deployment experience","Limited database design knowledge","Projects lack tests"],
                          "risks":[],"growth_direction":"Docker, database design, testing strategies, CI/CD basics."}),

    # ═══════════════════════════════════════════════════════════════
    # 15. Karthik Rajan — Moderate Data Science — VIT Vellore
    # ═══════════════════════════════════════════════════════════════
    _p("Karthik Rajan", "karthik.r@vit.ac.in", "https://github.com/karthikrajan",
       "Data Science", "pending", 56.8, "Moderate",
       personal={"fullName":"Karthik Rajan","email":"karthik.r@vit.ac.in","phone":"+91 7788990011","age":21,"location":"Vellore, Tamil Nadu"},
       education={"degree":"Bachelor's Degree","fieldOfStudy":"Data Science","institution":"VIT Vellore","graduationYear":2026,"gpa":"7.4"},
       experience={"hasPreviousInternship":False,"projectLinks":[{"url":"https://github.com/karthikrajan/titanic-analysis","description":"Titanic survival prediction with ensemble methods"},
                                                                  {"url":"https://github.com/karthikrajan/covid-dashboard","description":"COVID-19 India dashboard with Plotly"}]},
       professional={"githubUrl":"https://github.com/karthikrajan","primaryTechStack":["Python","Pandas","scikit-learn","Matplotlib"],"yearsOfExperience":0,"currentStatus":"Student"},
       github_metrics={"username":"karthikrajan","total_repos":6,"total_public_repos":6,"total_stars":5,
                       "top_repositories":[{"name":"titanic-analysis","stars":3,"language":"Python"},{"name":"covid-dashboard","stars":2,"language":"Python"}],
                       "languages":{"Python":55.0,"Jupyter Notebook":35.0,"HTML":10.0},
                       "last_activity":"2026-02-10T10:00:00Z","recent_activity_score_base":40,"commits_last_90_days":22},
       resume_analysis={"keywords_detected":["python","pandas","scikit-learn","matplotlib","data","analysis","ml","git"],"ats_score":55,"project_quality":48},
       score_breakdown={"resume_skill_score":15,"github_activity_score":12.5,"project_quality_score":10.5,"role_alignment_score":10.8,"recency_score":8,
                        "all_role_scores":{"backend":12,"frontend":5,"data":55,"full stack":15,"devops":5}},
       learning_gaps=["Move beyond Kaggle-style projects","Learn deep learning frameworks","Build end-to-end data pipelines","Increase project complexity"],
       background_report={"summary":"Karthik from VIT Vellore shows interest in data science with Titanic prediction and COVID dashboard. 6 repos, 22 commits in 90 days. Projects are tutorial-level — needs to build more complex, original work.",
                          "strengths":["Python/Pandas fundamentals","Data visualization experience","Interest in ML"],
                          "weaknesses":["Projects are tutorial-level (Titanic, COVID)","No deep learning experience","Low GitHub activity","No production data experience"],
                          "risks":["May need significant upskilling before being productive"],"growth_direction":"Original datasets, deep learning (PyTorch), feature engineering, end-to-end pipelines."}),
]


def seed():
    db = SessionLocal()
    try:
        count = db.query(Application).count()
        if count > 0:
            print(f"Database already has {count} applications. Skipping mock data seed.")
            return

        for profile in PROFILES:
            app = Application(**profile)
            db.add(app)
        db.commit()
        print(f"✅ Seeded {len(PROFILES)} mock profiles")
        count = db.query(Application).count()
        print(f"   Total: {count}")
        for app in db.query(Application).all():
            gm = json.loads(app.github_metrics_json or "{}")
            sb = json.loads(app.score_breakdown_json or "{}")
            langs = gm.get("languages", {})
            roles = sb.get("all_role_scores", {})
            print(f"   {app.id:2d}. {app.full_name:20s} | {app.role_applied:22s} | score={app.master_score:5.1f} | {app.status:10s} | langs sum={sum(langs.values()):.1f}% | roles={len(roles)}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
