"""dsh-skill-lint — checks a SKILL.md against the DSH Skill Specification."""
from .linter import Finding, Report, lint_path, lint_skill, discover

__version__ = "0.1.0"
SPEC_VERSION = "0.1"
__all__ = ["Finding", "Report", "lint_path", "lint_skill", "discover", "__version__", "SPEC_VERSION"]
