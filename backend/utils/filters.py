"""Job filtering using whitelist/blacklist system based on user preferences.

Key rules:
1. IT roles: Include general IT, exclude support/helpdesk/service desk
2. Finance: Only "Financial Technology/FinTech" - exclude pure finance
3. Engineering: Include software/data/embedded, exclude mechanical/civil/structural/generic
4. Research: Exclude PhD/Research Scientist, but include "Applied AI/ML"
5. Support roles: Hard exclude all support/helpdesk/service desk
6. Analyst roles: Include Technical/Business/Data/Information Analyst, exclude Risk/Financial Analyst
7. Generic titles: Include "Technology Intern", "Digital Intern", exclude "Engineering Intern"
8. AI roles: Include all AI-related (AI Ops, AI Transformation, Applied AI)
9. Cybersecurity: Include all cybersecurity roles
10. NO neutral pass-through - must match whitelist to be included
"""
import re
from typing import List
from backend.models.job import JobData


# =============================================================================
# INTERNSHIP DETECTION
# =============================================================================

INTERNSHIP_KEYWORDS = ["intern", "co-op", "coop", "internship", "student", "summer student"]

# Keywords that MUST NOT be in title (senior/lead roles)
SENIORITY_EXCLUDE = ["senior", "sr.", "lead", "manager", "director", "principal", "staff"]


# =============================================================================
# TITLE WHITELIST - Must match one of these to be included
# =============================================================================

TITLE_WHITELIST = [
    # Software/Development
    "software", "developer", "swe ", "sde ", "full stack", "fullstack",
    "frontend", "front-end", "front end", "backend", "back-end", "back end",
    "mobile developer", "mobile engineer", "ios developer", "android developer",
    "web developer", "web engineer",

    # Data & AI/ML
    "data engineer", "data analyst", "data science", "data scientist",
    "machine learning", "deep learning", "ai intern", "ai co-op",
    "ai ops", "applied ai", "ai transformation",
    "ml intern", "ml co-op", "nlp", "computer vision",

    # Infrastructure/DevOps/Security
    "devops", "cloud engineer", "cloud intern", "security engineer",
    "cybersecurity", "network engineer", "database admin", "dba intern",

    # QA/Testing
    "qa ", "qa intern", "qa co-op", "quality analyst", "quality assurance",
    "test automation", "performance engineer", "sdet",

    # Other technical
    "embedded", "firmware", "game develop", "graphics engineer",
    "blockchain", "build engineer", "simulation",

    # IT roles (not support)
    "technology intern", "it intern", "it co-op", "digital intern",
    "information technology", "technology program", "technology workplace",
    "it - manufacturing", "computer systems",

    # Analyst roles (tech-focused)
    "technical analyst", "information analyst", "business process analyst",
    "measurement and insights",

    # PM/Design
    "product manager", "ux ", "ui ", "ux/ui",
    "business analyst", "systems analyst",
    "bi intern", "business intelligence",
    "fintech", "financial technology",

    # Innovation/Automation
    "innovation", "automation engineer",

    # Electronics (when coding-related)
    "electronics intern",
]


# =============================================================================
# TITLE BLACKLIST - If title contains ANY of these, EXCLUDE (checked first)
# =============================================================================

TITLE_BLACKLIST = [
    # Support roles (hard no)
    "help desk", "helpdesk", "desktop support", "it support",
    "technical support", "support analyst", "support specialist",
    "service desk",

    # Finance (except fintech which is whitelisted)
    "financial analyst", "financial planning", "finance intern",
    "finance internship", "accountant", "accounting",
    "actuary", "actuarial", "auditor", "audit intern", "tax intern", "tax analyst",
    "treasury", "trading system", "quantitative developer", "quant intern",
    "risk analytics", "risk modelling", "portfolio management",
    "investment analyst", "investment management",

    # HR/Admin
    "human resources", "hr intern", "recruiter", "recruiting",
    "admin assistant", "administrative", "receptionist",
    "office coordinator", "talent acquisition", "payroll",

    # Marketing/Sales
    "marketing", "sales intern", "sales representative",
    "business development", "account manager", "account executive",
    "communications intern", "public relations", "pr intern",
    "copywriter", "content writer", "social media", "advertising",

    # Legal
    "legal intern", "law intern", "paralegal", "attorney", "lawyer",
    "compliance analyst", "compliance officer", "law enforcement",
    "regulatory affairs",

    # Healthcare/Science
    "nursing", "nurse", "clinical", "medical intern", "healthcare",
    "pharmacist", "pharmacy intern", "lab technician",
    "medical affairs", "pharmacovigilance", "dietitian",

    # Non-CS Engineering
    "mechanical engineer", "mechanical design", "civil engineer",
    "chemical engineer", "structural engineer", "environmental engineer",
    "electrical engineer", "mechatronics", "package engineer",
    "materials engineer", "bridge engineering", "rail engineering",
    "optical engineering", "manufacturing engineer",
    "manufacturing process", "process engineering",

    # Operations/Logistics
    "supply chain", "logistics", "warehouse",
    "production associate", "field service",

    # Other unwanted
    "phd intern", "research scientist", "applied research",
    "consultant", "release engineer",
    "servicenow", "itv specialist", "robotics engineer",
    "platform engineer", "event coordinator", "project coordinator",
    "commercial coordinator", "relocation",
    "health & safety", "occupational health",
]


# =============================================================================
# LOCATION FILTERING
# =============================================================================

TORONTO_KEYWORDS = [
    "toronto", "gta", "ontario", "on, canada", "on canada", ", on",
    "canada", "canadian",
    "waterloo", "mississauga", "scarborough", "north york",
    "markham", "vaughan", "brampton", "richmond hill",
    "oakville", "hamilton", "ottawa", "montreal", "vancouver", "calgary",
    "burlington", "guelph", "kitchener", "london, on", "windsor",
    "ancaster", "dundas", "concord", "newmarket", "whitby", "kingston"
]

REMOTE_KEYWORDS = ["remote", "work from home", "wfh", "anywhere", "distributed"]

US_ONLY_KEYWORDS = [
    "united states only", "us only", "usa only",
    "must be located in the us", "must be in the us",
    "u.s. only", "us citizens only", "us-based only",
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def is_internship(job: JobData) -> bool:
    """Check if a job is an internship."""
    title = job.title.lower()
    description = (job.description or "").lower()

    has_intern_keyword = any(
        kw in title or kw in description for kw in INTERNSHIP_KEYWORDS
    )
    has_seniority_exclude = any(kw in title for kw in SENIORITY_EXCLUDE)

    return has_intern_keyword and not has_seniority_exclude


def is_blacklisted(job: JobData) -> bool:
    """Check if job title is blacklisted."""
    title = job.title.lower()
    return any(bad in title for bad in TITLE_BLACKLIST)


def is_whitelisted(job: JobData) -> bool:
    """Check if job title is whitelisted."""
    title = job.title.lower()

    # Check for standalone "AI" (word boundary match - not part of another word like "flair")
    if re.search(r'\bai\b', title):
        return True

    return any(good in title for good in TITLE_WHITELIST)


def is_toronto_or_remote(job: JobData) -> bool:
    """Check if a job is located in Toronto/Canada area or is remote."""
    location = job.location.lower() if job.location else ""
    description = (job.description or "").lower()
    title = job.title.lower()

    # Check for US-only restrictions
    for us_keyword in US_ONLY_KEYWORDS:
        if us_keyword in description:
            return False

    # Check if location mentions Toronto/Canada
    for keyword in TORONTO_KEYWORDS:
        if keyword in location:
            return True

    # Check if remote
    for keyword in REMOTE_KEYWORDS:
        if keyword in location or keyword in title:
            return True

    # Also check description for Canada mentions
    if "toronto" in description or "canada" in description:
        return True

    return False


# =============================================================================
# MAIN FILTER FUNCTION
# =============================================================================

def filter_internships(jobs: List[JobData]) -> List[JobData]:
    """
    Filter jobs using whitelist/blacklist system with NO neutral pass-through.

    Logic:
    1. Must be an internship
    2. If blacklisted -> REJECT
    3. Must match whitelist -> ACCEPT (no neutral pass-through)
    4. Must be in Toronto/Canada or remote
    """
    result = []

    # Stats for logging
    total = len(jobs)
    not_internship = 0
    blacklisted = 0
    not_whitelisted = 0
    wrong_location = 0

    for job in jobs:
        # 1. Must be internship
        if not is_internship(job):
            not_internship += 1
            continue

        # 2. Blacklist check - instant reject
        if is_blacklisted(job):
            blacklisted += 1
            continue

        # 3. Must match whitelist (no neutral pass-through)
        if not is_whitelisted(job):
            not_whitelisted += 1
            continue

        # 4. Location check
        if not is_toronto_or_remote(job):
            wrong_location += 1
            continue

        result.append(job)

    # Log summary
    print(f"   Filter: {total} total -> {len(result)} passed")
    print(f"   Rejected: {not_internship} not internship, {blacklisted} blacklisted, {not_whitelisted} not whitelisted, {wrong_location} wrong location")

    return result


# =============================================================================
# DEBUG FUNCTIONS
# =============================================================================

def is_hard_rejected(job: JobData) -> bool:
    """Alias for debug script compatibility."""
    return is_blacklisted(job)


def calculate_tech_score(job: JobData) -> tuple:
    """Simple scoring for debug purposes."""
    breakdown = {
        "hard_excluded": False,
        "role_matches": [],
        "skill_matches": [],
        "negative_matches": [],
        "bonus_matches": [],
    }

    if is_blacklisted(job):
        breakdown["hard_excluded"] = True
        return -100, breakdown

    if is_whitelisted(job):
        return 10, breakdown

    # Not whitelisted - will be rejected
    return 0, breakdown
