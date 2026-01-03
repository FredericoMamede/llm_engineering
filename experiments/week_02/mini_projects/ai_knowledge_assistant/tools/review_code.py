"""
Tool: review_code
Performs quick/deep code review with best-practice checks.
"""

import re
from typing import Any, List

# Best practice patterns to check
QUICK_CHECKS = [
    {
        "name": "bare_except",
        "pattern": r"except\s*:",
        "message": "Bare except clause catches all exceptions including KeyboardInterrupt. Use 'except Exception:' or specific types.",
        "severity": "warning",
    },
    {
        "name": "mutable_default",
        "pattern": r"def\s+\w+\s*\([^)]*=\s*(\[\]|\{\}|\(\))",
        "message": "Mutable default argument. Use None and create inside function.",
        "severity": "warning",
    },
    {
        "name": "global_keyword",
        "pattern": r"\bglobal\s+\w+",
        "message": "Global keyword usage. Consider passing as parameter or using a class.",
        "severity": "info",
    },
    {
        "name": "print_statement",
        "pattern": r"\bprint\s*\(",
        "message": "Print statement found. Consider using logging for production code.",
        "severity": "info",
    },
    {
        "name": "hardcoded_password",
        "pattern": r"(password|secret|api_key|token)\s*=\s*['\"][^'\"]+['\"]",
        "message": "Possible hardcoded secret. Use environment variables.",
        "severity": "error",
    },
    {
        "name": "todo_fixme",
        "pattern": r"#\s*(TODO|FIXME|XXX|HACK)",
        "message": "TODO/FIXME comment found. Address before production.",
        "severity": "info",
    },
]

DEEP_CHECKS = QUICK_CHECKS + [
    {
        "name": "long_function",
        "pattern": None,  # Custom check
        "message": "Function exceeds 50 lines. Consider splitting.",
        "severity": "info",
    },
    {
        "name": "no_docstring",
        "pattern": r"def\s+\w+\s*\([^)]*\)\s*:\s*\n\s*[^\"']",
        "message": "Function without docstring. Add documentation.",
        "severity": "info",
    },
    {
        "name": "star_import",
        "pattern": r"from\s+\w+\s+import\s+\*",
        "message": "Star import pollutes namespace. Import specific names.",
        "severity": "warning",
    },
    {
        "name": "nested_loops",
        "pattern": r"for\s+.+:\s*\n\s+for\s+.+:",
        "message": "Nested loops detected. Consider list comprehension or helper function.",
        "severity": "info",
    },
    {
        "name": "magic_number",
        "pattern": r"(?<!['\"\w])\b(?!0\b|1\b|2\b)[0-9]{2,}\b(?!['\"])",
        "message": "Magic number. Consider using named constant.",
        "severity": "info",
    },
]


def _run_checks(code: str, checks: List[dict]) -> List[dict]:
    """Run pattern checks on code and return findings."""
    findings = []
    lines = code.split("\n")
    
    for check in checks:
        if check["pattern"] is None:
            continue
        
        for i, line in enumerate(lines, 1):
            if re.search(check["pattern"], line, re.IGNORECASE):
                findings.append({
                    "line": i,
                    "name": check["name"],
                    "message": check["message"],
                    "severity": check["severity"],
                    "code": line.strip()[:60],
                })
    
    return findings


def _check_function_length(code: str) -> List[dict]:
    """Check for functions exceeding 50 lines."""
    findings = []
    lines = code.split("\n")
    
    func_start = None
    func_name = None
    indent_level = None
    
    for i, line in enumerate(lines):
        # Detect function definition
        match = re.match(r"^(\s*)def\s+(\w+)", line)
        if match:
            # Close previous function if any
            if func_start is not None and i - func_start > 50:
                findings.append({
                    "line": func_start + 1,
                    "name": "long_function",
                    "message": f"Function '{func_name}' is {i - func_start} lines. Consider splitting.",
                    "severity": "info",
                    "code": f"def {func_name}(...)",
                })
            func_start = i
            func_name = match.group(2)
            indent_level = len(match.group(1))
    
    # Check last function
    if func_start is not None and len(lines) - func_start > 50:
        findings.append({
            "line": func_start + 1,
            "name": "long_function",
            "message": f"Function '{func_name}' is {len(lines) - func_start} lines. Consider splitting.",
            "severity": "info",
            "code": f"def {func_name}(...)",
        })
    
    return findings


def review_code(code: str, depth: str = "quick") -> str:
    """
    Review code for common issues and best practices.
    
    Args:
        code: The code to review
        depth: "quick" for fast checks, "deep" for thorough analysis
    
    Returns:
        Formatted review with findings and recommendations
    """
    if not code or not code.strip():
        return "No code provided."

    checks = QUICK_CHECKS if depth == "quick" else DEEP_CHECKS
    findings = _run_checks(code, checks)
    
    if depth == "deep":
        findings.extend(_check_function_length(code))
    
    # Sort by severity, then line number
    severity_order = {"error": 0, "warning": 1, "info": 2}
    findings.sort(key=lambda f: (severity_order.get(f["severity"], 3), f["line"]))

    if not findings:
        return f"**Code Review ({depth.upper()}):** No issues found. Code looks clean."

    # Build report
    parts = [f"**Code Review ({depth.upper()}):** Found {len(findings)} issue(s).\n"]
    
    error_count = sum(1 for f in findings if f["severity"] == "error")
    warn_count = sum(1 for f in findings if f["severity"] == "warning")
    info_count = sum(1 for f in findings if f["severity"] == "info")
    
    parts.append(f"Summary: {error_count} errors, {warn_count} warnings, {info_count} info\n")
    
    for f in findings:
        icon = {"error": "[ERROR]", "warning": "[WARN]", "info": "[INFO]"}.get(f["severity"], "")
        parts.append(f"\n{icon} Line {f['line']}: {f['message']}")
        parts.append(f"   Code: `{f['code']}`")

    return "\n".join(parts)


# Tool metadata for registry
TOOL_NAME = "review_code"
TOOL_IMPL = review_code
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "review_code",
        "description": "Review code for common issues and best practices. Returns findings with severity and recommendations.",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The code to review",
                },
                "depth": {
                    "type": "string",
                    "enum": ["quick", "deep"],
                    "description": "Review depth: 'quick' for fast checks, 'deep' for thorough analysis",
                },
            },
            "required": ["code"],
        },
    },
}
