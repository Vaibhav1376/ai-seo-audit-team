"""
Workflows Package
Main workflow orchestration functions
"""

from .single_page import run_single_page_audit
from .batch_audit import run_batch_audit_with_features
from .full_site import run_full_site_audit

# Try to import competitor analysis (may not exist yet)
try:
    from .competitor_analysis import run_competitor_analysis
except ImportError:
    run_competitor_analysis = None

# Create alias for backward compatibility
run_batch_audit = run_batch_audit_with_features

__all__ = [
    'run_single_page_audit',
    'run_batch_audit',
    'run_batch_audit_with_features',
    'run_full_site_audit',
    'run_competitor_analysis'
]
