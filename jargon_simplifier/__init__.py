"""jargon-simplifier: turn stiff prose into plain English.

Built by Asdale Dynamics, LLC. MIT licensed.
"""

__version__ = "1.0.0"

from .engine import Edit, RewriteResult, rewrite_offline  # noqa: F401
from .glossary import GLOSSARY  # noqa: F401
