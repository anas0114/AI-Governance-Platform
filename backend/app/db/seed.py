"""Seed the database with sample data for local development and demos.

Run with:  python -m app.db.seed
"""
import asyncio
import uuid
from datetime import date

from app.core.security import get_password_hash
from app.db.init_db import init_db
from app.db.session import AsyncSessionLocal
from app.models.ai_system import AISystem
from app.models.audit import Audit, AuditFinding
from app.models.compliance import ComplianceAssessment, ComplianceControl, ComplianceFramework
from app.models.policy import Policy
from app.models.regulation import Regulation, RegulationClause
from app.models.research import ResearchNote
from app.models.user import User


async def seed() -> None:
    await init_db()

    async with AsyncSessionLocal() as db:
        admin = User(
            id=uuid.uuid4(),
            email="admin@aigovernance.dev",
            full_name="Platform Admin",
            role="admin",
            hashed_password=get_password_hash("ChangeMe123!"),
        )
        db.add(admin)

        # --- Compliance frameworks & controls ---
        eu_ai_act = ComplianceFramework(name="EU AI Act", description="EU regulation on artificial intelligence.")
        nist_rmf = ComplianceFramework(name="NIST AI RMF", description="NIST AI Risk Management Framework.")
        iso_42001 = ComplianceFramework(name="ISO/IEC 42001", description="AI management system standard.")
        db.add_all([eu_ai_act, nist_rmf, iso_42001])
        await db.flush()

        controls = [
            ComplianceControl(framework_id=eu_ai_act.id, code="Art.9", title="Risk management system",
                               description="Establish and maintain a risk management system for high-risk AI."),
            ComplianceControl(framework_id=eu_ai_act.id, code="Art.10", title="Data and data governance",
                               description="Training, validation and testing data quality requirements."),
            ComplianceControl(framework_id=eu_ai_act.id, code="Art.13", title="Transparency",
                               description="High-risk AI systems must be transparent to users."),
            ComplianceControl(framework_id=nist_rmf.id, code="GOVERN 1.1", title="AI risk governance",
                               description="Legal/regulatory requirements involving AI are understood and managed."),
            ComplianceControl(framework_id=iso_42001.id, code="A.6.2", title="AI system impact assessment",
                               description="Assess impact of AI systems on individuals and society."),
        ]
        db.add_all(controls)

        # --- Regulations & clauses (Regulation Repository) ---
        eu_ai_act_reg = Regulation(
            title="EU Artificial Intelligence Act",
            jurisdiction="European Union",
            category="AI Act",
            summary="Risk-based regulatory framework for AI systems placed on the EU market.",
            source_url="https://artificialintelligenceact.eu/",
            effective_date=date(2024, 8, 1),
            status="in_force",
        )
        nist_reg = Regulation(
            title="NIST AI Risk Management Framework 1.0",
            jurisdiction="United States",
            category="Risk Management",
            summary="Voluntary framework to manage risks of AI systems across the lifecycle.",
            source_url="https://www.nist.gov/itl/ai-risk-management-framework",
            effective_date=date(2023, 1, 26),
            status="in_force",
        )
        db.add_all([eu_ai_act_reg, nist_reg])
        await db.flush()

        clauses = [
            RegulationClause(
                regulation_id=eu_ai_act_reg.id,
                clause_number="Article 9",
                title="Risk management system",
                text="A risk management system shall be established, implemented, documented and maintained "
                     "in relation to high-risk AI systems, run as a continuous iterative process.",
            ),
            RegulationClause(
                regulation_id=eu_ai_act_reg.id,
                clause_number="Article 13",
                title="Transparency and provision of information to users",
                text="High-risk AI systems shall be designed to ensure their operation is sufficiently "
                     "transparent to enable users to interpret the system's output and use it appropriately.",
            ),
            RegulationClause(
                regulation_id=nist_reg.id,
                clause_number="GOVERN 1.1",
                title="AI risk governance",
                text="Legal and regulatory requirements involving AI are understood, managed, and documented "
                     "as part of organizational risk management.",
            ),
        ]
        db.add_all(clauses)

        # --- AI Systems registry ---
        credit_scoring = AISystem(
            name="Credit Scoring Model",
            description="ML model used to assess consumer credit risk for loan approvals.",
            owner="Risk Analytics Team",
            risk_level="high",
            lifecycle_stage="production",
        )
        support_chatbot = AISystem(
            name="Customer Support Chatbot",
            description="LLM-based chatbot for tier-1 customer support triage.",
            owner="Customer Experience Team",
            risk_level="limited",
            lifecycle_stage="production",
        )
        resume_screener = AISystem(
            name="Resume Screening Assistant",
            description="Recommendation model that ranks job applicants for recruiters.",
            owner="Talent Acquisition",
            risk_level="high",
            lifecycle_stage="development",
        )
        db.add_all([credit_scoring, support_chatbot, resume_screener])
        await db.flush()

        # --- Policies (Policy Management) ---
        policies = [
            Policy(
                title="Responsible AI Usage Policy",
                description="Company-wide policy governing acceptable use of AI systems.",
                content="All AI systems must be registered, risk-classified, and reviewed before deployment.",
                version=2,
                status="approved",
                owner_id=admin.id,
            ),
            Policy(
                title="AI Data Governance Policy",
                description="Standards for training/validation data quality and lineage.",
                content="Training data must be documented, versioned, and reviewed for bias.",
                version=1,
                status="in_review",
                owner_id=admin.id,
            ),
            Policy(
                title="High-Risk AI System Approval Policy",
                description="Approval workflow required before releasing high-risk AI systems.",
                content="High-risk systems require a compliance assessment and sign-off from Legal.",
                version=1,
                status="draft",
                owner_id=admin.id,
            ),
        ]
        db.add_all(policies)

        # --- Compliance assessments ---
        assessments = [
            ComplianceAssessment(
                ai_system_id=credit_scoring.id, framework_id=eu_ai_act.id, status="in_progress", score="72%"
            ),
            ComplianceAssessment(
                ai_system_id=support_chatbot.id, framework_id=nist_rmf.id, status="passed", score="91%"
            ),
            ComplianceAssessment(
                ai_system_id=resume_screener.id, framework_id=eu_ai_act.id, status="failed", score="48%"
            ),
        ]
        db.add_all(assessments)

        # --- Audits & findings ---
        audit_1 = Audit(ai_system_id=credit_scoring.id, title="Q3 Credit Scoring Model Audit", status="in_progress")
        audit_2 = Audit(ai_system_id=resume_screener.id, title="Pre-launch Bias Audit", status="open")
        db.add_all([audit_1, audit_2])
        await db.flush()

        findings = [
            AuditFinding(
                audit_id=audit_1.id,
                severity="medium",
                description="Model documentation is missing data lineage details.",
                remediation="Add data lineage section to model card.",
                status="open",
            ),
            AuditFinding(
                audit_id=audit_2.id,
                severity="high",
                description="Evidence of disparate impact across demographic groups in screening scores.",
                remediation="Retrain with bias mitigation and re-evaluate fairness metrics.",
                status="open",
            ),
        ]
        db.add_all(findings)

        # --- Research workspace notes ---
        notes = [
            ResearchNote(
                title="EU AI Act high-risk obligations summary",
                content="Key obligations: risk management (Art.9), data governance (Art.10), "
                        "transparency (Art.13), human oversight, and conformity assessment before market entry.",
                tags="eu-ai-act,high-risk",
                author_id=admin.id,
            ),
            ResearchNote(
                title="NIST RMF mapping to internal controls",
                content="GOVERN function maps to our AI Steering Committee charter; MEASURE function maps "
                        "to our model validation pipeline metrics.",
                tags="nist,mapping",
                author_id=admin.id,
            ),
        ]
        db.add_all(notes)

        await db.commit()

    print("Seed data inserted successfully.")
    print("Login with: admin@aigovernance.dev / ChangeMe123!")


if __name__ == "__main__":
    asyncio.run(seed())
