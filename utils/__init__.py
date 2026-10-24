"""
Utils Module: Core Infrastructure for the AI SEO Audit SaaS
Includes Database management, Scraping fallbacks, PDF generation, and Billing.
"""

# 1. Database & User Management (from db.py)
from .db import (
    get_db_connection,
    init_db,
    get_user_by_email,
    create_user,
    deduct_credit,
    add_credits_to_user
)

# 2. Web Scraping Engine (from scraper.py and js_scraper.py)
try:
    from .scraper import scrape_url
except ImportError:
    scrape_url = None

try:
    from .js_scraper import scrape_with_js_rendering
except ImportError:
    scrape_with_js_rendering = None

# 3. Monetization & Billing (from billing.py)
try:
    from .billing import create_checkout_session
except ImportError:
    create_checkout_session = None

# 4. Authentication UI (from auth_manager.py)
try:
    from .auth_manager import login_ui
except ImportError:
    login_ui = None

# 5. Reporting (from pdf_generator.py)
try:
    from .pdf_generator import markdown_to_pdf
except ImportError:
    markdown_to_pdf = None

# Exporting for easy access
__all__ = [
    # DB
    "get_db_connection",
    "init_db",
    "get_user_by_email",
    "create_user",
    "deduct_credit",
    "add_credits_to_user",
    
    # Scraping
    "scrape_url",
    "scrape_with_js_rendering",
    
    # SaaS Essentials
    "create_checkout_session",
    "login_ui",
    
    # Exports
    "markdown_to_pdf"
]